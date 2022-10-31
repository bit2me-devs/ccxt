# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.pro.base.exchange import Exchange
import ccxt.async_support
from ccxt.pro.base.cache import ArrayCache, ArrayCacheBySymbolById, ArrayCacheByTimestamp
import hashlib
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import NotSupported


class deribit(Exchange, ccxt.async_support.deribit):

    def describe(self):
        return self.deep_extend(super(deribit, self).describe(), {
            'has': {
                'ws': True,
                'watchBalance': True,
                'watchTicker': True,
                'watchTickers': False,
                'watchTrades': True,
                'watchMyTrades': True,
                'watchOrders': True,
                'watchOrderBook': True,
                'watchOHLCV': True,
            },
            'urls': {
                'test': {
                    'ws': 'wss://test.deribit.com/ws/api/v2',
                },
                'api': {
                    'ws': 'wss://www.deribit.com/ws/api/v2',
                },
            },
            'options': {
                'timeframes': {
                    '1m': 1,
                    '3m': 3,
                    '5m': 5,
                    '15m': 15,
                    '30m': 30,
                    '1h': 60,
                    '2h': 120,
                    '4h': 180,
                    '6h': 360,
                    '12h': 720,
                    '1d': '1D',
                },
                'currencies': ['BTC', 'ETH', 'SOL', 'USDC'],
            },
            'streaming': {
            },
            'exceptions': {
            },
        })

    def request_id(self):
        requestId = self.sum(self.safe_integer(self.options, 'requestId', 0), 1)
        self.options['requestId'] = requestId
        return requestId

    async def watch_balance(self, params={}):
        """
        see https://docs.deribit.com/#user-portfolio-currency
        query for balance and get the amount of funds available for trading or funds locked in orders
        :param dict params: extra parameters specific to the deribit api endpoint
        :returns dict: a `balance structure <https://docs.ccxt.com/en/latest/manual.html?#balance-structure>`
        """
        await self.authenticate(params)
        messageHash = 'balance'
        url = self.urls['api']['ws']
        currencies = self.safe_value(self.options, 'currencies', [])
        channels = []
        for i in range(0, len(currencies)):
            currencyCode = currencies[i]
            channels.append('user.portfolio.' + currencyCode)
        subscribe = {
            'jsonrpc': '2.0',
            'method': 'private/subscribe',
            'params': {
                'channels': channels,
            },
            'id': self.request_id(),
        }
        request = self.deep_extend(subscribe, params)
        return await self.watch(url, messageHash, request, messageHash, request)

    def handle_balance(self, client, message):
        #
        # subscription
        #     {
        #         jsonrpc: '2.0',
        #         method: 'subscription',
        #         params: {
        #             channel: 'user.portfolio.btc',
        #             data: {
        #                 total_pl: 0,
        #                 session_upl: 0,
        #                 session_rpl: 0,
        #                 projected_maintenance_margin: 0,
        #                 projected_initial_margin: 0,
        #                 projected_delta_total: 0,
        #                 portfolio_margining_enabled: False,
        #                 options_vega: 0,
        #                 options_value: 0,
        #                 options_theta: 0,
        #                 options_session_upl: 0,
        #                 options_session_rpl: 0,
        #                 options_pl: 0,
        #                 options_gamma: 0,
        #                 options_delta: 0,
        #                 margin_balance: 0.0015,
        #                 maintenance_margin: 0,
        #                 initial_margin: 0,
        #                 futures_session_upl: 0,
        #                 futures_session_rpl: 0,
        #                 futures_pl: 0,
        #                 fee_balance: 0,
        #                 estimated_liquidation_ratio_map: {},
        #                 estimated_liquidation_ratio: 0,
        #                 equity: 0.0015,
        #                 delta_total_map: {},
        #                 delta_total: 0,
        #                 currency: 'BTC',
        #                 balance: 0.0015,
        #                 available_withdrawal_funds: 0.0015,
        #                 available_funds: 0.0015
        #             }
        #         }
        #     }
        #
        params = self.safe_value(message, 'params', {})
        data = self.safe_value(params, 'data', {})
        currencyId = self.safe_string(data, 'currency')
        currencyCode = self.safe_currency_code(currencyId)
        balance = self.parse_balance(data)
        self.balance[currencyCode] = balance
        messageHash = 'balance'
        client.resolve(self.balance, messageHash)

    async def watch_ticker(self, symbol, params={}):
        """
        see https://docs.deribit.com/#ticker-instrument_name-interval
        watches a price ticker, a statistical calculation with the information for a specific market.
        :param str symbol: unified symbol of the market to fetch the ticker for
        :param dict params: extra parameters specific to the deribit api endpoint
        :param str|None params['interval']: specify aggregation and frequency of notifications. Possible values: 100ms, raw
        :returns dict: a `ticker structure <https://docs.ccxt.com/en/latest/manual.html#ticker-structure>`
        """
        market = self.market(symbol)
        url = self.urls['api']['ws']
        interval = self.safe_string(params, 'interval', '100ms')
        params = self.omit(params, 'interval')
        await self.load_markets()
        if interval == 'raw':
            await self.authenticate()
        channel = 'ticker.' + market['id'] + '.' + interval
        message = {
            'jsonrpc': '2.0',
            'method': 'public/subscribe',
            'params': {
                'channels': ['ticker.' + market['id'] + '.' + interval],
            },
            'id': self.request_id(),
        }
        request = self.deep_extend(message, params)
        return await self.watch(url, channel, request, channel, request)

    def handle_ticker(self, client, message):
        #
        #     {
        #         jsonrpc: '2.0',
        #         method: 'subscription',
        #         params: {
        #             channel: 'ticker.BTC_USDC-PERPETUAL.raw',
        #             data: {
        #                 timestamp: 1655393725041,
        #                 stats: [Object],
        #                 state: 'open',
        #                 settlement_price: 21729.5891,
        #                 open_interest: 164.501,
        #                 min_price: 20792.9376,
        #                 max_price: 21426.225,
        #                 mark_price: 21109.555,
        #                 last_price: 21132,
        #                 instrument_name: 'BTC_USDC-PERPETUAL',
        #                 index_price: 21122.3937,
        #                 funding_8h: -0.00022427,
        #                 estimated_delivery_price: 21122.3937,
        #                 current_funding: -0.00010782,
        #                 best_bid_price: 21106,
        #                 best_bid_amount: 1.143,
        #                 best_ask_price: 21113,
        #                 best_ask_amount: 0.327
        #             }
        #         }
        #     }
        #
        params = self.safe_value(message, 'params', {})
        data = self.safe_value(params, 'data', {})
        marketId = self.safe_string(data, 'instrument_name')
        symbol = self.safe_symbol(marketId)
        ticker = self.parse_ticker(data)
        messageHash = self.safe_string(params, 'channel')
        self.tickers[symbol] = ticker
        client.resolve(ticker, messageHash)

    async def watch_trades(self, symbol, since=None, limit=None, params={}):
        """
        get the list of most recent trades for a particular symbol
        see https://docs.deribit.com/#trades-instrument_name-interval
        :param str symbol: unified symbol of the market to fetch trades for
        :param int|None since: timestamp in ms of the earliest trade to fetch
        :param int|None limit: the maximum amount of trades to fetch
        :param dict params: extra parameters specific to the deribit api endpoint
        :param str|None params['interval']: specify aggregation and frequency of notifications. Possible values: 100ms, raw
        :returns [dict]: a list of `trade structures <https://docs.ccxt.com/en/latest/manual.html?#public-trades>`
        """
        await self.load_markets()
        market = self.market(symbol)
        url = self.urls['api']['ws']
        interval = self.safe_string(params, 'interval', '100ms')
        params = self.omit(params, 'interval')
        channel = 'trades.' + market['id'] + '.' + interval
        if interval == 'raw':
            await self.authenticate()
        message = {
            'jsonrpc': '2.0',
            'method': 'public/subscribe',
            'params': {
                'channels': [channel],
            },
            'id': self.request_id(),
        }
        request = self.deep_extend(message, params)
        trades = await self.watch(url, channel, request, channel, request)
        return self.filter_by_since_limit(trades, since, limit, 'timestamp', True)

    def handle_trades(self, client, message):
        #
        #     {
        #         "jsonrpc": "2.0",
        #         "method": "subscription",
        #         "params": {
        #             "channel": "trades.BTC_USDC-PERPETUAL.100ms",
        #             "data": [{
        #                 "trade_seq": 501899,
        #                 "trade_id": "USDC-2436803",
        #                 "timestamp": 1655397355998,
        #                 "tick_direction": 2,
        #                 "price": 21026,
        #                 "mark_price": 21019.9719,
        #                 "instrument_name": "BTC_USDC-PERPETUAL",
        #                 "index_price": 21031.7847,
        #                 "direction": "buy",
        #                 "amount": 0.049
        #             }]
        #         }
        #     }
        #
        params = self.safe_value(message, 'params', {})
        channel = self.safe_string(params, 'channel', '')
        parts = channel.split('.')
        marketId = self.safe_string(parts, 1)
        symbol = self.safe_symbol(marketId)
        market = self.safe_market(marketId)
        trades = self.safe_value(params, 'data', [])
        stored = self.safe_value(self.trades, symbol)
        if stored is None:
            limit = self.safe_integer(self.options, 'tradesLimit', 1000)
            stored = ArrayCache(limit)
            self.trades[symbol] = stored
        for i in range(0, len(trades)):
            trade = trades[i]
            parsed = self.parse_trade(trade, market)
            stored.append(parsed)
        self.trades[symbol] = stored
        client.resolve(self.trades[symbol], channel)

    async def watch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        """
        get the list of trades associated with the user
        see https://docs.deribit.com/#user-trades-instrument_name-interval
        :param str symbol: unified symbol of the market to fetch trades for. Use 'any' to watch all trades
        :param int|None since: timestamp in ms of the earliest trade to fetch
        :param int|None limit: the maximum amount of trades to fetch
        :param dict params: extra parameters specific to the deribit api endpoint
        :param str|None params['interval']: specify aggregation and frequency of notifications. Possible values: 100ms, raw
        :returns [dict]: a list of `trade structures <https://docs.ccxt.com/en/latest/manual.html?#public-trades>`
        """
        await self.authenticate(params)
        if symbol is not None:
            await self.load_markets()
            symbol = self.symbol(symbol)
        url = self.urls['api']['ws']
        interval = self.safe_string(params, 'interval', 'raw')
        params = self.omit(params, 'interval')
        channel = 'user.trades.any.any.' + interval
        message = {
            'jsonrpc': '2.0',
            'method': 'private/subscribe',
            'params': {
                'channels': [channel],
            },
            'id': self.request_id(),
        }
        request = self.deep_extend(message, params)
        trades = await self.watch(url, channel, request, channel, request)
        return self.filter_by_symbol_since_limit(trades, symbol, since, limit, True)

    def handle_my_trades(self, client, message):
        #
        #     {
        #         "jsonrpc": "2.0",
        #         "method": "subscription",
        #         "params": {
        #             "channel": "user.trades.any.any.raw",
        #             "data": [{
        #                 "trade_seq": 149546319,
        #                 "trade_id": "219381310",
        #                 "timestamp": 1655421193564,
        #                 "tick_direction": 0,
        #                 "state": "filled",
        #                 "self_trade": False,
        #                 "reduce_only": False,
        #                 "profit_loss": 0,
        #                 "price": 20236.5,
        #                 "post_only": False,
        #                 "order_type": "market",
        #                 "order_id": "46108941243",
        #                 "matching_id": null,
        #                 "mark_price": 20233.96,
        #                 "liquidity": "T",
        #                 "instrument_name": "BTC-PERPETUAL",
        #                 "index_price": 20253.31,
        #                 "fee_currency": "BTC",
        #                 "fee": 2.5e-7,
        #                 "direction": "buy",
        #                 "amount": 10
        #             }]
        #         }
        #     }
        #
        params = self.safe_value(message, 'params', {})
        channel = self.safe_string(params, 'channel', '')
        trades = self.safe_value(params, 'data', [])
        cachedTrades = self.myTrades
        if cachedTrades is None:
            limit = self.safe_integer(self.options, 'tradesLimit', 1000)
            cachedTrades = ArrayCacheBySymbolById(limit)
        parsed = self.parse_trades(trades)
        marketIds = {}
        for i in range(0, len(parsed)):
            trade = parsed[i]
            cachedTrades.append(trade)
            symbol = trade['symbol']
            marketIds[symbol] = True
        client.resolve(cachedTrades, channel)

    async def watch_order_book(self, symbol, limit=None, params={}):
        """
        see https://docs.deribit.com/#public-get_book_summary_by_instrument
        watches information on open orders with bid(buy) and ask(sell) prices, volumes and other data
        :param str symbol: unified symbol of the market to fetch the order book for
        :param int|None limit: the maximum amount of order book entries to return
        :param dict params: extra parameters specific to the deribit api endpoint
        :param str params['interval']: Frequency of notifications. Events will be aggregated over self interval. Possible values: 100ms, raw
        :returns dict: A dictionary of `order book structures <https://docs.ccxt.com/en/latest/manual.html#order-book-structure>` indexed by market symbols
        """
        await self.load_markets()
        market = self.market(symbol)
        url = self.urls['api']['ws']
        interval = self.safe_string(params, 'interval', '100ms')
        params = self.omit(params, 'interval')
        if interval == 'raw':
            await self.authenticate()
        channel = 'book.' + market['id'] + '.' + interval
        subscribe = {
            'jsonrpc': '2.0',
            'method': 'public/subscribe',
            'params': {
                'channels': [channel],
            },
            'id': self.request_id(),
        }
        request = self.deep_extend(subscribe, params)
        orderbook = await self.watch(url, channel, request, channel)
        return orderbook.limit(limit)

    def handle_order_book(self, client, message):
        #
        #  snapshot
        #     {
        #         "jsonrpc": "2.0",
        #         "method": "subscription",
        #         "params": {
        #             "channel": "book.BTC_USDC-PERPETUAL.raw",
        #             "data": {
        #                 "type": "snapshot",
        #                 "timestamp": 1655395057025,
        #                 "instrument_name": "BTC_USDC-PERPETUAL",
        #                 "change_id": 1550694837,
        #                 "bids": [
        #                     ["new", 20987, 0.487],
        #                     ["new", 20986, 0.238],
        #                 ],
        #                 "asks": [
        #                     ["new", 20999, 0.092],
        #                     ["new", 21000, 1.238],
        #                 ]
        #             }
        #         }
        #     }
        #
        #  change
        #     {
        #         "jsonrpc": "2.0",
        #         "method": "subscription",
        #         "params": {
        #             "channel": "book.BTC_USDC-PERPETUAL.raw",
        #             "data": {
        #                 "type": "change",
        #                 "timestamp": 1655395168086,
        #                 "prev_change_id": 1550724481,
        #                 "instrument_name": "BTC_USDC-PERPETUAL",
        #                 "change_id": 1550724483,
        #                 "bids": [
        #                     ["new", 20977, 0.109],
        #                     ["delete", 20975, 0]
        #                 ],
        #                 "asks": []
        #             }
        #         }
        #     }
        #
        params = self.safe_value(message, 'params', {})
        data = self.safe_value(params, 'data', {})
        channel = self.safe_string(params, 'channel')
        marketId = self.safe_string(data, 'instrument_name')
        symbol = self.safe_symbol(marketId)
        timestamp = self.safe_number(data, 'timestamp')
        storedOrderBook = self.safe_value(self.orderbooks, symbol)
        if storedOrderBook is None:
            storedOrderBook = self.counted_order_book()
        asks = self.safe_value(data, 'asks', [])
        bids = self.safe_value(data, 'bids', [])
        self.handle_deltas(storedOrderBook['asks'], asks)
        self.handle_deltas(storedOrderBook['bids'], bids)
        storedOrderBook['nonce'] = timestamp
        storedOrderBook['timestamp'] = timestamp
        storedOrderBook['datetime'] = self.iso8601(timestamp)
        storedOrderBook['symbol'] = symbol
        self.orderbooks[symbol] = storedOrderBook
        client.resolve(storedOrderBook, channel)

    def clean_order_book(self, data):
        bids = self.safe_value(data, 'bids', [])
        asks = self.safe_value(data, 'asks', [])
        cleanedBids = []
        for i in range(0, len(bids)):
            cleanedBids.append([bids[i][1], bids[i][2]])
        cleanedAsks = []
        for i in range(0, len(asks)):
            cleanedAsks.append([asks[i][1], asks[i][2]])
        data['bids'] = cleanedBids
        data['asks'] = cleanedAsks
        return data

    def handle_delta(self, bookside, delta):
        price = delta[1]
        amount = delta[2]
        if delta[0] == 'new' or delta[0] == 'change':
            bookside.store(price, amount, 1)
        elif delta[0] == 'delete':
            bookside.store(price, amount, 0)

    def handle_deltas(self, bookside, deltas):
        for i in range(0, len(deltas)):
            self.handle_delta(bookside, deltas[i])

    async def watch_orders(self, symbol=None, since=None, limit=None, params={}):
        """
        see https://docs.deribit.com/#user-orders-instrument_name-raw
        watches information on multiple orders made by the user
        :param str symbol: unified market symbol of the market orders were made in
        :param int|None since: the earliest time in ms to fetch orders for
        :param int|None limit: the maximum number of  orde structures to retrieve
        :param dict params: extra parameters specific to the deribit api endpoint
        :returns [dict]: a list of [order structures]{@link https://docs.ccxt.com/en/latest/manual.html#order-structure
        """
        await self.load_markets()
        await self.authenticate(params)
        if symbol is not None:
            symbol = self.symbol(symbol)
        url = self.urls['api']['ws']
        currency = self.safe_string(params, 'currency', 'any')
        interval = self.safe_string(params, 'interval', 'raw')
        kind = self.safe_string(params, 'kind', 'any')
        params = self.omit(params, 'interval', 'currency', 'kind')
        channel = 'user.orders.' + kind + '.' + currency + '.' + interval
        message = {
            'jsonrpc': '2.0',
            'method': 'private/subscribe',
            'params': {
                'channels': [channel],
            },
            'id': self.request_id(),
        }
        request = self.deep_extend(message, params)
        orders = await self.watch(url, channel, request, channel, request)
        if self.newUpdates:
            limit = orders.getLimit(symbol, limit)
        return self.filter_by_symbol_since_limit(orders, symbol, since, limit, True)

    def handle_orders(self, client, message):
        # Does not return a snapshot of current orders
        #
        #     {
        #         jsonrpc: '2.0',
        #         method: 'subscription',
        #         params: {
        #             channel: 'user.orders.any.any.raw',
        #             data: {
        #                 web: True,
        #                 time_in_force: 'good_til_cancelled',
        #                 replaced: False,
        #                 reduce_only: False,
        #                 profit_loss: 0,
        #                 price: 50000,
        #                 post_only: False,
        #                 order_type: 'limit',
        #                 order_state: 'open',
        #                 order_id: '46094375191',
        #                 max_show: 10,
        #                 last_update_timestamp: 1655401625037,
        #                 label: '',
        #                 is_liquidation: False,
        #                 instrument_name: 'BTC-PERPETUAL',
        #                 filled_amount: 0,
        #                 direction: 'sell',
        #                 creation_timestamp: 1655401625037,
        #                 commission: 0,
        #                 average_price: 0,
        #                 api: False,
        #                 amount: 10
        #             }
        #         }
        #     }
        #
        if self.orders is None:
            limit = self.safe_integer(self.options, 'ordersLimit', 1000)
            self.orders = ArrayCacheBySymbolById(limit)
        params = self.safe_value(message, 'params', {})
        channel = self.safe_string(params, 'channel', '')
        data = self.safe_value(params, 'data', {})
        orders = []
        if self.is_array(data):
            orders = self.parse_orders(data)
        else:
            order = self.parse_order(data)
            orders = [order]
        for i in range(0, len(orders)):
            self.orders.append(orders[i])
        client.resolve(self.orders, channel)

    async def watch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        """
        see https://docs.deribit.com/#chart-trades-instrument_name-resolution
        watches historical candlestick data containing the open, high, low, and close price, and the volume of a market
        :param str symbol: unified symbol of the market to fetch OHLCV data for
        :param str timeframe: the length of time each candle represents
        :param int|None since: timestamp in ms of the earliest candle to fetch
        :param int|None limit: the maximum amount of candles to fetch
        :param dict params: extra parameters specific to the deribit api endpoint
        :returns [[int]]: A list of candles ordered as timestamp, open, high, low, close, volume
        """
        await self.load_markets()
        market = self.market(symbol)
        url = self.urls['api']['ws']
        timeframes = self.safe_value(self.options, 'timeframes', {})
        interval = self.safe_string(timeframes, timeframe)
        if interval is None:
            raise NotSupported(self.id + ' self interval is not supported, please provide one of the supported timeframes')
        channel = 'chart.trades.' + market['id'] + '.' + interval
        message = {
            'jsonrpc': '2.0',
            'method': 'public/subscribe',
            'params': {
                'channels': [channel],
            },
            'id': self.request_id(),
        }
        request = self.deep_extend(message, params)
        ohlcv = await self.watch(url, channel, request, channel, request)
        if self.newUpdates:
            limit = ohlcv.getLimit(market['symbol'], limit)
        return self.filter_by_since_limit(ohlcv, since, limit, 0, True)

    def handle_ohlcv(self, client, message):
        #
        #     {
        #         jsonrpc: '2.0',
        #         method: 'subscription',
        #         params: {
        #             channel: 'chart.trades.BTC_USDC-PERPETUAL.1',
        #             data: {
        #                 volume: 0,
        #                 tick: 1655403420000,
        #                 open: 20951,
        #                 low: 20951,
        #                 high: 20951,
        #                 cost: 0,
        #                 close: 20951
        #             }
        #         }
        #     }
        #
        params = self.safe_value(message, 'params', {})
        channel = self.safe_string(params, 'channel', '')
        parts = channel.split('.')
        marketId = self.safe_string(parts, 2)
        symbol = self.safe_symbol(marketId)
        ohlcv = self.safe_value(params, 'data', {})
        parsed = [
            self.safe_number(ohlcv, 'tick'),
            self.safe_number(ohlcv, 'open'),
            self.safe_number(ohlcv, 'high'),
            self.safe_number(ohlcv, 'low'),
            self.safe_number(ohlcv, 'close'),
            self.safe_number(ohlcv, 'volume'),
        ]
        stored = self.safe_value(self.ohlcvs, symbol)
        if stored is None:
            limit = self.safe_integer(self.options, 'OHLCVLimit', 1000)
            stored = ArrayCacheByTimestamp(limit)
        stored.append(parsed)
        self.ohlcvs[symbol] = stored
        client.resolve(stored, channel)

    def handle_message(self, client, message):
        #
        # error
        #     {
        #         "jsonrpc": "2.0",
        #         "id": 1,
        #         "error": {
        #             "message": "Invalid params",
        #             "data": {
        #                 "reason": "invalid format",
        #                 "param": "nonce"
        #             },
        #             "code": -32602
        #         },
        #         "usIn": "1655391709417993",
        #         "usOut": "1655391709418049",
        #         "usDiff": 56,
        #         "testnet": False
        #     }
        #
        # subscribe
        #     {
        #         jsonrpc: '2.0',
        #         id: 2,
        #         result: ['ticker.BTC_USDC-PERPETUAL.raw'],
        #         usIn: '1655393625889396',
        #         usOut: '1655393625889518',
        #         usDiff: 122,
        #         testnet: False
        #     }
        #
        # notification
        #     {
        #         jsonrpc: '2.0',
        #         method: 'subscription',
        #         params: {
        #             channel: 'ticker.BTC_USDC-PERPETUAL.raw',
        #             data: {
        #                 timestamp: 1655393724752,
        #                 stats: [Object],
        #                 state: 'open',
        #                 settlement_price: 21729.5891,
        #                 open_interest: 164.501,
        #                 min_price: 20792.9001,
        #                 max_price: 21426.1864,
        #                 mark_price: 21109.4757,
        #                 last_price: 21132,
        #                 instrument_name: 'BTC_USDC-PERPETUAL',
        #                 index_price: 21122.3937,
        #                 funding_8h: -0.00022427,
        #                 estimated_delivery_price: 21122.3937,
        #                 current_funding: -0.00011158,
        #                 best_bid_price: 21106,
        #                 best_bid_amount: 1.143,
        #                 best_ask_price: 21113,
        #                 best_ask_amount: 0.402
        #             }
        #         }
        #     }
        #
        error = self.safe_value(message, 'error')
        if error is not None:
            raise ExchangeError(self.id + ' ' + self.json(error))
        params = self.safe_value(message, 'params')
        channel = self.safe_string(params, 'channel')
        if channel is not None:
            parts = channel.split('.')
            channelId = self.safe_string(parts, 0)
            userHandlers = {
                'trades': self.handle_my_trades,
                'portfolio': self.handle_balance,
                'orders': self.handle_orders,
            }
            handlers = {
                'ticker': self.handle_ticker,
                'book': self.handle_order_book,
                'trades': self.handle_trades,
                'chart': self.handle_ohlcv,
                'user': self.safe_value(userHandlers, self.safe_string(parts, 1)),
            }
            handler = self.safe_value(handlers, channelId)
            if handler is not None:
                return handler(client, message)
            raise NotSupported(self.id + ' no handler found for self message ' + self.json(message))
        result = self.safe_value(message, 'result', {})
        accessToken = self.safe_string(result, 'access_token')
        if accessToken is not None:
            return self.handle_authentication_message(client, message)
        return message

    def handle_authentication_message(self, client, message):
        #
        #     {
        #         jsonrpc: '2.0',
        #         id: 1,
        #         result: {
        #             token_type: 'bearer',
        #             scope: 'account:read_write block_trade:read_write connection custody:read_write mainaccount name:ccxt trade:read_write wallet:read_write',
        #             refresh_token: '1686927372328.1EzFBRmt.logRQWXkPA1oE_Tk0gRsls9Hau7YN6a321XUBnxvR4x6cryhbkKcniUJU-czA8_zKXrqQGpQmfoDwhLIjIsWCvRuu6otbg-LKWlrtTX1GQqLcPaTTHAdZGTMV-HM8HiS03QBd9MIXWRfF53sKj2hdR9nZPZ6MH1XrkpAZPB_peuEEB9wlcc3elzWEZFtCmiy1fnQ8TPHwAJMt3nuUmEcMLt_-F554qrsg_-I66D9xMiifJj4dBemdPfV_PkGPRIwIoKlxDjyv2-xfCw-4eKyo6Hu1m2h6gT1DPOTxSXcBgfBQjpi-_uY3iAIj7U6xjC46PHthEdquhEuCTZl7UfCRZSAWwZA',
        #             expires_in: 31536000,
        #             access_token: '1686923272328.1CkwEx-u.qHradpIulmuoeboKMEi8PkQ1_4DF8yFE2zywBTtkD32sruVC53b1HwL5OWRuh2nYAndXff4xuXIMRkkEfMAFCeq24prihxxinoS8DDVkKBxedGx4CUPJFeXjmh7wuRGqQOLg1plXOpbF3fwF2KPEkAuETwcpcVY6K9HUVjutNRfxFe2TR7CvuS9x8TATvoPeu7H1ezYl-LkKSaRifdTXuwituXgp4oDbPRyQLniEBWuYF9rY7qbABxuOJlXI1VZ63u7Bh0mGWei-KeVeqHGNpy6OgrFRPXPxa9_U7vaxCyHW3zZ9959TQ1QUMLWtUX-NLBEv3BT5eCieW9HORYIOKfsgkpd3'
        #         },
        #         usIn: '1655391872327712',
        #         usOut: '1655391872328515',
        #         usDiff: 803,
        #         testnet: False
        #     }
        #
        future = self.safe_value(client.futures, 'authenticated')
        if future is not None:
            future.resolve(True)
        return message

    async def authenticate(self, params={}):
        url = self.urls['api']['ws']
        client = self.client(url)
        time = self.milliseconds()
        timeString = self.number_to_string(time)
        nonce = timeString
        messageHash = 'authenticated'
        future = client.future('authenticated')
        authenticated = self.safe_value(client.subscriptions, messageHash)
        if authenticated is None:
            self.check_required_credentials()
            requestId = self.request_id()
            signature = self.hmac(self.encode(timeString + '\n' + nonce + '\n'), self.encode(self.secret), hashlib.sha256)
            request = {
                'jsonrpc': '2.0',
                'id': requestId,
                'method': 'public/auth',
                'params': {
                    'grant_type': 'client_signature',
                    'client_id': self.apiKey,
                    'timestamp': time,
                    'signature': signature,
                    'nonce': nonce,
                    'data': '',
                },
            }
            self.spawn(self.watch, url, messageHash, self.extend(request, params), messageHash)
        return await future
