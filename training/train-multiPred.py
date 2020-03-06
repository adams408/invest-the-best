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



def load_data(ticker):
    df = pd.DataFrame()
    if os.path.exists(f'data/stock_data/{ticker}.csv'):
        df = pd.read_csv(f'data/stock_data/{ticker}.csv',index_col='date',usecols=[0,2,3,4,5])
    else:
        print(f'{ticker} data not found\ntrying to download...')
######    MODIFIED CODE FROM 'data.py'    ######
        os.environ['TIINGO_API_KEY'] = '31db9807b1b41a9e85229876c01472b6a4f263ed'
        try:
            df = web.get_data_tiingo(ticker, api_key=os.getenv('TIINGO_API_KEY'))
            df.reset_index(inplace=True)
            df.set_index('date', inplace=True)
            df.to_csv(f'data/stock_data/{ticker}.csv')
            df.drop(columns=['symbol','volume','adjClose','adjHigh',
                             'adjLow','adjOpen','adjVolume','divCash','splitFactor'],inplace=True)
            
################################################
        except:
##            print(sys.exc_info[0],df)
            pass
    return df

def makemodel(ticker,x,y,val_x,val_y):
    
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(32,activation = 'linear'))
    model.add(tf.keras.layers.Dense(64,activation = 'linear'))
##    model.add(tf.keras.layers.Dense(128,activation = 'linear'))
    model.add(tf.keras.layers.Dense(4,activation = 'linear'))
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.8,
                              patience=0, min_lr=0.00001,mode='min',verbose=0)
    check = tf.keras.callbacks.ModelCheckpoint(f'training/models/{ticker}.h5',save_best_only=True,verbose=0)
    early = tf.keras.callbacks.EarlyStopping(monitor='val_loss',patience=10, baseline=0.1)
    model.compile(optimizer = tf.keras.optimizers.Adam(0.1),loss='mean_absolute_error')
    model.fit(x=x,y=y,validation_data=(val_x,val_y),epochs=100,
              callbacks=[reduce_lr,check,early],verbose=0)
    return model

    
if __name__ == "__main__":
    start = time.time()
    if not os.path.exists('training/models'):
        os.mkdir('training/models')
    if not os.path.exists('data/stock_data'):
        os.mkdir('data/stock_data')
    if not os.path.exists('training/test_images'):
        os.mkdir('training/test_images')
    if not os.path.exists('training/predictions'):
        os.mkdir('training/predictions')
    if not os.path.exists("data/symbols.pickle"):
##        symbols = data.get_symbols()
        print('Symbols file needs to be downloaded into data directory.')
    else:
        with open("data/symbols.pickle", "rb") as f:
            symbols = pickle.load(f)
##    print(os.getcwd())
##    exit()
    if len(os.listdir('data/stock_data')) == 0:
        data.get_data()
    
    for ticker in symbols:
##        if os.path.exists(f'models/{ticker}.h5'):
##            continue
        df = load_data(ticker).tail(1500)
        if df.empty:
            print(f'{ticker} is not availible at this time')
            continue
        if df.shape[0] < 300:
            print(f'{ticker} does not have enough data')
            continue
        date_range = df.index.tolist()
        normalizer = preprocessing.MinMaxScaler()
        df = normalizer.fit_transform(df)

        a = int(-df.shape[0]*.2)
##        b = int(a*.3)
        
        train = df[:a]
        val = df[a:]
##        val = df[a:b]
##        test = df[b:]

        x = train[:-1]
        y = train[1:]

        val_x = val[:-1]
        val_y = val[1:]
        
        if not os.path.exists(f'training/models/{ticker}.h5'):
            model = makemodel(ticker,x,y,val_x,val_y)
        else:
            model = tf.keras.models.load_model(f'training/models/{ticker}.h5')
##        pred_test = model.predict(test)
        try:
            predict = model.predict(np.array([df[-1]]))
        except:
            print(sys.exc_info[0])
        days = 100
        
        for x in range(days):
            predict = np.append(predict,model.predict(np.array([predict[x]])),axis=0)

        df = normalizer.inverse_transform(df)
##        pred_test = normalizer.inverse_transform(pred_test)
        predict = normalizer.inverse_transform(predict)

        t = len(date_range)
        plt.plot(range(t),df[:,-1], label='real')
##        plt.plot(date_range[c:],pred_test[:,:], label='pred0')
        plt.plot(range(t-1,t+days),predict[:,:], label='pred')
        plt.savefig(f'training/test_images/{ticker}.png')

        plt.clf()
        np.savetxt(f'training/predictions/{ticker}.csv',predict, delimiter=',',header='close,high,low,open',comments='')
        print(f'finished {ticker}')
    print(f'Total time = {(time.time()-start)/60}')
