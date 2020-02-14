#!/usr/bin/python3
"""
Bittensor. Datasmith.
by: AlphaGriffin
"""

__author__ = "Eric Petersen @Ruckusist"
__copyright__ = "Copyright 2018, The Alpha Griffin Project"
__credits__ = ["Eric Petersen", "Shawn Wilson", "@alphagriffin"]
__license__ = "***"
__version__ = "0.0.3"
__maintainer__ = "Eric Petersen"
__email__ = "ruckusist@alphagriffin.com"
__status__ = "Beta"

# generic
import os, sys, time, datetime, collections, re, random
import csv
from tqdm import tqdm, trange
from timeit import default_timer as timer
import ccxt

from itertools import cycle
import numpy as np
import pandas as pd

# from utils import options
from ag.options import Options
# from utils import printer
from ag.printing import Printer, Color


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    MAGENTA = '\u001b[35m'
    YELLOW = '\u001b[33m'
    BRIGHT_YELLOW = '\u001b[33;1m'
    BRIGHT_WHITE = '\u001b[37;1m'
    BRIGHT_GREEN = '\u001b[32;1m'
    CYAN = '\u001b[36m'
    # CURSOR
    # all cursor movements require a .format(num of places to move)
    UP = '\u001b[{n}A'
    DOWN = '\u001b[{n}B'
    LEFT = '\u001b[{n}C'
    RIGHT = '\u001b[{n}D'
    ROW_UP = '\u001b[{n}F'
    ROW_DOWN = '\u001b[{n}E'
    CLEARSCREEN = '\u001b[{n}J'.format(n=2)
    # shapes
    SQUARE = '█'  # '\033[219m'
    SQR = u'\u2588'

class GrabData(object):
    """
    Bittensor.
    Another AlphaGriffin Project 2018.
    Alphagriffin.com
    """

    def __init__(self, options=None):
        """Use the options for a proper setup."""
        self.options = options
        self.filepath = os.path.join(os.getcwd(), 'data', 'exchanges', 'bittrex')
        if not self.check_path_integrity(self.filepath):
            sys.exit('Failure to build filesystem!')
        self.filelist = os.listdir(self.filepath)
        self.columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
        self.P = Printer(options)
        self.P()
        x = self.P('test', ret=True)
        # print(x)

    def main(self):
        self.P('Starting Datagrabber.')
        # exit()
        runtime = timer()
        # check current filesystem
        # if not self.check_last_update():
        self.P('starting historical update')
        self.do_historical_update()
        self.P('Finished Historical Update')
        self.P('Current Runtime: {:.2f} mins'.format(float(timer()-runtime)/60))
        return True

    def write_csv_file(self, filename, data):
        pass

    def do_historical_update(self):
        try:
            exchanges = list(self.options.exchanges.split(','))
            FAILOUT = 0
            exchanges_path = os.path.join(os.getcwd(), 'data', 'exchanges')
            for exchange_name in exchanges:
                exchange = eval('ccxt.{}()'.format(exchange_name))
                eid = exchange.id
                exchange_path = os.path.join(exchanges_path, eid)
                self.P('Fetching Market Data @ {}'.format(eid))
                MARKETS = exchange.fetchMarkets()
                # continue
                sizecounter = 0
                self.P("There are {} Pairs @ {}".format(len(MARKETS), eid))
                self.P()
                with tqdm(
                    total=len(MARKETS),
                    unit=' pairs',
                    unit_scale=False,
                    leave=False,
                ) as pbar:
                    while sizecounter < len(MARKETS):

                        i = MARKETS[sizecounter]
                        pair = i['symbol']
                        coin, base = pair.split('/')
                        filename = '{}_{}_{}.csv'.format(eid, coin, base)
                        filepath = os.path.join(exchange_path, filename)
                        printed_pair = filename[:-4][len(eid)+1:]
                        pbar.set_postfix(file=printed_pair, refresh=False)

                        lasttimestamp = time.time() - 86400*60  # one year ago now...
                        if os.path.exists(filepath):            # unless something already exists
                            with open(filepath, 'r') as cur_file:
                                reader = csv.reader(cur_file)
                                full_csv = [ row for row in reader ]  # <-- What is Pythonic?
                            try:
                                lasttimestamp = int(int(full_csv[-1][0]) / 1000)
                                ish = 86400 / time.time() + 1  # one day ago now...
                                if lasttimestamp * ish >= time.time():
                                    tqdm.write(str(self.P('{} up to date!'.format(pair), ret=True, color='green')))
                                    time.sleep(.1)
                                    sizecounter += 1
                                    pbar.update(1)
                                    continue
                            except:  # Previously failed to write this file.
                                os.remove(filepath)
                                pass

                        time_frame = '5m' if 'poloniex' in eid else '1m'
                        write_time = timer()
                        try:
                            # tqdm.write(self.P('    ' + bcolors.BRIGHT_YELLOW + 'Downloading Historical Data {}'.format(pair) + bcolors.ENDC, ret=True))
                            tqdm.write(self.P('Downloading Historical Data {}'.format(pair), ret=True, color='yellow'))
                            # time.sleep(1.15)
                            historicial_data = exchange.fetch_ohlcv(
                                pair,
                                timeframe=time_frame,
                                since=lasttimestamp,
                                limit=time.time()
                            )
                            # print(historicial_data)
                        except:
                            tqdm.write(str(self.P('Probably failed for a reason. Waiting 20 secs for retry. error {}/5'.format(
                                FAILOUT+1
                            ), ret=True, color='red')))
                            time.sleep(20)
                            if FAILOUT >= 4:
                                sizecounter += 1
                                pbar.update(1)
                                tqdm.write(str(self.P('Bailing on Pair: {}'.format(pair), ret=True)))
                                FAILOUT = 0
                            else:
                                FAILOUT += 1
                            pass

                        check = True
                        with open(filepath, 'a', newline='') as cur_file:
                            # columns = ['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
                            writer = csv.DictWriter(cur_file, fieldnames=self.columns)
                            for i in historicial_data:
                                cur_line_time = i[0] / 1000
                                check_time = datetime.datetime.fromtimestamp(
                                    int(cur_line_time)
                                ).strftime('%Y-%m-%d')  # %H:%M:%S')
                                # IF TIME IS GREATER THAN WHAT WE ALREADY HAVE!
                                if i[0] > int(lasttimestamp*1000):
                                    if check:
                                        check = False
                                        tqdm.write(self.P('Updating Records starting with {}'.format(check_time), ret=True))
                                    writer.writerow({
                                        'timestamp': i[0],
                                        'Open': i[1],
                                        'High': i[2],
                                        'Low': i[3],
                                        'Close': i[4],
                                        'Volume': i[5]
                                    })

                        # END SUCESSFULLY
                        write_time = timer() - write_time
                        sleeptime = 3 - write_time
                        FAILOUT = 0
                        sizecounter += 1
                        pbar.update(1)

                        tqdm.write(self.P('Took {:.2f} secs to write historical data for {} | {}'.format(
                           write_time, eid, pair
                        ), ret=True))
                        if sleeptime > 0:
                            tqdm.write(self.P('Sleeping for {:.2f} secs'.format(sleeptime), ret=True))
                            time.sleep(sleeptime)
        except KeyboardInterrupt:
            print('try to fail safely!')
            sys.exit(0)

    def check_path_integrity(self, path):
        if os.path.exists(path):
            return True
        else:
            # check and make the first dir
            if not os.path.exists(os.path.join(os.getcwd(), 'data')):
                os.mkdir('data')
            # make a general exchanges folder
            if not os.path.exists(os.path.join(os.getcwd(), 'data', 'exchanges')):
                os.mkdir(os.path.join(os.getcwd(), 'data', 'exchanges'))
            # make exchanges folders
            exchanges = list(self.options.exchanges.split(','))
            for e in exchanges:
                if not os.path.exists(os.path.join(os.getcwd(), 'data', 'exchanges', e)):
                    os.mkdir(os.path.join(os.getcwd(), 'data', 'exchanges', e))
        return True

    def check_last_update(self):
        filename = 'bittrex_BTC_USDT.csv'
        path = os.path.join(self.filepath, filename)
        if not os.path.exists(path):
            return False
        with open(path, 'r') as cur_file:
            reader = csv.reader(cur_file)
            full_csv = [row for row in reader]
        lasttimestamp = int(int(full_csv[-1][0]) / 1000)
        ish = 86400 / time.time() + 1
        if lasttimestamp * ish >= time.time():
            self.report('Files are up to date')
            return 0
        else:
            self.report('Files need to be updated!')
            return lasttimestamp

    def write_files(self, ticker, loop_num):
        columns = [
            'timestamp', 'high', 'low',
            'last', 'change', 'baseVolume'
        ]
        for pair in ticker:
            _pair = '{}_{}'.format(pair.split('/')[0], pair.split('/')[1])
            filename = 'bittrex_{}.csv'.format(_pair)
            filepath = os.path.join(self.filepath, filename)
            with open(filepath, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writerow({
                    'timestamp': ticker[pair]['timestamp'],
                    'high': ticker[pair]['high'],
                    'low': ticker[pair]['low'],
                    'last': ticker[pair]['last'],
                    'change': ticker[pair]['change'],
                    'baseVolume': ticker[pair]['baseVolume'],
                })
        return True

    def report(self, data):
        cur_time = datetime.datetime.now()
        color_time = '[{color}{date:%B %d, %Y | %H:%M}{end}]'.format(
            color=Color.OKBLUE,
            date=cur_time,
            end=Color.ENDC
        )
        color_msg = '{color}{message}{end}'.format(
            color=Color.OKGREEN,
            message=data,
            end=Color.ENDC
        )
        print('{} {}'.format(color_time, color_msg))


def main():
    """Loads Options ahead of the app"""
    os.system('cls')
    config = Options('config/access_codes.yaml')
    app = GrabData(config)
    try:
        app.main()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
    # os.system('cls')
    print('Thanks!')
    print('BitTensor - AlphaGriffin | 2018')
