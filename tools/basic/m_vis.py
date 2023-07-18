import numpy as np
import matplotlib.pyplot as plt
import cv2

def gaussian(pos):
    pos = pos.reshape(32, 32, 100, 3)

    for i in range(pos.shape[0]):
        for j in range(pos.shape[1]):
            strand_root_pos = np.array([pos[i, j, 0, 0], pos[i, j, 0, 1], pos[i, j, 0, 2]])
            strand_tail_pos = np.array([pos[i, j, 99, 0], pos[i, j, 99, 1], pos[i, j, 99, 2]])
            gaussian_dis = np.linalg.norm(strand_tail_pos - strand_root_pos)
            gaussian_weight = np.clip(int(20 * np.cos(3 * gaussian_dis)), a_min=2, a_max=None)  # 试验得到的
            gaussian = cv2.getGaussianKernel(gaussian_weight, 3)
            pos[i, j, :, :] = cv2.filter2D(pos[i, j, :, :], -1, gaussian)
    pos = pos.reshape(1024, 100, 3)
    pos = pos[np.newaxis, :]

    return pos

def vis_hair(save_path, hair, gaussian_flag):
    fig = plt.figure()
    fig.set_tight_layout(False)
    ax = plt.subplot(projection="3d")
    if gaussian_flag:
        hair[..., :3] = gaussian(hair[..., :3])
    show_hair(ax, hair)

    if(save_path != ""):
        plt.savefig(save_path, bbox_inches='tight')
    # plt.show()


def show_hair(axis, hair):
    """

    :param axis:
    :param hair: (n, m, 3)
    :return:
    """

    hair = hair.copy()
    n, m, k = hair.shape
    hair.shape = (-1, k)
    # for item in hair[:]:
    #     if np.sum(item) != 0:
    #         axis.scatter3D(-item[0],item[2],item[1], s=0.2, c="black")

    axis.scatter3D(hair[:, 2], -hair[:, 0], hair[:, 1], s=0.001, c="black")
    x_min, x_max = np.min(hair[:, 0]), np.max(hair[:, 0])
    y_min, y_max = np.min(hair[:, 1]), np.max(hair[:, 1])
    z_min, z_max = np.min(hair[:, 2]), np.max(hair[:, 2])

    r = 0.001
    axis.set_xlim3d([x_min - r, x_max + r])
    axis.set_ylim3d([z_min - r, z_max + r])
    axis.set_zlim3d([y_min - r, y_max + r])

    RADIUS = 0.3  # space around the head
    xroot, yroot, zroot = 0, 0, 1.65
    axis.set_xlim3d([-RADIUS + xroot, RADIUS + xroot])
    axis.set_ylim3d([-RADIUS + yroot, RADIUS + yroot])
    axis.set_zlim3d([-RADIUS + zroot, RADIUS + zroot])

    # Get rid of the ticks and tick labels
    axis.set_xticks([])
    axis.set_yticks([])
    axis.set_zticks([])

    axis.get_xaxis().set_ticklabels([])
    axis.get_yaxis().set_ticklabels([])
    axis.set_zticklabels([])
    axis.set_aspect("auto")

def saveObjHairFile(fileName, strands, gaussian_flag):
    """
    fileName: string
    strands: [32 * 32, 300]
    """
    # strands = strands.reshape(-1, 300)
    n, m, k = strands.shape
    strands = strands[...,:3]
    if gaussian_flag:
        strands = gaussian(strands)
    strands = strands.reshape(n, -1)

    vertices = []
    # hairWidth = 0.0 #0.02
    # scaledY = [0, hairWidth, 0]

    def cross(a, b):
        ax = a[0]
        ay = a[1]
        az = a[2]
        bx = b[0]
        by = b[1]
        bz = b[2]
        return [ay * bz - az * by, az * bx - ax * bz, ax * by - bx * ay]

    def add(a, b):
        return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]

    for i in range(32 * 32):
        vertices.append([])
        for j in range(0, 300 - 3, 6):
            # transform from graphics coordinate to math coordinate
            z, y, x = [np.array([strands[i, j + axis], strands[i, j + axis + 3]]) for axis in range(3)]
            vertex0 = [x[0], y[0] - 1.7, z[0]]
            vertex1 = [x[1], y[1] - 1.7, z[1]] # 原数据集中发型原点在（0，1.7m，0）
            # vertex2 = [n + hairWidth for n in vertex0]
            # vertex3 = [n + hairWidth for n in vertex1]
            # while hairWidth != 0:
            #     vertex2 = add(cross(vertex0, scaledY), vertex0)
            #     vertex3 = add(cross(vertex1, scaledY), vertex1)
            #     vertices.extend([vertex0, vertex1, vertex2, vertex3])

            vertices[i].extend([vertex0, vertex1])

    file = open(fileName, 'w')

    for i in range(32 * 32):
        for vertex in vertices[i]:
            if vertex != [0.0, -1.7, 0.0]:
                file.write("v {0} {1} {2}\n".format(vertex[0], vertex[1], vertex[2]))

    # while hairWidth != 0:
    #     for i in range(1, len(vertices) + 1, 4):
    #         file.write("f {0} {1} {2}\n".format(i, i + 1, i + 2))
    #         file.write("f {0} {1} {2}\n".format(i + 1, i + 2, i + 3))

    sum = 0
    for i in range(32 * 32):
        if vertices[i][0] != [0.0, -1.7, 0.0]:
            for j in range(sum + 1, sum + len(vertices[i]), 1):
                file.write("l {0} {1}\n".format(j, j + 1))
            sum += len(vertices[i])

    file.close()