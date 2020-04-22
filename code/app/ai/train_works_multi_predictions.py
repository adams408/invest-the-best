"""
data downloaded from: http://download.macrotrends.net/assets/php/stock_data_export.php?t=[SYMBOL NAME]
read_csv documentation: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html
to_csv documentation: https://pandas.pydata.org/pandas-docs/version/0.19.1/generated/pandas.DataFrame.to_csv.html
"""

import warnings  # warning suppression

with warnings.catch_warnings():
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.preprocessing.text import Tokenizer
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

import datetime as dt
import pandas as pd
from sklearn import preprocessing
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import pandas_datareader.data as web

import sys, os, pickle, time

os.chdir('../')
sys.path.append(os.getcwd())
import data.data

tf.compat.v1.enable_eager_execution()


def load_data(symbol):
    df = pd.DataFrame()
    if os.path.exists(f'data/stock_data/{symbol}.csv'):
        df = pd.read_csv(f'data/stock_data/{symbol}.csv', index_col='date', usecols=[0, 2, 3, 4, 5])
    else:
        print(f'{symbol} data not found\ntrying to download...')
        
        # MODIFIED CODE FROM 'data.py'
        os.environ['TIINGO_API_KEY'] = '31db9807b1b41a9e85229876c01472b6a4f263ed'
        try:
            df = web.get_data_tiingo(symbol, api_key=os.getenv('TIINGO_API_KEY'))
            df.reset_index(inplace=True)
            df.set_index('date', inplace=True)
            df.to_csv(f'data/stock_data/{symbol}.csv')
            df.drop(columns=['symbol', 'volume', 'adjClose', 'adjHigh', 'adjLow', 'adjOpen', 'adjVolume', 'divCash', 'splitFactor'], inplace=True)
        except:
            # print(sys.exc_info[0],df)
            pass
    return df


def make_model(symbol, x, y, val_x, val_y):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(32, activation='linear'))
    model.add(tf.keras.layers.Dense(64, activation='linear'))
    # model.add(tf.keras.layers.Dense(128,activation = 'linear'))
    model.add(tf.keras.layers.Dense(4, activation='linear'))
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.8, patience=0, min_lr=0.00001, mode='min', verbose=0)
    check = tf.keras.callbacks.ModelCheckpoint(f'ai/models/{symbol}.h5', save_best_only=True, verbose=0)
    early = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, baseline=0.1)
    model.compile(optimizer=tf.keras.optimizers.Adam(0.1), loss='mean_absolute_error')
    model.fit(x=x, y=y, validation_data=(val_x, val_y), epochs=100, callbacks=[reduce_lr, check, early], verbose=0)
    return model


if __name__ == "__main__":
    
    start = time.time()
    
    if not os.path.exists('ai/models'):
        os.mkdir('ai/models')
    if not os.path.exists('data/stock_data'):
        os.mkdir('data/stock_data')
    if not os.path.exists('ai/test_images'):
        os.mkdir('ai/test_images')
    if not os.path.exists('ai/predictions'):
        os.mkdir('ai/predictions')
    if not os.path.exists("data/symbols.pickle"):
        # symbols = data.get_symbols()
        print('symbols file needs to be downloaded into data directory.')
    else:
        with open("data/symbols.pickle", "rb") as f:
            symbols = pickle.load(f)
        # print(os.getcwd())
        # exit()

    if len(os.listdir('data/stock_data')) == 0:
        data.get_data()

    for symbol in symbols:
        # if os.path.exists(f'models/{symbol}.h5'):
            # continue
        df = load_data(symbol).tail(1500)
        if df.empty:
            print(f'{symbol} is not availible at this time')
            continue
        if df.shape[0] < 300:
            print(f'{symbol} does not have enough data')
            continue
        date_range = df.index.tolist()
        normalizer = preprocessing.MinMaxScaler()
        df = normalizer.fit_transform(df)

        a = int(-df.shape[0] * .2)
        # b = int(a*.3)

        train = df[:a]
        val = df[a:]
        # val = df[a:b]
        # test = df[b:]

        x = train[:-1]
        y = train[1:]

        val_x = val[:-1]
        val_y = val[1:]

        if not os.path.exists(f'ai/models/{symbol}.h5'):
            model = make_model(symbol, x, y, val_x, val_y)
        else:
            model = tf.keras.models.load_model(f'ai/models/{symbol}.h5')
            # pred_test = model.predict(test)
        try:
            predict = model.predict(np.array([df[-1]]))
        except:
            print(sys.exc_info[0])
        days = 100

        for x in range(days):
            predict = np.append(predict, model.predict(np.array([predict[x]])), axis=0)

        df = normalizer.inverse_transform(df)
        # pred_test = normalizer.inverse_transform(pred_test)
        predict = normalizer.inverse_transform(predict)

        t = len(date_range)
        plt.plot(range(t), df[:, -1], label='real')
        # plt.plot(date_range[c:],pred_test[:,:], label='pred0')
        plt.plot(range(t - 1, t + days), predict[:, :], label='pred')
        plt.savefig(f'ai/test_images/{symbol}.png')

        plt.clf()
        np.savetxt(f'ai/predictions/{symbol}.csv', predict, delimiter=',', header='close,high,low,open', comments='')
        print(f'finished {symbol}')

    print(f'Total time = {(time.time() - start) / 60}')
