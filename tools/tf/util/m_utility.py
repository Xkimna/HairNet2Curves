import tensorflow.compat.v1 as tf


def get_config():
    # config
    config = tf.ConfigProto()
    config.allow_soft_placement = True
    # config.log_device_placement = True
    config.gpu_options.allow_growth = True
    config.gpu_options.force_gpu_compatible = True
    # config.gpu_options.visible_device_list = "0"
    config.intra_op_parallelism_threads = 10
    config.inter_op_parallelism_threads = 10
    return config
