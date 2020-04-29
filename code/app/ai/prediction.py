import os
import sys
import warnings
import pickle
import numpy as np
import time
import pandas as pd

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)
    warnings.filterwarnings('ignore', category=RuntimeWarning)
    import tensorflow as tf
    from sklearn import preprocessing
    # import matplotlib.pyplot as plt

os.chdir('../')
sys.path.append(os.getcwd())
import data.data

tf.compat.v1.enable_eager_execution()


def load_data(symbol):
    df = pd.DataFrame()
    if os.path.exists(f'data/stock_data/{symbol}') and not os.path.isfile(f'data/stock_data/{symbol}'):
        if os.listdir(f'data/stock_data/{symbol}'):
            _df = pd.read_pickle(f'data/stock_data/{symbol}/{symbol}.pkl')
            df = pd.DataFrame(_df)
            df.set_index('date', inplace=True)
            df.drop(columns=['volume', 'adjClose', 'adjHigh', 'adjLow', 'adjOpen', 'adjVolume', 'divCash', 'splitFactor'], inplace=True)

    return df


def make_model(symbol, x, y, val_x, val_y):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(32, activation='linear'))
    model.add(tf.keras.layers.Dense(64, activation='linear'))
    model.add(tf.keras.layers.Dense(4, activation='linear'))
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.8, patience=0, min_lr=0.00001, mode='min', verbose=0)
    check = tf.keras.callbacks.ModelCheckpoint(f'ai/models/{symbol}.h5', save_best_only=True, verbose=0)
    early = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, baseline=0.1)
    model.compile(optimizer=tf.keras.optimizers.Adam(0.1), loss='mean_absolute_error')
    model.fit(x=x, y=y, validation_data=(val_x, val_y), epochs=100, callbacks=[reduce_lr, check, early], verbose=0)
    return model


if __name__ == "__main__":
    if not os.path.exists("data/symbols.pkl"):
        symbols = data.get_symbols()
    else:
        with open("data/symbols.pkl", "rb") as f:
            symbols = pickle.load(f)

    if not os.path.exists('ai/models'):
        os.mkdir('ai/models')
    # if not os.path.exists('ai/test_images'):
    #     os.mkdir('ai/test_images')
    if not os.path.exists('ai/prediction_data'):
        os.mkdir('ai/prediction_data')
    if not os.path.exists('data/stock_data'):
        os.mkdir('data/stock_data')
    if len(os.listdir('data/stock_data')) == 0:
        data.get_data()

    start = time.time()

    for symbol in symbols:
        df = load_data(symbol).tail(1500)
        if df.empty:
            print(f'{symbol} does not have data')
            continue
        if df.shape[0] < 300:
            print(f'{symbol} does not have enough data')
            continue

        normalizer = preprocessing.MinMaxScaler()
        df = normalizer.fit_transform(df)
        a = int(-df.shape[0] * .2)

        x = df[:a][:-1]
        y = df[:a][1:]

        val_x = df[a:][:-1]
        val_y = df[a:][1:]

        model = make_model(symbol, x, y, val_x, val_y)
        try:
            predict = model.predict(np.array([df[-1]]))

            # date = pd.to_datetime(df.index).to_frame(index=False)
            date = df.index.astype('datetime64[ns]')
            days = 99
            dates = pd.date_range(start=date[-1], periods=days + 1)
            for x in range(days):
                predict = np.append(predict, model.predict(np.array([predict[x]])), axis=0)

            df = normalizer.inverse_transform(df)
            predict = normalizer.inverse_transform(predict)

            dates = dates.to_frame(index=False).rename(columns={0: 'date'})
            prediction = dates.join(pd.DataFrame(predict, columns=['close', 'high', 'low', 'open']))
            prediction.drop(columns=['high', 'low', 'open'], inplace=True)

            with open(f'ai/prediction_data/{symbol}.pkl', "wb") as f:
                pickle.dump(prediction.to_dict('records'), f)

            # plt.savefig(f'ai/test_images/{symbol}.png')
            # plt.clf()
            # np.savetxt(f'ai/predictions/{symbol}.csv', predict, delimiter=',', header='close,high,low,open', comments='')
            print(f'finished {symbol}')
        except:
            print(sys.exc_info())

    print(f'total time = {(time.time() - start) / 60} minutes')
