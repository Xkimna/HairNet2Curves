import tensorflow.compat.v1 as tf
tf.get_logger().setLevel('ERROR')
# import keras

from tools.basic.m_config import Config
from tools.tf.util.m_utility import get_config
from tools.tf.util.m_decorator import template_wrapper

from tensorflow.python.ops.init_ops import variance_scaling_initializer


def he_normal(seed=None):  # work with relu
    return variance_scaling_initializer(scale=2., mode="fan_in", distribution="normal", seed=seed)


def lecun_normal(seed=None):  # work with selu
    return variance_scaling_initializer(scale=1., mode="fan_in", distribution="normal", seed=seed)


def dense(kernel_num, name=""):
    def f(x):
        x = tf.layers.dense(
            x, kernel_num,
            activation=None,
            use_bias=True,
            kernel_initializer=lecun_normal(),
            kernel_regularizer=tf.keras.regularizers.l1_l2(l1=1e-4, l2=1e-4),
            bias_regularizer=None,
            activity_regularizer=None,
            kernel_constraint=None,
            bias_constraint=None,
            trainable=True,
            name=name,
            reuse=None)
        return x

    return f


def conv(kernel_num, kernel_size=(3, 3), strides=(1, 1), name=None):
    def f(x):
        x = tf.layers.conv2d(x,
                             kernel_num,
                             kernel_size=kernel_size,
                             strides=strides,
                             use_bias=True,
                             padding="same",
                             kernel_initializer=lecun_normal(),
                             kernel_regularizer=tf.keras.regularizers.l1_l2(l1 = 1e-4, l2 = 1e-4), name=name)
        return x

    return f


def deconv(kernel_num, name=None):
    def f(x):
        n, h, w, c = x.get_shape()
        x = tf.image.resize_images(x, (h * 2, w * 2), method=tf.image.ResizeMethod.BILINEAR)
        x = tf.pad(x, paddings=tf.constant([[0, 0], [1, 1], [1, 1], [0, 0]]), mode="SYMMETRIC")
        x = tf.layers.conv2d(x,
                             kernel_num,
                             kernel_size=(3, 3),
                             strides=(1, 1),
                             use_bias=True,
                             padding="valid",
                             kernel_initializer=lecun_normal(),
                             kernel_regularizer=tf.keras.regularizers.l1_l2(l1 = 1e-4, l2 = 1e-4), name=name)
        return x

    return f


def build_model(cfg, training=False):
    @template_wrapper(name="model")
    def f(x):
        # print(x.get_shape())
        out = x
        with tf.variable_scope("encoder"):
            # x 256x256
            k = 16
            with tf.variable_scope("conv_1"):
                out = conv(k, (8, 8), (2, 2))(out)  # 128x128
                out = tf.nn.relu(out)
                k *= 2

            with tf.variable_scope("conv_2"):
                out = conv(k, (8, 8), (2, 2))(out)  # 64x64
                out = tf.nn.relu(out)
                k *= 2

            with tf.variable_scope("conv_3"):
                out = conv(k, (6, 6), (2, 2))(out)  # 32x32
                out = tf.nn.relu(out)
                k *= 2

            with tf.variable_scope("conv_4"):
                out = conv(k, (4, 4), (2, 2))(out)  # 16x16
                out = tf.nn.relu(out)
                k *= 2

            with tf.variable_scope("conv_5"):
                out = conv(k, (4, 4), (2, 2))(out)  # 8x8
                out = tf.nn.relu(out)

        with tf.variable_scope("embedding"):
            # x 8x8
            n, h, w, c = out.get_shape()
            out = tf.layers.max_pooling2d(out, (h, w), (1, 1), name="max_pool")
            out = tf.nn.tanh(out, name="embedding")

            out = tf.reshape(out, (n, c))

            out = dense(1024)(out)
            out = tf.nn.relu(out)
            out = dense(4096)(out)
            out = tf.nn.relu(out)

            out = tf.reshape(out, (n, 4, 4, 256))

        with tf.variable_scope("decoder"):
            k = 128
            with tf.variable_scope("deconv_1"):
                out = deconv(k)(out)
                out = tf.nn.relu(out)
            with tf.variable_scope("deconv_2"):
                out = deconv(k)(out)
                out = tf.nn.relu(out)
            with tf.variable_scope("deconv_3"):
                out = deconv(k)(out)
                out = tf.nn.relu(out)

        # x 32x32
        with tf.variable_scope("analyzer"):
            k = 384
            with tf.variable_scope("position"):
                pos = conv(k, (1, 1), (1, 1), name="conv_1")(out)
                pos = tf.nn.relu(pos)
                pos = conv(k, (1, 1), (1, 1), name="conv_2")(pos)
                pos = tf.nn.tanh(pos)
                pos = conv(300, (1, 1), (1, 1), name="conv_3")(pos)

            k = 128
            with tf.variable_scope("curvature"):
                crv = conv(k, (1, 1), (1, 1), name="conv_1")(out)
                crv = tf.nn.relu(crv)
                crv = conv(k, (1, 1), (1, 1), name="conv_2")(crv)
                crv = tf.nn.tanh(crv)
                crv = conv(100, (1, 1), (1, 1), name="conv_3")(crv)

        return pos, crv

    return f


def test_model():
    import numpy as np
    cfg = Config()

    x = tf.placeholder(dtype=tf.float32, shape=[4, 256, 256, 3], name="x")
    model = build_model(cfg, False)
    y = model(x)

    saver = tf.train.Saver(max_to_keep=1)
    with tf.Session(config=get_config()) as sess:
        sess.run(tf.global_variables_initializer())
        _x = np.random.rand(4, 256, 256, 3)
        _y = sess.run(y, feed_dict={x: _x})
        print(_y[0].shape)
        summary = tf.Summary()
        summary.value.add(tag="a", simple_value=0)

        summary_writer = tf.summary.FileWriterCache.get("./model")
        summary_writer.add_summary(summary, 0)
        summary_writer.flush()

        saver.save(sess, "./model/model", global_step=0)


if __name__ == '__main__':
    test_model()
