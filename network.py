
from keras.models import Sequential, Model
from keras.layers import Dense, InputLayer, Reshape, Flatten, merge, Input
from keras.layers.convolutional import Conv2D, ZeroPadding1D
from keras.layers.local import LocallyConnected2D
from keras.layers.normalization import BatchNormalization
from keras.layers.advanced_activations import ELU
from keras.optimizers import Adam

def create_model6():

    board_input = Input(shape=[6, 6])
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
        model_v(board_input),
        model_h(board_input),
        model_dl(board_input),
        model_dr(board_input),
        color_model(color_input),
        model_v(action_input),
        model_h(action_input),
        model_dl(action_input),
        model_dr(action_input),
    ], mode="concat", concat_axis=-1) 

    x = Dense(2048)(merge_layer)
    x = BatchNormalization()(x)
    x = ELU()(x)
    x = Dense(512)(x)
    x = BatchNormalization()(x)
    x = ELU()(x)
    x = Dense(128)(x)
    x = BatchNormalization()(x)
    x = ELU()(x)
    output = Dense(1, activation="tanh")(x)

    model = Model(input=[board_input, color_input, action_input], output=[output])

    adam = Adam(lr=1e-4)
    model.compile(optimizer=adam, loss="mse")

    return model


def create_model8():
    board_input = Input(shape=[8, 8])
    action_input = Input(shape=[8, 8])
    color_input = Input(shape=[1])

    model_v = Sequential([
        InputLayer([8, 8]),
        Reshape([8, 8, 1]),
        Conv2D(64, 8, 1), # 1x8
        ELU(),
        Conv2D(64, 1, 1),
        ELU(),
        Flatten()
    ])

    model_h = Sequential([
        InputLayer([8, 8]),
        Reshape([8, 8, 1]),
        Conv2D(64, 1, 8), # 8x1
        ELU(),
        Conv2D(64, 1, 1),
        ELU(),
        Flatten()
    ])

    model_dr = Sequential([
        InputLayer([8, 8]),
        Reshape([8*8, 1]),
        ZeroPadding1D(4),
        Reshape([8, 9, 1]),
        LocallyConnected2D(64, 8, 1),
        ELU(),
        LocallyConnected2D(64, 1, 1),
        ELU(),
        Flatten()
    ])

    model_dl = Sequential([
        InputLayer([8, 8]),
        Reshape([8*8, 1]),
        ZeroPadding1D(2),
        Reshape([10, 7, 1]),
        LocallyConnected2D(64, 10, 1),
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
        model_v(board_input),
        model_h(board_input),
        model_dl(board_input),
        model_dr(board_input),
        color_model(color_input),
        model_v(action_input),
        model_h(action_input),
        model_dl(action_input),
        model_dr(action_input),
    ], mode="concat", concat_axis=-1) 

    x = Dense(2048)(merge_layer)
    x = BatchNormalization()(x)
    x = ELU()(x)
    x = Dense(512)(x)
    x = BatchNormalization()(x)
    x = ELU()(x)
    x = Dense(128)(x)
    x = BatchNormalization()(x)
    x = ELU()(x)
    output = Dense(1, activation="tanh")(x)

    model = Model(input=[board_input, color_input, action_input], output=[output])

    adam = Adam(lr=1e-4)
    model.compile(optimizer=adam, loss="mse")

    return model
