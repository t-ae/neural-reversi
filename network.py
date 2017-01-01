
from keras.models import Sequential, Model
from keras.layers import Dense, InputLayer, Reshape, Flatten, merge, Input
from keras.layers.convolutional import Conv2D, ZeroPadding1D
from keras.layers.local import LocallyConnected2D
from keras.layers.advanced_activations import ELU
from keras.optimizers import Adam

def create_model6():

    action_input = Input(shape=[6, 6])
    color_input = Input(shape=[1])

    model_v = Sequential([
        InputLayer([6, 6]),
        Reshape([6, 6, 1]),
        Conv2D(64, 6, 1), # 1x6
        ELU(),
        Conv2D(64, 1, 1),
        ELU(),
        Flatten()
    ])

    model_h = Sequential([
        InputLayer([6, 6]),
        Reshape([6, 6, 1]),
        Conv2D(64, 1, 6), # 6x1
        ELU(),
        Conv2D(64, 1, 1),
        ELU(),
        Flatten()
    ])

    model_dr = Sequential([
        InputLayer([6, 6]),
        Reshape([6*6, 1]),
        ZeroPadding1D(3),
        Reshape([6, 7, 1]),
        LocallyConnected2D(64, 6, 1),
        ELU(),
        LocallyConnected2D(64, 1, 1),
        ELU(),
        Flatten()
    ])

    model_dl = Sequential([
        InputLayer([6, 6]),
        Reshape([6*6, 1]),
        ZeroPadding1D(2),
        Reshape([8, 5, 1]),
        LocallyConnected2D(64, 8, 1),
        ELU(),
        LocallyConnected2D(64, 1, 1),
        ELU(),
        Flatten()
    ])

    color_model = Sequential([
        InputLayer([1]),
        Dense(256),
        ELU(),
        Dense(1024),
        ELU()
    ])

    merge_layer = merge([
        color_model(color_input),
        model_v(action_input),
        model_h(action_input),
        model_dl(action_input),
        model_dr(action_input),
    ], mode="concat", concat_axis=-1) 

    x = Dense(2048)(merge_layer)
    x = ELU()(x)
    x = Dense(512)(x)
    x = ELU()(x)
    x = Dense(128)(x)
    x = ELU()(x)
    output = Dense(1, activation="tanh")(x)

    model = Model(input=[color_input, action_input], output=[output])

    adam = Adam(lr=1e-4)
    model.compile(optimizer=adam, loss="mse")

    return model


def create_model8():
    action_input = Input(shape=[8, 8])
    color_input = Input(shape=[1])

    model_c = Sequential([
        InputLayer([8, 8]),
        Reshape([8, 8, 1]),
        Conv2D(128, 8, 1, name="model_c_conv1"), # 1x8
        ELU(),
        Conv2D(128, 1, 1, name="model_c_conv2"), # 1x8
        ELU(),
        Flatten()
    ], name="model_c")

    model_r = Sequential([
        InputLayer([8, 8]),
        Reshape([8, 8, 1]),
        Conv2D(128, 1, 8, name="model_r_conv1"), # 8x1
        ELU(),
        Conv2D(128, 1, 1, name="model_r_conv2"), # 8x1
        ELU(),
        Flatten()
    ], name="model_r")

    model_dr = Sequential([
        InputLayer([8, 8]),
        Reshape([8*8, 1]),
        ZeroPadding1D(4),
        Reshape([8, 9, 1]),
        LocallyConnected2D(96, 8, 1, name="model_dr_lc1"), # 1x9
        ELU(),
        LocallyConnected2D(64, 1, 1, name="model_dr_lc2"), # 1x9
        ELU(),
        Flatten()
    ], name="model_dr")

    model_dl = Sequential([
        InputLayer([8, 8]),
        Reshape([8*8, 1]),
        ZeroPadding1D(3),
        Reshape([10, 7, 1]),
        LocallyConnected2D(96, 10, 1, name="model_dl_lc1"), # 1x7
        ELU(),
        LocallyConnected2D(64, 1, 1, name="model_dl_lc2"), # 1x7
        ELU(),
        Flatten()
    ], name="model_dl")

    merge_layer = merge([
        color_input,
        model_c(action_input),
        model_r(action_input),
        model_dl(action_input),
        model_dr(action_input),
    ], mode="concat", concat_axis=-1, name="merge_layer") 

    x = Dense(2048, name="fc_1")(merge_layer)
    x = ELU()(x)
    x = Dense(512, name="fc_2")(x)
    x = ELU()(x)
    output = Dense(1, activation="tanh", name="fc_3")(x)

    model = Model(input=[color_input, action_input], output=[output])

    adam = Adam(lr=1e-5)
    model.compile(optimizer=adam, loss="mse")

    return model
