import numpy as np
from tensorflow.keras.layers import Dense, Conv1D, GlobalMaxPooling1D, Embedding, Dropout, MaxPooling1D
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.backend import *


def train(code):
    x_data = np.load('./x_train.npy')
    y_data = np.load('./y_train_{}.npy'.format(code))
    print(x_data.shape, y_data.shape)
    assert len(x_data) == len(y_data)

    # p = np.random.permutation(len(x_data))
    # x_data = x_data[p]
    # y_data = y_data[p]

    train_percent = 0.8
    train_size = int(len(x_data) * train_percent)
    x_train = x_data[:train_size]
    x_test = x_data[train_size:]
    y_train = y_data[:train_size]
    y_test = y_data[train_size:]

    model = Sequential()
    model.add(Embedding(50000, 128, input_length=500))
    model.add(Dropout(0.2))
    model.add(Conv1D(256, 5, strides=1, padding='valid', activation='relu'))
    model.add(GlobalMaxPooling1D())
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(3, activation='sigmoid'))
    model.summary()
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['acc'])

    es = EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=8)
    mc = ModelCheckpoint('best_model.h5', monitor='val_acc', mode='max', verbose=1, save_best_only=True)

    history = model.fit(x_train, y_train, epochs=20, batch_size=64, validation_split=0.2, callbacks=[es, mc])

    return x_train, y_train, x_test, y_test, history


train('017670')
