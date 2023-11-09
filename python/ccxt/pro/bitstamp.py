# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

import ccxt.async_support
from ccxt.async_support.base.ws.cache import ArrayCache, ArrayCacheBySymbolById
from ccxt.async_support.base.ws.client import Client
from typing import Optional
from ccxt.base.errors import AuthenticationError


class bitstamp(ccxt.async_support.bitstamp):

    def describe(self):
        return self.deep_extend(super(bitstamp, self).describe(), {
            'has': {
                'ws': True,
                'watchOrderBook': True,
                'watchOrders': True,
                'watchTrades': True,
                'watchOHLCV': False,
                'watchTicker': False,
                'watchTickers': False,
            },
            'urls': {
                'api': {
                    'ws': 'wss://ws.bitstamp.net',
                },
            },
            'options': {
                'expiresIn': '',
                'userId': '',
                'wsSessionToken': '',
                'watchOrderBook': {
                    'snapshotDelay': 6,
                    'snapshotMaxRetries': 3,
                },
                'tradesLimit': 1000,
                'OHLCVLimit': 1000,
            },
            'exceptions': {
                'exact': {
                    '4009': AuthenticationError,
                },
            },
        })

    async def watch_order_book(self, symbol: str, limit: Optional[int] = None, params={}):
        """
        watches information on open orders with bid(buy) and ask(sell) prices, volumes and other data
        :param str symbol: unified symbol of the market to fetch the order book for
        :param int [limit]: the maximum amount of order book entries to return
        :param dict [params]: extra parameters specific to the bitstamp api endpoint
        :returns dict: A dictionary of `order book structures <https://github.com/ccxt/ccxt/wiki/Manual#order-book-structure>` indexed by market symbols
        """
        await self.load_markets()
        market = self.market(symbol)
        symbol = market['symbol']
        messageHash = 'orderbook:' + symbol
        channel = 'diff_order_book_' + market['id']
        url = self.urls['api']['ws']
        request = {
            'event': 'bts:subscribe',
            'data': {
                'channel': channel,
            },
        }
        message = self.extend(request, params)
        orderbook = await self.watch(url, messageHash, message, messageHash)
        return orderbook.limit()

    def handle_order_book(self, client: Client, message):
        #
        # initial snapshot is fetched with ccxt's fetchOrderBook
        # the feed does not include a snapshot, just the deltas
        #
        #     {
        #         "data": {
        #             "timestamp": "1583656800",
        #             "microtimestamp": "1583656800237527",
        #             "bids": [
        #                 ["8732.02", "0.00002478", "1207590500704256"],
        #                 ["8729.62", "0.01600000", "1207590502350849"],
        #                 ["8727.22", "0.01800000", "1207590504296448"],
        #             ],
        #             "asks": [
        #                 ["8735.67", "2.00000000", "1207590693249024"],
        #                 ["8735.67", "0.01700000", "1207590693634048"],
        #                 ["8735.68", "1.53294500", "1207590692048896"],
        #             ],
        #         },
        #         "event": "data",
        #         "channel": "diff_order_book_btcusd"
        #     }
        #
        channel = self.safe_string(message, 'channel')
        parts = channel.split('_')
        marketId = self.safe_string(parts, 3)
        symbol = self.safe_symbol(marketId)
        storedOrderBook = self.safe_value(self.orderbooks, symbol)
        nonce = self.safe_value(storedOrderBook, 'nonce')
        delta = self.safe_value(message, 'data')
        deltaNonce = self.safe_integer(delta, 'microtimestamp')
        messageHash = 'orderbook:' + symbol
        if nonce is None:
            cacheLength = len(storedOrderBook.cache)
            # the rest API is very delayed
            # usually it takes at least 4-5 deltas to resolve
            snapshotDelay = self.handle_option('watchOrderBook', 'snapshotDelay', 6)
            if cacheLength == snapshotDelay:
                self.spawn(self.load_order_book, client, messageHash, symbol)
            storedOrderBook.cache.append(delta)
            return
        elif nonce >= deltaNonce:
            return
        self.handle_delta(storedOrderBook, delta)
        client.resolve(storedOrderBook, messageHash)

    def handle_delta(self, orderbook, delta):
        timestamp = self.safe_timestamp(delta, 'timestamp')
        orderbook['timestamp'] = timestamp
        orderbook['datetime'] = self.iso8601(timestamp)
        orderbook['nonce'] = self.safe_integer(delta, 'microtimestamp')
        bids = self.safe_value(delta, 'bids', [])
        asks = self.safe_value(delta, 'asks', [])
        storedBids = orderbook['bids']
        storedAsks = orderbook['asks']
        self.handle_bid_asks(storedBids, bids)
        self.handle_bid_asks(storedAsks, asks)

    def handle_bid_asks(self, bookSide, bidAsks):
        for i in range(0, len(bidAsks)):
            bidAsk = self.parse_bid_ask(bidAsks[i])
            bookSide.storeArray(bidAsk)

    def get_cache_index(self, orderbook, deltas):
        # we will consider it a fail
        firstElement = deltas[0]
        firstElementNonce = self.safe_integer(firstElement, 'microtimestamp')
        nonce = self.safe_integer(orderbook, 'nonce')
        if nonce < firstElementNonce:
            return -1
        for i in range(0, len(deltas)):
            delta = deltas[i]
            deltaNonce = self.safe_integer(delta, 'microtimestamp')
            if deltaNonce == nonce:
                return i + 1
        return len(deltas)

    async def watch_trades(self, symbol: str, since: Optional[int] = None, limit: Optional[int] = None, params={}):
        """
        get the list of most recent trades for a particular symbol
        :param str symbol: unified symbol of the market to fetch trades for
        :param int [since]: timestamp in ms of the earliest trade to fetch
        :param int [limit]: the maximum amount of trades to fetch
        :param dict [params]: extra parameters specific to the bitstamp api endpoint
        :returns dict[]: a list of `trade structures <https://github.com/ccxt/ccxt/wiki/Manual#public-trades>`
        """
        await self.load_markets()
        market = self.market(symbol)
        symbol = market['symbol']
        messageHash = 'trades:' + symbol
        url = self.urls['api']['ws']
        channel = 'live_trades_' + market['id']
        request = {
            'event': 'bts:subscribe',
            'data': {
                'channel': channel,
            },
        }
        message = self.extend(request, params)
        trades = await self.watch(url, messageHash, message, messageHash)
        if self.newUpdates:
            limit = trades.getLimit(symbol, limit)
        return self.filter_by_since_limit(trades, since, limit, 'timestamp', True)

    def parse_ws_trade(self, trade, market=None):
        #
        #     {
        #         "buy_order_id": 1211625836466176,
        #         "amount_str": "1.08000000",
        #         "timestamp": "1584642064",
        #         "microtimestamp": "1584642064685000",
        #         "id": 108637852,
        #         "amount": 1.08,
        #         "sell_order_id": 1211625840754689,
        #         "price_str": "6294.77",
        #         "type": 1,
        #         "price": 6294.77
        #     }
        #
        microtimestamp = self.safe_integer(trade, 'microtimestamp')
        id = self.safe_string(trade, 'id')
        timestamp = self.parse_to_int(microtimestamp / 1000)
        price = self.safe_string(trade, 'price')
        amount = self.safe_string(trade, 'amount')
        symbol = market['symbol']
        sideRaw = self.safe_integer(trade, 'type')
        side = 'buy' if (sideRaw == 0) else 'sell'
        return self.safe_trade({
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
            'cost': None,
            'fee': None,
        }, market)

    def handle_trade(self, client: Client, message):
        #
        #     {
        #         "data": {
        #             "buy_order_id": 1207733769326592,
        #             "amount_str": "0.14406384",
        #             "timestamp": "1583691851",
        #             "microtimestamp": "1583691851934000",
        #             "id": 106833903,
        #             "amount": 0.14406384,
        #             "sell_order_id": 1207733765476352,
        #             "price_str": "8302.92",
        #             "type": 0,
        #             "price": 8302.92
        #         },
        #         "event": "trade",
        #         "channel": "live_trades_btcusd"
        #     }
        #
        # the trade streams push raw trade information in real-time
        # each trade has a unique buyer and seller
        channel = self.safe_string(message, 'channel')
        parts = channel.split('_')
        marketId = self.safe_string(parts, 2)
        market = self.safe_market(marketId)
        symbol = market['symbol']
        messageHash = 'trades:' + symbol
        data = self.safe_value(message, 'data')
        trade = self.parse_ws_trade(data, market)
        tradesArray = self.safe_value(self.trades, symbol)
        if tradesArray is None:
            limit = self.safe_integer(self.options, 'tradesLimit', 1000)
            tradesArray = ArrayCache(limit)
            self.trades[symbol] = tradesArray
        tradesArray.append(trade)
        client.resolve(tradesArray, messageHash)

    async def watch_orders(self, symbol: Optional[str] = None, since: Optional[int] = None, limit: Optional[int] = None, params={}):
        """
        watches information on multiple orders made by the user
        :param str symbol: unified market symbol of the market orders were made in
        :param int [since]: the earliest time in ms to fetch orders for
        :param int [limit]: the maximum number of order structures to retrieve
        :param dict [params]: extra parameters specific to the bitstamp api endpoint
        :returns dict[]: a list of `order structures <https://github.com/ccxt/ccxt/wiki/Manual#order-structure>`
        """
        self.check_required_symbol('watchOrders', symbol)
        await self.load_markets()
        market = self.market(symbol)
        symbol = market['symbol']
        channel = 'private-my_orders'
        messageHash = channel + '_' + market['id']
        subscription = {
            'symbol': symbol,
            'limit': limit,
            'type': channel,
            'params': params,
        }
        orders = await self.subscribe_private(subscription, messageHash, params)
        if self.newUpdates:
            limit = orders.getLimit(symbol, limit)
        return self.filter_by_since_limit(orders, since, limit, 'timestamp', True)

    def handle_orders(self, client: Client, message):
        #
        # {
        #     "data":{
        #        "id":"1463471322288128",
        #        "id_str":"1463471322288128",
        #        "order_type":1,
        #        "datetime":"1646127778",
        #        "microtimestamp":"1646127777950000",
        #        "amount":0.05,
        #        "amount_str":"0.05000000",
        #        "price":1000,
        #        "price_str":"1000.00"
        #     },
        #     "channel":"private-my_orders_ltcusd-4848701",
        # }
        #
        channel = self.safe_string(message, 'channel')
        order = self.safe_value(message, 'data', {})
        limit = self.safe_integer(self.options, 'ordersLimit', 1000)
        if self.orders is None:
            self.orders = ArrayCacheBySymbolById(limit)
        stored = self.orders
        subscription = self.safe_value(client.subscriptions, channel)
        symbol = self.safe_string(subscription, 'symbol')
        market = self.market(symbol)
        parsed = self.parse_ws_order(order, market)
        stored.append(parsed)
        client.resolve(self.orders, channel)

    def parse_ws_order(self, order, market=None):
        #
        #   {
        #        "id":"1463471322288128",
        #        "id_str":"1463471322288128",
        #        "order_type":1,
        #        "datetime":"1646127778",
        #        "microtimestamp":"1646127777950000",
        #        "amount":0.05,
        #        "amount_str":"0.05000000",
        #        "price":1000,
        #        "price_str":"1000.00"
        #    }
        #
        id = self.safe_string(order, 'id_str')
        orderType = self.safe_string_lower(order, 'order_type')
        price = self.safe_string(order, 'price_str')
        amount = self.safe_string(order, 'amount_str')
        side = 'sell' if (orderType == '1') else 'buy'
        timestamp = self.safe_timestamp(order, 'datetime')
        market = self.safe_market(None, market)
        symbol = market['symbol']
        return self.safe_order({
            'info': order,
            'symbol': symbol,
            'id': id,
            'clientOrderId': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'type': None,
            'timeInForce': None,
            'postOnly': None,
            'side': side,
            'price': price,
            'stopPrice': None,
            'triggerPrice': None,
            'amount': amount,
            'cost': None,
            'average': None,
            'filled': None,
            'remaining': None,
            'status': None,
            'fee': None,
            'trades': None,
        }, market)

    def handle_order_book_subscription(self, client: Client, message):
        channel = self.safe_string(message, 'channel')
        parts = channel.split('_')
        marketId = self.safe_string(parts, 3)
        symbol = self.safe_symbol(marketId)
        self.orderbooks[symbol] = self.order_book()

    def handle_subscription_status(self, client: Client, message):
        #
        #     {
        #         "event": "bts:subscription_succeeded",
        #         "channel": "detail_order_book_btcusd",
        #         "data": {},
        #     }
        #     {
        #         "event": "bts:subscription_succeeded",
        #         "channel": "private-my_orders_ltcusd-4848701",
        #         "data": {}
        #     }
        #
        channel = self.safe_string(message, 'channel')
        if channel.find('order_book') > -1:
            self.handle_order_book_subscription(client, message)

    def handle_subject(self, client: Client, message):
        #
        #     {
        #         "data": {
        #             "timestamp": "1583656800",
        #             "microtimestamp": "1583656800237527",
        #             "bids": [
        #                 ["8732.02", "0.00002478", "1207590500704256"],
        #                 ["8729.62", "0.01600000", "1207590502350849"],
        #                 ["8727.22", "0.01800000", "1207590504296448"],
        #             ],
        #             "asks": [
        #                 ["8735.67", "2.00000000", "1207590693249024"],
        #                 ["8735.67", "0.01700000", "1207590693634048"],
        #                 ["8735.68", "1.53294500", "1207590692048896"],
        #             ],
        #         },
        #         "event": "data",
        #         "channel": "detail_order_book_btcusd"
        #     }
        #
        # private order
        #     {
        #         "data":{
        #         "id":"1463471322288128",
        #         "id_str":"1463471322288128",
        #         "order_type":1,
        #         "datetime":"1646127778",
        #         "microtimestamp":"1646127777950000",
        #         "amount":0.05,
        #         "amount_str":"0.05000000",
        #         "price":1000,
        #         "price_str":"1000.00"
        #         },
        #         "channel":"private-my_orders_ltcusd-4848701",
        #     }
        #
        channel = self.safe_string(message, 'channel')
        methods = {
            'live_trades': self.handle_trade,
            'diff_order_book': self.handle_order_book,
            'private-my_orders': self.handle_orders,
        }
        keys = list(methods.keys())
        for i in range(0, len(keys)):
            key = keys[i]
            if channel.find(key) > -1:
                method = methods[key]
                method(client, message)

    def handle_error_message(self, client: Client, message):
        # {
        #     "event": "bts:error",
        #     "channel": '',
        #     "data": {code: 4009, message: "Connection is unauthorized."}
        # }
        event = self.safe_string(message, 'event')
        if event == 'bts:error':
            feedback = self.id + ' ' + self.json(message)
            data = self.safe_value(message, 'data', {})
            code = self.safe_number(data, 'code')
            self.throw_exactly_matched_exception(self.exceptions['exact'], code, feedback)
        return message

    def handle_message(self, client: Client, message):
        if not self.handle_error_message(client, message):
            return
        #
        #     {
        #         "event": "bts:subscription_succeeded",
        #         "channel": "detail_order_book_btcusd",
        #         "data": {},
        #     }
        #
        #     {
        #         "data": {
        #             "timestamp": "1583656800",
        #             "microtimestamp": "1583656800237527",
        #             "bids": [
        #                 ["8732.02", "0.00002478", "1207590500704256"],
        #                 ["8729.62", "0.01600000", "1207590502350849"],
        #                 ["8727.22", "0.01800000", "1207590504296448"],
        #             ],
        #             "asks": [
        #                 ["8735.67", "2.00000000", "1207590693249024"],
        #                 ["8735.67", "0.01700000", "1207590693634048"],
        #                 ["8735.68", "1.53294500", "1207590692048896"],
        #             ],
        #         },
        #         "event": "data",
        #         "channel": "detail_order_book_btcusd"
        #     }
        #
        #     {
        #         "event": "bts:subscription_succeeded",
        #         "channel": "private-my_orders_ltcusd-4848701",
        #         "data": {}
        #     }
        #
        event = self.safe_string(message, 'event')
        if event == 'bts:subscription_succeeded':
            return self.handle_subscription_status(client, message)
        else:
            return self.handle_subject(client, message)

    async def authenticate(self, params={}):
        self.check_required_credentials()
        time = self.milliseconds()
        expiresIn = self.safe_integer(self.options, 'expiresIn')
        if (expiresIn is None) or (time > expiresIn):
            response = await self.privatePostWebsocketsToken(params)
            #
            # {
            #     "valid_sec":60,
            #     "token":"siPaT4m6VGQCdsDCVbLBemiphHQs552e",
            #     "user_id":4848701
            # }
            #
            sessionToken = self.safe_string(response, 'token')
            if sessionToken is not None:
                userId = self.safe_number(response, 'user_id')
                validity = self.safe_integer_product(response, 'valid_sec', 1000)
                self.options['expiresIn'] = self.sum(time, validity)
                self.options['userId'] = userId
                self.options['wsSessionToken'] = sessionToken
                return response

    async def subscribe_private(self, subscription, messageHash, params={}):
        url = self.urls['api']['ws']
        await self.authenticate()
        messageHash += '-' + self.options['userId']
        request = {
            'event': 'bts:subscribe',
            'data': {
                'channel': messageHash,
                'auth': self.options['wsSessionToken'],
            },
        }
        subscription['messageHash'] = messageHash
        return await self.watch(url, messageHash, self.extend(request, params), messageHash, subscription)
