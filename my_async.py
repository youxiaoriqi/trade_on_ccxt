# -*- coding: utf-8 -*-

import asyncio
import functools
import os
import sys


root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root + '/ccxt/python')
#print(root)

import ccxt.async as ccxt  # noqa: E402

from color_dump import *

async def print_ticker(symbol, id):
    # verbose mode will show the order of execution to verify concurrency
    exchange = getattr(ccxt, id)({'verbose': False,'enableRateLimit': True})

    ticker = {}

    try:
        #await exchange.load_markets(True)

        ticker = await exchange.fetch_ticker(symbol)
        #print(ticker)
        print('successed ' + id)
        ticker['id'] = id

    except ccxt.DDoSProtection as e:
        dump(yellow(type(e).__name__), e.args)
    except ccxt.RequestTimeout as e:
        dump(yellow(type(e).__name__), e.args)
    except ccxt.AuthenticationError as e:
        ticker = {'error': True, 'id': id}
        dump(yellow(type(e).__name__), e.args)
    except ccxt.ExchangeNotAvailable as e:
        ticker = {'error': True, 'id': id}
        dump(yellow(type(e).__name__), e.args)
    except ccxt.ExchangeError as e:
        ticker = {'error': True,'id': id}
        dump(yellow(type(e).__name__), e.args)
    except ccxt.NetworkError as e:
        dump(yellow(type(e).__name__), e.args)
    except Exception as e:  # reraise all other exceptions
        #raise
        print('failed ' + id)
        print(e)
    await exchange.close()

    #print('ok')
    return ticker


if __name__ == '__main__':

    import time

    symbol = 'LTC/ETH'
    #symbol = 'BAT/ETH'

    exchanges_list = ccxt.exchanges

    #检查交易所是否支持交易对
    print(exchanges_list)

    exchanges_list.remove("fybse")
    exchanges_list.remove("fybsg")
    exchanges_list.remove("huobicny")
    exchanges_list.remove("hitbtc")
    exchanges_list.remove("bitfinex")
    exchanges_list.remove("btcturk")


    while len(exchanges_list) > 0:

        print(len(exchanges_list))

        print_ethbtc_ticker = functools.partial(print_ticker, symbol)
        pending = [asyncio.ensure_future(print_ethbtc_ticker(id)) for id in exchanges_list]
        #pending = asyncio.Task.all_tasks()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*pending))
        tickers_list = {}
        for task in pending:
            task_result = task.result()

            if task_result is None:
                continue

            if "error" in task_result.keys() and task_result["error"] == True:
                exchanges_list.remove(task_result['id'])

            #去掉fybsg,vaultoro
            if("id" in task_result.keys() and  task_result['id']  in ['fybsg','fybse','vaultoro']):
                continue

            if("last" in task_result.keys() and task_result['last'] is not None and task_result['last'] != 0):
                tickers_list[task_result['id']] = task_result

        if len(tickers_list) == 0:
            continue


        max_id = max(tickers_list,key=lambda key:float(tickers_list[key]['bid']))
        min_id = min(tickers_list,key=lambda key:float(tickers_list[key]['ask']))
        #print(tickers_list)
        print(tickers_list[min_id])
        print(tickers_list[max_id])
        print(min_id + str(tickers_list[min_id]['ask']))
        print(max_id + str(tickers_list[max_id]['bid']))
        print((tickers_list[max_id]['bid'] - tickers_list[min_id]['ask']) / tickers_list[max_id]['bid'] * 100)
        #print(time.time())
        #time.sleep(5)

