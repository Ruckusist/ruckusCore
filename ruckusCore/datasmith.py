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
import random, pathlib, shutil, asyncio
import csv
from itertools import cycle
from timeit import default_timer as timer
from termcolor import colored, cprint
from collections import defaultdict as sdict

from math import floor, ceil
import numpy as np
import pandas as pd
import ccxt

from .filesystem import Filesystem
from .utils import protected, isnotebook
from .talib import TALib


class Data(object):
    def __init__(self, pair):
        self.filesystem = Filesystem()
        self.columns = ['timestamp','Open','High','Low','Close','Volume']
        self.data_dir = os.path.join(self.filesystem.app_dir, "data")
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        self.pair = pair
        self.dataframe = self._dataframe(pair)
        self.build()
        self.candles = self.make_candles(self.dataframe)
        # self.make_numpy()
        self.talib = sdict()
        self.cur_change = 0
        self.ytd_change = 0
        # print(f"Finished Loading Pair: {pair}")

    def __call__(self): return self.dataframe

    def __str__(self): return self.pair

    def __len__(self): return len(self.dataframe)

    @staticmethod
    def fix_time(dataframe):
        time = dataframe.pop('timestamp')
        transform = time.apply(
            lambda x: datetime.datetime.fromtimestamp(x/1000).strftime(
                '%Y-%m-%d %H:%M:%S'))
        dataframe = dataframe.join(transform, how='inner')
        return dataframe

    @staticmethod
    def make_candles(df, column='Close', period='D'):
        '''Slice the data for any candle periods'''
        candles = pd.DataFrame()
        candles['Open'] = df['Open'].resample(period).first().values
        candles['High'] = df['High'].resample(period).max().values
        candles['Low'] = df['Low'].resample(period).min().values
        candles['Close'] = df['Close'].resample(period).last().values
        candles['Volume'] = df['Volume'].resample(period).last().values
        candles['timestamp'] = df['timestamp'].resample(period).last().values
        candles.fillna(method='bfill')
        candles.set_index('timestamp', inplace=True)
        return candles

    def _dataframe(self, value):
        value = "_".join(value.split("/"))
        value = value + ".csv"
        dataframe = pd.read_csv(
            os.path.join(self.data_dir, value), names=self.columns)
        # if not dataframe: return None  #  blank file error.
        dataframe = self.fix_time(dataframe)
        dataframe.set_index(pd.DatetimeIndex(
            dataframe['timestamp']),
            inplace=True)
        dataframe.start_date = dataframe.index[0]
        dataframe.end_date = dataframe.index[-1]
        return dataframe

    async def plot(self, cfg={}):
        max_h, max_w = shutil.get_terminal_size(fallback=(80, 13))
        cfg['height'] = 15
        series = self.candles['Close']
        verbose = False
        minimum = min(series)
        maximum = max(series)
        if verbose: print("Series min/max: {}/{}".format(minimum, maximum))

        interval = abs(float(maximum) - float(minimum))
        offset = cfg['offset'] if 'offset' in cfg else 5
        # padding = cfg['padding'] if 'padding' in cfg else '       '
        height = cfg['height'] if 'height' in cfg else interval
        ratio = height / interval
        min2 = floor(float(minimum) * ratio)
        max2 = ceil(float(maximum) * ratio)

        intmin2 = int(min2)
        intmax2 = int(max2)

        rows = abs(intmax2 - intmin2)
        width = len(series) + offset
        # format = cfg['format'] if 'format' in cfg else lambda x: (padding + '{:.2f}'.format(x))[:-len(padding)]

        result = [[' '] * width for i in range(rows + 1)]

        # axis and labels
        for y in range(intmin2, intmax2 + 1):
            value = float(maximum) - ((y - intmin2) * interval / rows)
            place_values = 2
            if value < 1:
                place_values = 8
            label = colored(f'{value:.{place_values}f}', "cyan")
            result[y - intmin2][max(offset - len(label), 0)] = label
            result[y - intmin2][offset - 1] = colored('┼', "green") if y == 0 else colored('┤', "yellow")

        y0 = int(series[0] * ratio - min2)
        result[rows - y0][offset - 1] = '┼'  # first value
        for x in range(0, len(series) - 1):  # plot the line
            y0 = int(round(series[x + 0] * ratio) - intmin2)
            y1 = int(round(series[x + 1] * ratio) - intmin2)
            if y0 == y1:
                result[rows - y0][x + offset] = '─'
            else:
                result[rows - y1][x + offset] = '╰' if y0 > y1 else '╭'
                result[rows - y0][x + offset] = '╮' if y0 > y1 else '╯'
                start = min(y0, y1) + 1
                end = max(y0, y1)
                for y in range(start, end):
                    result[rows - y][x + offset] = '│'

        # return result
        if False:
            return '\n'.join([''.join(row) for row in result])
        else:
            print('\n'.join([''.join(row) for row in result[-max_w-10:]]))
            # await self.status()

    async def status(self):
        """Rattle off a bunch of info about the pair."""
        await self.do_talib()
        columns, rows = shutil.get_terminal_size(fallback=(80, 24))
        first = self.dataframe['timestamp'][0]
        last = self.dataframe['timestamp'][-1]
        star = "*"*120
        print(f"TIMEFRAME: {first} ==> {last}")
        print(colored(star, "blue"))
        await self.plot()
        print(colored(star, "blue"))
        print(f"MEAN ROC: {self.talib['ROC'].mean():.4f} | Current ROC: {self.talib['ROC'][-1]:.4f}")
        print(f"MEAN MOM: {self.talib['MOM'].mean():.4f} | Current MOM: {self.talib['MOM'][-1]:.4f}")
        print(f"YTD Change: {self.ytd_change:.2f}% | Current Change {self.cur_change:.2f}%")
        pass

    def build(self):
        talib = TALib()
        self.dataframe['ROC'] = talib.ROC(self.dataframe)
        self.columns.append('ROC')
        self.dataframe['MOM'] = talib.MOM(self.dataframe)
        self.columns.append('MOM')
        # self.talib['RSI'] = talib.RSI(self.dataframe)
        # self.talib['ATR'] = talib.ATR(self.dataframe)
        self.dataframe['CCI'] = talib.CCI(self.dataframe)
        self.columns.append('CCI')
        self.dataframe['MA'] = talib.MA(self.dataframe)
        self.columns.append('MA')

    async def do_talib(self):
        talib = TALib()
        self.talib['ROC'] = talib.ROC(self.dataframe)
        self.talib['MOM'] = talib.MOM(self.dataframe)
        # self.talib['RSI'] = talib.RSI(self.dataframe)
        # self.talib['ATR'] = talib.ATR(self.dataframe)
        self.talib['CCI'] = talib.CCI(self.dataframe)
        self.talib['MA'] = talib.MA(self.dataframe)

        # do some other stats.
        self.ytd_change = (self.dataframe['Close'][0]/self.dataframe['Close'][-1]-1)*100
        self.cur_change = (self.dataframe['Close'][-7]/self.dataframe['Close'][-1]-1)*100

    def make_numpy(self):
        """create input training data."""
        talib = TALib()
        cols = [x for x in self.columns]
        cols.pop('timestamp')
        i_split = int(len(self.dataframe) * .75)
        df = talib.unzero(self.dataframe)
        self.matrix_train = df.get(cols).values[:i_split]
        self.matrix_test = df.get(cols).values[i_split:]


class Fully(object):
    """
    RuckusCore Datasmith.
    """
    def __init__(self):
        self.filesystem = Filesystem()
        self.columns = ['timestamp','Open','High','Low','Close','Volume']
        self.data_dir = os.path.join(self.filesystem.app_dir, "data")
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)


class Datasmith(object):
    """
    RuckusCore Datasmith.
    """
    def __init__(self):
        self.filesystem = Filesystem()
        self.columns = ['timestamp','Open','High','Low','Close','Volume']
        self.data_dir = os.path.join(self.filesystem.app_dir, "data")
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        self.setup()

    def __call__(self): return self.get_historical_update()

    def __str__(self): return self.__doc__

    def setup(self):
        self.exchange = ccxt.coinbasepro()
        market_data_path = os.path.join(self.data_dir, "markets.txt")
        if False:
        # if os.path.exists(market_data_path):
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

    async def get_historical_update(self, *args):
        """Download historical dataset of all pairs."""
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
                    # start_read_time = timer()
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
                        tqdm.write(colored(f'{base_pair} up to date! | last: {t}', color='green'))
                        continue
                else:
                    since_str = '2020-01-01T00:00:00Z'
                    since = self.exchange.parse8601(since_str)
 
                timeframe = '1h'
                tqdm.write(colored(f'Downloading Historical Data {base_pair} Since {since_str} in {timeframe} Candles', color='yellow'))
                # Keep making calls to recover all the data.
                now = self.exchange.milliseconds()
                dataset = []
                start_download_time = timer()
                while since < now:
                    try:
                        data = self.exchange.fetch_ohlcv(base_pair, timeframe, since)
                    except:
                        break
                    if not data: break
                    dataset.extend(tuple(data))
                    msg  = f"First candle: {self.exchange.iso8601(data[0][0])} "
                    msg += f"Last candle: {self.exchange.iso8601(data[-1][0])} "
                    msg += f"Candles returned: {len(data)}"
                    since += len(data) * 60000 * 60
                    tqdm.write(msg)
                    time.sleep(2.001)
                total_download_time = timer() - start_download_time
                tqdm.write(colored(f'Download time was {total_download_time:.2f} secs', color='cyan'))
                # historicial_data = self.exchange.fetch_ohlcv(symbol, '1h')
                tqdm.write(colored(f'Writing Data to Disk', color='cyan'))
                if dataset:
                    with open(filepath, 'a+', newline='') as cur_file:
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
                # tqdm.write(colored(f"Sleeping...", "cyan"))
                # time.sleep(4)

    async def purge_files(self, *args):
        """delete all downloaded files."""
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                os.remove(os.path.join(self.data_dir, filename))
        print(colored("all files purged.", "red"))

    async def list_markets(self, *args):
        """list of all available market pairs."""
        print("\n".join(sorted(self.markets)))
        print(f"Total: {len(self.markets)}")

    async def LOOKUP__DATA__FOR___FILENAME(self, *args):
        if args:
            pair = args[-1][-1]
        else:
            return False
        if pair in tuple(self.markets):
            print(f"Looking up {pair}")
        else:
            print(f"pair {pair} not found.")
            return False
        data = Data(pair)
        print(data.candles.tail(5))
        
    async def ascii_graph(self, *args):
        """Graph of Close price over max time frame."""
        if args:
            pair = args[-1][-1]
        else:
            return False
        if pair in tuple(self.markets): pass
            # print(f"Looking up {pair}")
        else:
            print(f"pair {pair} not found.")
            return False
        data = Data(pair)
        await data.plot()

    async def full_status(self, *args):
        """full pair status: input: THIS/THAT."""
        if args:
            pair = args[-1][-1]
        else:
            return False
        if pair in tuple(self.markets): pass
            # print(f"Looking up {pair}")
        else:
            print(f"pair {pair} not found.")
            return False
        data = Data(pair)
        await data.status()

    async def tops(self, *args):
        """this is the goods right here."""
        print("Calculating Tops for last 7 days.")
        dataset = []
        for pair in self.markets:
            try:
                d = Data(pair)
                await d.do_talib()
                dataset.append(d)
            except: pass

        # TOPS - ROC
        new_set = []
        for d in dataset:
            new_set.append((d.talib['ROC'][-1], d.pair))
        x = list(reversed(sorted(new_set, key=lambda x: x[0])))
        print("top 5 Rate of Change Movers")
        for i in x[:5]:
            print(f"{i[1]:8s}: {i[0]:.4f}")
        print("Bottom 5 Rate of Change Losers")
        for i in x[-5:]:
            print(f"{i[1]:8s}: {i[0]:.4f}")

        # TOPS - CUR
        new_set = []
        for d in dataset:
            new_set.append((d.cur_change, d.pair))
        x = list(reversed(sorted(new_set, key=lambda x: x[0])))
        print("top 5 Week Price Change Movers")
        for i in x[:5]:
            print(f"{i[1]:8s}: {i[0]:.4f}")
        print("Bottom 5 Week Price Change Losers")
        for i in x[-5:]:
            print(f"{i[1]:8s}: {i[0]:.4f}")

        # TOPS - YTD
        new_set = []
        for d in dataset:
            new_set.append((d.ytd_change, d.pair))
        x = list(reversed(sorted(new_set, key=lambda x: x[0])))
        print("top 5 YTD Price Change Movers")
        for index, element in enumerate(x[:5]):
            print(f"# {index+1})\t{element[1]:8s}: {element[0]:.4f}")
        print("Bottom 5 YTD Price Change Losers")
        for index, element in enumerate(x[-5:]):
            print(f"# {5-index})\t{element[1]:8s}: {element[0]:.4f}")