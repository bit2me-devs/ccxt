# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxtpro.base.exchange import Exchange
import ccxt.async_support as ccxt
import hashlib


class poloniex(Exchange, ccxt.poloniex):

    def describe(self):
        return self.deep_extend(super(poloniex, self).describe(), {
            'has': {
                'ws': True,
                'watchTicker': True,
                'watchTickers': False,  # for now
                'watchTrades': True,
                'watchOrderBook': True,
                'watchBalance': False,  # not implemented yet
            },
            'urls': {
                'api': {
                    'ws': 'wss://api2.poloniex.com',
                },
            },
            'options': {
                'tradesLimit': 1000,
            },
        })

    def handle_tickers(self, client, message):
        #
        #     [
        #         1002,
        #         null,
        #         [
        #             50,               # currency pair id
        #             '0.00663930',     # last trade price
        #             '0.00663924',     # lowest ask
        #             '0.00663009',     # highest bid
        #             '0.01591824',     # percent change in last 24 hours
        #             '176.03923205',   # 24h base volume
        #             '26490.59208176',  # 24h quote volume
        #             0,                # is frozen
        #             '0.00678580',     # highest price
        #             '0.00648216'      # lowest price
        #         ]
        #     ]
        #
        channelId = self.safe_string(message, 0)
        subscribed = self.safe_value(message, 1)
        if subscribed:
            # skip subscription confirmation
            return
        ticker = self.safe_value(message, 2)
        numericId = self.safe_string(ticker, 0)
        market = self.safe_value(self.options['marketsByNumericId'], numericId)
        if market is None:
            # todo handle market not found, reject corresponging futures
            return
        symbol = self.safe_string(market, 'symbol')
        timestamp = self.milliseconds()
        open = None
        change = None
        average = None
        last = self.safe_float(ticker, 1)
        relativeChange = self.safe_float(ticker, 4)
        if relativeChange != -1:
            open = last / self.sum(1, relativeChange)
            change = last - open
            average = self.sum(last, open) / 2
        result = {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 8),
            'low': self.safe_float(ticker, 9),
            'bid': self.safe_float(ticker, 3),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 2),
            'askVolume': None,
            'vwap': None,
            'open': open,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': change,
            'percentage': relativeChange * 100,
            'average': average,
            'baseVolume': self.safe_float(ticker, 6),
            'quoteVolume': self.safe_float(ticker, 5),
            'info': ticker,
        }
        self.tickers[symbol] = result
        messageHash = channelId + ':' + numericId
        client.resolve(result, messageHash)

    async def watch_balance(self, params={}):
        await self.load_markets()
        self.balance = await self.fetchBalance(params)
        channelId = '1000'
        subscribe = {
            'command': 'subscribe',
            'channel': channelId,
        }
        messageHash = channelId + ':b:e'
        url = self.urls['api']['ws']
        return await self.watch(url, messageHash, subscribe, channelId)

    async def watch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        numericId = self.safe_string(market, 'numericId')
        channelId = '1002'
        messageHash = channelId + ':' + numericId
        url = self.urls['api']['ws']
        subscribe = {
            'command': 'subscribe',
            'channel': channelId,
        }
        return await self.watch(url, messageHash, subscribe, channelId)

    async def watch_tickers(self, symbols=None, params={}):
        await self.load_markets()
        channelId = '1002'
        messageHash = channelId
        url = self.urls['api']['ws']
        subscribe = {
            'command': 'subscribe',
            'channel': channelId,
        }
        future = self.watch(url, messageHash, subscribe, channelId)
        return await self.after(future, self.filterByArray, 'symbol', symbols)

    async def load_markets(self, reload=False, params={}):
        markets = await super(poloniex, self).load_markets(reload, params)
        marketsByNumericId = self.safe_value(self.options, 'marketsByNumericId')
        if (marketsByNumericId is None) or reload:
            marketsByNumericId = {}
            for i in range(0, len(self.symbols)):
                symbol = self.symbols[i]
                market = self.markets[symbol]
                numericId = self.safe_string(market, 'numericId')
                marketsByNumericId[numericId] = market
            self.options['marketsByNumericId'] = marketsByNumericId
        return markets

    async def watch_trades(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        numericId = self.safe_string(market, 'numericId')
        messageHash = 'trades:' + numericId
        url = self.urls['api']['ws']
        subscribe = {
            'command': 'subscribe',
            'channel': numericId,
        }
        return await self.watch(url, messageHash, subscribe, numericId)

    async def watch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        numericId = self.safe_string(market, 'numericId')
        messageHash = 'orderbook:' + numericId
        url = self.urls['api']['ws']
        subscribe = {
            'command': 'subscribe',
            'channel': numericId,
        }
        future = self.watch(url, messageHash, subscribe, numericId)
        return await self.after(future, self.limit_order_book, symbol, limit, params)

    def limit_order_book(self, orderbook, symbol, limit=None, params={}):
        return orderbook.limit(limit)

    async def watch_heartbeat(self, params={}):
        await self.load_markets()
        channelId = '1010'
        url = self.urls['api']['ws']
        return await self.watch(url, channelId)

    def sign_message(self, client, messageHash, message, params={}):
        if messageHash.find('1000') == 0:
            throwOnError = False
            if self.check_required_credentials(throwOnError):
                nonce = self.nonce()
                payload = self.urlencode({'nonce': nonce})
                signature = self.hmac(self.encode(payload), self.encode(self.secret), hashlib.sha512)
                message = self.extend(message, {
                    'key': self.apiKey,
                    'payload': payload,
                    'sign': signature,
                })
        return message

    def handle_heartbeat(self, client, message):
        #
        # every second(approx) if no other updates are sent
        #
        #     [1010]
        #
        channelId = '1010'
        client.resolve(message, channelId)

    def handle_trade(self, client, trade, market=None):
        #
        # public trades
        #
        #     [
        #         "t",  # trade
        #         "42706057",  # id
        #         1,  # 1 = buy, 0 = sell
        #         "0.05567134",  # price
        #         "0.00181421",  # amount
        #         1522877119,  # timestamp
        #     ]
        #
        id = self.safe_string(trade, 1)
        isBuy = self.safe_integer(trade, 2)
        side = 'buy' if isBuy else 'sell'
        price = self.safe_float(trade, 3)
        amount = self.safe_float(trade, 4)
        timestamp = self.safe_timestamp(trade, 5)
        symbol = None
        if market is not None:
            symbol = market['symbol']
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'id': id,
            'order': None,
            'type': None,
            'takerOrMaker': None,
            'side': side,
            'price': price,
            'amount': amount,
            'cost': price * amount,
            'fee': None,
        }

    def handle_order_book_and_trades(self, client, message):
        #
        # first response
        #
        #     [
        #         14,  # channelId == market['numericId']
        #         8767,  # nonce
        #         [
        #             [
        #                 "i",  # initial snapshot
        #                 {
        #                     "currencyPair": "BTC_BTS",
        #                     "orderBook": [
        #                         {"0.00001853": "2537.5637", "0.00001854": "1567238.172367"},  # asks, price, size
        #                         {"0.00001841": "3645.3647", "0.00001840": "1637.3647"}  # bids
        #                     ]
        #                 }
        #             ]
        #         ]
        #     ]
        #
        # subsequent updates
        #
        #     [
        #         14,
        #         8768,
        #         [
        #             ["o", 1, "0.00001823", "5534.6474"],  # orderbook delta, bids, price, size
        #             ["o", 0, "0.00001824", "6575.464"],  # orderbook delta, asks, price, size
        #             ["t", "42706057", 1, "0.05567134", "0.00181421", 1522877119]  # trade, id, side(1 for buy, 0 for sell), price, size, timestamp
        #         ]
        #     ]
        #
        marketId = str(message[0])
        nonce = message[1]
        data = message[2]
        market = self.safe_value(self.options['marketsByNumericId'], marketId)
        symbol = self.safe_string(market, 'symbol')
        orderbookUpdatesCount = 0
        tradesCount = 0
        stored = self.safe_value(self.trades, symbol, [])
        for i in range(0, len(data)):
            delta = data[i]
            if delta[0] == 'i':
                snapshot = self.safe_value(delta[1], 'orderBook', [])
                sides = ['asks', 'bids']
                self.orderbooks[symbol] = self.order_book()
                orderbook = self.orderbooks[symbol]
                for j in range(0, len(snapshot)):
                    side = sides[j]
                    bookside = orderbook[side]
                    orders = snapshot[j]
                    prices = list(orders.keys())
                    for k in range(0, len(prices)):
                        price = prices[k]
                        amount = orders[price]
                        bookside.store(float(price), float(amount))
                orderbook['nonce'] = nonce
                orderbookUpdatesCount = self.sum(orderbookUpdatesCount, 1)
            elif delta[0] == 'o':
                orderbook = self.orderbooks[symbol]
                side = 'bids' if delta[1] else 'asks'
                bookside = orderbook[side]
                price = float(delta[2])
                amount = float(delta[3])
                bookside.store(price, amount)
                orderbookUpdatesCount = self.sum(orderbookUpdatesCount, 1)
                orderbook['nonce'] = nonce
            elif delta[0] == 't':
                trade = self.handle_trade(client, delta, market)
                stored.append(trade)
                storedLength = len(stored)
                if storedLength > self.options['tradesLimit']:
                    stored.pop(0)
                tradesCount = self.sum(tradesCount, 1)
        if orderbookUpdatesCount:
            # resolve the orderbook future
            messageHash = 'orderbook:' + marketId
            orderbook = self.orderbooks[symbol]
            client.resolve(orderbook, messageHash)
        if tradesCount:
            self.trades[symbol] = stored
            # resolve the trades future
            messageHash = 'trades:' + marketId
            # todo: incremental trades
            client.resolve(self.trades[symbol], messageHash)

    def handle_account_notifications(self, client, message):
        # not implemented yet
        return message

    def handle_message(self, client, message):
        channelId = self.safe_string(message, 0)
        methods = {
            # '<numericId>': 'handleOrderBookAndTrades',  # Price Aggregated Book
            '1000': self.handle_account_notifications,  # Beta
            '1002': self.handle_tickers,  # Ticker Data
            # '1003': None,  # 24 Hour Exchange Volume
            '1010': self.handle_heartbeat,
        }
        method = self.safe_value(methods, channelId)
        if method is None:
            market = self.safe_value(self.options['marketsByNumericId'], channelId)
            if market is None:
                return message
            else:
                return self.handle_order_book_and_trades(client, message)
        else:
            method(client, message)
