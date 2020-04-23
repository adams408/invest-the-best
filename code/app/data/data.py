import os
import requests
import bs4 as bs
import pickle


def get_symbols():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})

    symbols = []
    for row in table.findAll('tr')[1:]:
        symbol = row.findAll('td')[0].text
        symbols.append(symbol.replace('\n', ''))

    with open("symbols.pkl", "wb") as f:
        pickle.dump(symbols, f)
    return symbols


def get_data():
    if not os.path.exists("symbols.pkl"):
        symbols = get_symbols()
    else:
        with open("symbols.pkl", "rb") as f:
            symbols = pickle.load(f)

    if not os.path.exists('stock_data'):
        os.makedirs('stock_data')

    for symbol in symbols:
        if not os.path.exists('stock_data/{}'.format(symbol)):
            os.makedirs('stock_data/{}'.format(symbol))

        if not os.path.exists('stock_data/{}/meta.csv'.format(symbol)):
            try:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Token 31db9807b1b41a9e85229876c01472b6a4f263ed'
                }
                meta = requests.get("https://api.tiingo.com/tiingo/daily/{}?".format(symbol.replace('.', '-')), headers=headers)
                with open('stock_data/{}/meta.pkl'.format(symbol), "wb") as f:
                    pickle.dump(meta.json(), f)
            except Exception:
                print(symbol + ' not found')

        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Token 31db9807b1b41a9e85229876c01472b6a4f263ed'
            }
            eod = requests.get("https://api.tiingo.com/tiingo/daily/{}/prices?startDate=2019-01-02".format(symbol.replace('.', '-')), headers=headers)
            with open('stock_data/{}/{}.pkl'.format(symbol, symbol), "wb") as f:
                pickle.dump(eod.json(), f)
        except Exception:
            print(symbol + ' not found')


if __name__ == '__main__':
    get_data()
