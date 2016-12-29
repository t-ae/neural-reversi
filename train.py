#!/usr/bin/env python

import os, glob, math
import numpy as np
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
from keras.models import load_model
from keras.callbacks import EarlyStopping
import reversi
import network
import train_data_creator
import evaluate

GAMMA = 0.97

MODEL_PATH = os.path.join(os.path.dirname(__file__), "./output/model.h5")
BEST_PATH = os.path.join(os.path.dirname(__file__), "./output/best_model.h5")
RECORD_PATH = os.path.join(os.path.dirname(__file__), "./record/*.npz")
TEST_RECORD_PATH = os.path.join(os.path.dirname(__file__), "./test_record.npz")

# restrict gpu memory usage
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.8
set_session(tf.Session(config=config))

if os.path.exists(MODEL_PATH):
    fine_tune = True
    model = load_model(MODEL_PATH)
else:
    fine_tune = False
    if reversi.BOARD_SIZE == 8:
        model = network.create_model8()
    elif reversi.BOARD_SIZE == 6:
        model = network.create_model6()
    else:
        print("invalid reversi.BORD_SIZE:", reversi.BOARD_SIZE)
        exit(-1)

model.summary()


creator = train_data_creator.TrainDataCreator(model,
                                              GAMMA)

# test
test_color, test_action = creator.load_test_record(TEST_RECORD_PATH)
max_win_ratio = -1.0

for i in range(1, 99999999):
    print("epoch:", i)
    records = glob.glob(RECORD_PATH)
    print("{0} records".format(len(records)))
    np.random.shuffle(records)

    record_index = 0
    for j in range(1, 9999999999):
        print("{0}-{1}: record_index:{2}/{3}".format(i, j, record_index, len(records)))
        end_index, data = creator.create_train_data(records, record_index)
        if end_index > len(records):
            print("index exceeds records len")
            break
        if data is None:
            print("data is none")
            break
        X_color, X_action, y_target = data
        print("train: {0} samples, {1} files".format(len(X_color), end_index-record_index))
        for c, r in zip(X_color[::4][0:60], y_target.reshape([-1, 4])):
            print("{0}: {1}".format("B" if c==reversi.BLACK else "W", r))
        history = model.fit([X_color, X_action], y_target,
                            verbose=1,
                            nb_epoch=24,
                            validation_split=0.2,
                            callbacks=[
                                EarlyStopping(patience=1)
                            ])

        # show test
        print("test_record")
        Qs = model.predict([test_color, test_action])
        for k, crow in enumerate(zip(test_color[::4], Qs.reshape([-1, 4]))):
            c, row = crow
            print("{0:2d}: {1}: {2}".format(k, "B" if c==reversi.BLACK else "W", row))

        model.save(MODEL_PATH)
        if j%100 == 0:
            ratio = evaluate.evaluate_model(model, 100)
            print("win ratio:", ratio)
            if max_win_ratio <= ratio:
                print("max update:", ratio, ">=", max_win_ratio)
                max_win_ratio = ratio
                model.save(BEST_PATH)
            else:
                print(ratio, "<", max_win_ratio)
        print("")

        record_index = end_index
