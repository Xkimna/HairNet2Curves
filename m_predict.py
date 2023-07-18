import os
import sys
import imageio.v2 as imageio
import argparse
import numpy as np
import cv2
import tensorflow.compat.v1 as tf

from tools.basic.m_config import Config
from tools.tf.util.m_utility import get_config

from config.m_cfg import load_cfg
from model.m_model import build_model
from tools.basic.m_vis import vis_hair, saveObjHairFile


def load_info(cur_dir):
    pos_mean_path = os.path.join(cur_dir, r"pos_mean.txt")
    pos_std_path = os.path.join(cur_dir, r"pos_std.txt")

    crv_mean_path = os.path.join(cur_dir, r"crv_mean.txt")
    crv_std_path = os.path.join(cur_dir, r"crv_std.txt")

    strands_mask_path = os.path.join(cur_dir, r"strands_mask.txt")
    strands_root_path = os.path.join(cur_dir, r"strands_root.txt")

    strands_mask = np.loadtxt(strands_mask_path, dtype=np.uint8)
    strands_root = np.loadtxt(strands_root_path, dtype=np.float32)

    pos_mean = np.loadtxt(pos_mean_path, dtype=np.float32)
    pos_std = np.loadtxt(pos_std_path, dtype=np.float32)

    crv_mean = np.loadtxt(crv_mean_path, dtype=np.float32)
    crv_std = np.loadtxt(crv_std_path, dtype=np.float32)

    strands_mask.shape = (32, 32, 1)
    strands_root.shape = (32, 32, 1, 3)

    pos_mean.shape = (1, 1, 1, 3)
    pos_std.shape = (1, 1, 1, 3)

    crv_mean.shape = (1, 1, 1)
    crv_std.shape = (1, 1, 1)

    return Config(locals())


def get_graph(graph_cfg):
    tf.compat.v1.disable_eager_execution()
    inp_img_feat = tf.placeholder(dtype=tf.float32, shape=[1, 256, 256, 3], name="inp_img_feat")
    model = build_model(graph_cfg, False)
    out_pos_feat, out_crv_feat = model(inp_img_feat)
    return Config(locals())


def main(workspace, image_dir, ckpt_dir, save_dir, save_name, gaussian_flag):
    dataspace = os.path.join(workspace, "data")

    ckpt_index_file = [f for f in os.listdir(ckpt_dir) if f.endswith('.index')][0]
    ckpt_index_file_without_extension = os.path.splitext(ckpt_index_file)[0]
    ckpt_dir = os.path.join(ckpt_dir, ckpt_index_file_without_extension)

    cfg = Config(load_cfg(workspace))

    graph = get_graph(cfg.graph)
    saver = tf.train.Saver(max_to_keep=1)

    info = load_info(dataspace)

    with tf.Session(config=get_config()) as sess:
        sess.run(tf.global_variables_initializer())
        print("load ckpt:", ckpt_dir)
        saver.restore(sess, ckpt_dir)

        inp_img = imageio.imread(image_dir)
        # inp_img = cv2.resize(inp_img, (256, 256))
        inp_img = inp_img[..., ::-1]
        inp_img_feat = (inp_img - 127.5) / 255.

        out_pos_feat, out_crv_feat = sess.run([graph.out_pos_feat,
                                               graph.out_crv_feat],
                                              feed_dict={graph.inp_img_feat:
                                                             np.asarray([inp_img_feat], dtype=np.float32)})
        out_pos_feat.shape = (1, 1024, 100, 3)
        out_crv_feat.shape = (1, 1024, 100, 1)

        out_pos = out_pos_feat[0]
        out_crv = out_crv_feat[0]
        out_pos *= np.tile(info.strands_mask.reshape(1024, 1, 1), [1, 100, 1])
        out_pos += np.tile(info.strands_root.reshape(1024, 1, 3), [1, 100, 1])
        out_crv *= np.tile(info.strands_mask.reshape(1024, 1, 1), [1, 100, 1])
        out_crv.shape = (1024, 100)
        out_pos.shape = (1024, 100, 3)
        out_crv.shape = (1024, 100, 1)
        hair = np.concatenate([out_pos,out_crv],axis=2)
        if np.all(hair == 0):
            print('*' * 30, "error:(", '*' * 30)
            sys.exit(1)
        else:
            if save_dir == "":
                vis_hair(os.path.join(workspace, "temp\\output.png"), hair, gaussian_flag)
                saveObjHairFile(os.path.join(workspace, "temp\\output.obj"), hair, gaussian_flag)
                print("save output: ", os.path.join(workspace, 'temp'))
            else:
                vis_hair(os.path.join(save_dir, save_name + "_output.png"), hair, gaussian_flag)
                saveObjHairFile(os.path.join(save_dir, save_name + "_output.obj"), hair, gaussian_flag)
                print("save output: ", save_dir)
            print('*' * 30, "success", '*' * 30)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp_dir", type=str, default="")
    parser.add_argument("--tgt_dir", type=str, default="")
    parser.add_argument("--ckpt_dir", type=str, default="")
    parser.add_argument("--save_dir", type=str, default="")
    parser.add_argument("--save_name", type=str, default="")
    parser.add_argument("--gaussian_flag", type=str)

    flags, _ = parser.parse_known_args()

    print('*' * 22, "argparse", '*' * 30)
    print('1.workspace:', flags.exp_dir,'\n'+
          '2.target image path:', flags.tgt_dir,'\n'+
          '3.pre-trained model path:', flags.ckpt_dir,'\n'+
          '4.output saving path:', flags.save_dir,'\n'+
          '5.Whether Gaussian:', eval(flags.gaussian_flag))
    print('*' * 30, "process", '*' * 30)

    main(flags.exp_dir, flags.tgt_dir, flags.ckpt_dir, flags.save_dir, flags.save_name, eval(flags.gaussian_flag))
