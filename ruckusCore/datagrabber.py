"""
Datasmith.
by: AlphaGriffin


__author__      = "Eric Petersen @Ruckusist"
__copyright__   = "Copyright 2020, The Alpha Griffin Project"
__credits__     = ["Eric Petersen", "Shawn Wilson", "@alphagriffin"]
__license__     = "***"
__version__     = "0.0.4"
__maintainer__  = "Eric Petersen"
__email__       = "ruckusist@alphagriffin.com"
__status__      = "Beta"
"""

import os, sys, time, datetime, collections, re
import random, pathlib
import csv
from itertools import cycle
from timeit import default_timer as timer
import numpy as np
import pandas as pd

from termcolor import colored, cprint
from .filesystem import Filesystem
from .utils import protected, isnotebook
import ccxt


class Data(object):
    def __init__(self):
        self.filesystem = Filesystem()
        self.columns = ['timestamp','Open','High','Low','Close','Volume']


class Datasmith(Data):
    """
    RuckusCore Datasmith.
    """
    def __init__(self):
        super().__init__()
        
        self.data_dir = ""
        self.setup()

    def __call__(self): return self.get_historical_update()

    def __str__(self): return self.__doc__

    def setup(self):
        self.data_dir = os.path.join(self.filesystem.app_dir, "data")
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        self.exchange = ccxt.coinbasepro()
        market_data_path = os.path.join(self.data_dir, "markets.txt")
        if os.path.exists(market_data_path):
            self.markets = []
            with open(market_data_path, "r") as data:
                counter = 0
                while True:
                    counter += 1
                    if counter == 1:
                        data.readline()
                        continue
                    d = data.readline()
                    if d:
                        self.markets.append(data.readline().strip('\n'))
                    else:
                        break
        else:
            self.markets = self.exchange.load_markets()
            with open(market_data_path, "w") as data:
                data.write(f"Market Data for coinbasepro march 2020\n")
                for i in self.markets:
                    data.write(f"{i}\n")
            for k, v in self.markets.items():
                base, coin = k.split('/')
                pair = f"{base}_{coin}"
                with open(os.path.join(self.data_dir, f"{pair}.txt"), "w") as data:
                    data.write(f"Coin Data from coinbasepro march 2020\n")
                    for a, b in v.items():
                        if a == "info": continue
                        data.write(f"{a:20s}: {b}\n")
                # print(k, v)

    def open(self, filename):
        self._dataframe = pd.read_csv(
                os.path.join(self.data_dir, filename),
                names=self.columns
        )
        self._dataframe = self.fix_time(self._dataframe)
        self._dataframe.set_index(
            pd.DatetimeIndex(
                self._dataframe['timestamp']),
            inplace=True)
        self._dataframe.start_date = self._dataframe.index[0]
        self._dataframe.end_date = self._dataframe.index[-1]

    def get_historical_update(self):
        if isnotebook():
            from tqdm.notebook import trange, tqdm
        else:
            from tqdm import tqdm, trange
        with tqdm(
            total=len(self.markets),
            unit=' pairs',
            unit_scale=False,
            leave=False,
            ) as pbar:
            for base_pair in sorted(self.markets):
                coin, base = base_pair.split('/')
                filename = f'{coin}_{base}.csv'
                filepath = os.path.join(self.data_dir, filename)
                pbar.set_postfix(file=filename[:-4], refresh=False)
                pbar.update(1)

                # CHECK IF FILE EXISTS:
                if os.path.exists(filepath):
                    start_read_time = timer()
                    # check file for most recent timestamp 
                    # print(filepath)   
                    with open(filepath, 'r') as cur_file:
                        reader = csv.reader(cur_file)
                        full_csv = [ *reader ]
                    if not full_csv: continue
                    since = int(int(full_csv[-1][0]))
                    lasttimestamp = int(int(full_csv[-1][0]) / 1000)
                    t = datetime.datetime.fromtimestamp( lasttimestamp )
                    if time.time() - lasttimestamp > 86400:
                        tqdm.write(colored(f'{base_pair} NOT up to date... --> {t}', color='yellow'))
                        since_str = t
                    else:
                        tqdm.write(colored(f'{base_pair} up to date! --> {t} - {lasttimestamp}', color='green'))
                        continue
                else:
                    since_str = '2020-01-01T00:00:00Z'

                # FINALLY JUST GET THE DATA!!
                # try:
                # [THIS IS THE FIRST RUN EVER .. EVER]
                    
                timeframe = '1h'
                tqdm.write(colored(f'Downloading Historical Data {base_pair} Since {since_str} in {timeframe} Candles', color='yellow'))
                # Keep making calls to recover all the data.
                now = self.exchange.milliseconds()
                # since = self.exchange.parse8601(since_str)
                #  print(now, since)
                # continue
                dataset = []
                start_download_time = timer()
                while since < now:
                    data = self.exchange.fetch_ohlcv(base_pair, timeframe, since)
                    if not data: break
                    dataset.extend(tuple(data))
                    msg  = f"First candle: {self.exchange.iso8601(data[0][0])} "
                    msg += f"Last candle: {self.exchange.iso8601(data[-1][0])} "
                    msg += f"Candles returned: {len(data)}"
                    since += len(data) * 60000 * 60
                    tqdm.write(msg)
                    time.sleep(3)
                total_download_time = timer() - start_download_time
                tqdm.write(colored(f'Download time was {total_download_time:.2f} secs', color='cyan'))
                # historicial_data = self.exchange.fetch_ohlcv(symbol, '1h')
                tqdm.write(colored(f'Writing Data to Disk', color='cyan'))
                with open(filepath, 'w', newline='') as cur_file:
                    writer = csv.DictWriter(cur_file, fieldnames=self.columns)
                    for entry in dataset:
                        writer.writerow({
                            'timestamp': entry[0],
                            'Open': entry[1],
                            'High': entry[2],
                            'Low': entry[3],
                            'Close': entry[4],
                            'Volume': entry[5]
                        })
                # except:
                #    tqdm.write(f"FAILING to get coin: {base_pair} | SKIPPING")
                #    pass

                # NOW WE NEED TO WRAP UP, REPORT AND BE DONE.
                # break
                tqdm.write(colored(f"Sleeping...", "cyan"))
                time.sleep(4)


class MakeData(object):
    """
    Bittensor.
    Another AlphaGriffin Project 2018.
    Alphagriffin.com
    """

    def __init__(self, options=None):
        """Use the options for a proper setup."""
        self.options = options
        self._dir_loc = os.path.join(os.getcwd(), 'exchanges')
        # self.file_loc = 'C:\\datasets\\files' # fucking windows
        self.columns = ['timestamp','Open','High','Low','Close','Volume']
        self.file_loc = ''
        self._cur_exchange = ''
        self._all_exchanges = []
        self._all_pairs = []
        self._dataframe = None
        self._candleframe = None
        self._pair = None
        self.max_time_frame = 75
        self._next_filename = None

        self.all_exchanges = self._dir_loc
        # self.cur_exchange = self.all_exchanges[0]
        self.cur_exchange = None
        self.next_filename = self.file_loc

    def main(self):
        sample = self.random_filename
        print('{}'.format(self.pair))

        self.dataframe = sample
        print(self.dataframe.tail(2))

        normal = self.make_normal(self.dataframe)
        inputs = self.make_input_from_normal(normal)
        for i in inputs:
            print(i)
        return True

    @property
    def cur_exchange(self):
        return self._cur_exchange

    @cur_exchange.setter
    def cur_exchange(self, value):
        self._cur_exchange = value
        ex_dir = os.path.join(self._dir_loc, value)
        self.file_loc = ex_dir
        self.all_pairs = ex_dir
        self.total_coins = len(os.listdir(ex_dir))

    @property
    def pair(self):
        return self._pair

    @pair.setter
    def pair(self, value):
        # value = '{}_{}'.format(value.split('/')[0], value.split('/')[1])
        value = value[:-4]  # remove .csv
        self._pair = value

    @property
    def random_filename(self):
        filename = os.listdir(self.file_loc)[random.randint(1, len(os.listdir(self.file_loc)))]
        self.pair = filename
        return filename

    @property
    def next_filename(self):
        try:
            filename = next(self._next_filename)
            self.pair = filename
        except:
            self._next_filename = iter(os.listdir(self.file_loc))
            filename = None
        return filename

    @next_filename.setter
    def next_filename(self, value):
        self._next_filename = iter(os.listdir(value))

    @property
    def candles(self):
        return self._candleframe

    @candles.setter
    def candles(self, value):
        # maybe this could take a tuple of (df, periods)
        # but that doesnt sound intuitive.. ???
        self._candleframe = self.make_candles(period=value)
        self._candleframe.pair = self.pair

    @property
    def dataframe(self):
        return self._dataframe

    @dataframe.setter
    def dataframe(self, value):
        self._dataframe = pd.read_csv(
                os.path.join(self.file_loc, value),
                names=self.columns
        )
        self._dataframe = self.fix_time(self._dataframe)
        self._dataframe.set_index(
            pd.DatetimeIndex(
                self._dataframe['timestamp']),
            inplace=True)
        self._dataframe.start_date = self._dataframe.index[0]
        self._dataframe.end_date = self._dataframe.index[-1]
        self._candleframe = self.make_candles(self.dataframe)
        self._dataframe.pair = self._candleframe.pair = value[:-4]

    @property
    def all_pairs(self):
        return self._all_pairs

    @all_pairs.setter
    def all_pairs(self, value):
        self._all_pairs = [x for x in os.listdir(value)]

    @property
    def all_exchanges(self):
        return self._all_exchanges

    @all_exchanges.setter
    def all_exchanges(self, value):
        # list(os.listdir(value))
        try:
            self._all_exchanges = [x for x in os.listdir(value)]
        except:
            self._all_exchanges = [None]

    def fix_time(self, dataframe=None):
        if dataframe is None:
            dataframe = self.dataframe
        time = dataframe.pop('timestamp')
        transform = time.apply(lambda x:
                                datetime.datetime.fromtimestamp(
                                        x/1000
                                    ).strftime('%Y-%m-%d %H:%M:%S'))
        dataframe = dataframe.join(transform, how='inner')
        return dataframe

    def make_candles(self, df=None, column='Close', period='5T'):
        '''Slice the data for any candle periods'''
        if df is None:
            df = self._dataframe
        candles = pd.DataFrame()
        candles['Open'] = df['Open'].resample(period).first().values
        candles['High'] = df['High'].resample(period).max().values
        candles['Low'] = df['Low'].resample(period).min().values
        candles['Close'] = df['Close'].resample(period).last().values
        candles['Volume'] = df['Volume'].resample(period).last().values
        candles['timestamp'] = df['timestamp'].resample(period).last().values
        """
        try:
            candles['timestamp'] = pd.DatetimeIndex(
                # this is not working properly !!  #DUH! didnt resample.
                df['timestamp'][:len(candles.index)].values
                # df['timestamp'][:].values
                )
        except:
            candles['timestamp'] = pd.DatetimeIndex(
                # this is not working properly !!  #DUH! didnt resample.
                df['timestamp'].values
                )
        """
        candles.fillna(method='bfill')
        candles.set_index('timestamp', inplace=True)

        return candles



def main():
    """Loads Options ahead of the app"""
    # config = options.Options('config/access_codes.yaml')
    app = Datasmith()
    protected(app())

if __name__ == '__main__':
    main()
    print('Thanks!')
    print('BitTensor - AlphaGriffin | 2018')
