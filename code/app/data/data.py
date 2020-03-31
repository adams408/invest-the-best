import os
import requests
import bs4 as bs
import pickle
import pandas_datareader.data as web


def get_symbols():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})

    symbols = []
    for row in table.findAll('tr')[1:]:
        symbol = row.findAll('td')[0].text
        symbols.append(symbol.replace('\n', ''))
    # print(symbols)

    with open("symbols.pickle", "wb") as f:
        pickle.dump(symbols, f)
    return symbols


def get_data():
    if not os.path.exists("symbols.pickle"):
        symbols = get_symbols()
    else:
        with open("symbols.pickle", "rb") as f:
            symbols = pickle.load(f)
    # print(symbols)

    if not os.path.exists('stock_data'):
        os.makedirs('stock_data')

    os.environ['TIINGO_API_KEY'] = '31db9807b1b41a9e85229876c01472b6a4f263ed'

    for symbol in symbols:
        if not os.path.exists('stock_data/{}.csv'.format(symbol)):
            try:
                df = web.get_data_tiingo(symbol.replace('.', '-'), api_key=os.getenv('TIINGO_API_KEY'))
                df.reset_index(inplace=True)
                df.set_index("date", inplace=True)
                df.to_csv('stock_data/{}.csv'.format(symbol))
            except Exception:
                print(symbol + ' not found')


if __name__ == '__main__':
    get_data()
