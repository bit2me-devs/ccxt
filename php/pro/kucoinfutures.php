<?php

namespace ccxt\pro;

// PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
// https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

use Exception; // a common import
use ccxt\ExchangeError;
use React\Async;

class kucoinfutures extends \ccxt\async\kucoinfutures {

    public function describe() {
        return $this->deep_extend(parent::describe(), array(
            'has' => array(
                'ws' => true,
                'watchTicker' => true,
                'watchTrades' => true,
                'watchOrderBook' => true,
                'watchOrders' => true,
                'watchBalance' => true,
            ),
            'options' => array(
                'accountsByType' => array(
                    'swap' => 'future',
                    'cross' => 'margin',
                    // 'spot' => ,
                    // 'margin' => ,
                    // 'main' => ,
                    // 'funding' => ,
                    // 'future' => ,
                    // 'mining' => ,
                    // 'trade' => ,
                    // 'contract' => ,
                    // 'pool' => ,
                ),
                'tradesLimit' => 1000,
                'watchOrderBook' => array(
                    'snapshotDelay' => 20,
                    'snapshotMaxRetries' => 3,
                ),
                'watchTicker' => array(
                    'name' => 'contractMarket/tickerV2', // market/ticker
                ),
            ),
            'streaming' => array(
                // kucoin does not support built-in ws protocol-level ping-pong
                // instead it requires a custom json-based text ping-pong
                // https://docs.kucoin.com/#ping
                'ping' => array($this, 'ping'),
            ),
        ));
    }

    public function negotiate($privateChannel, $params = array ()) {
        $connectId = $privateChannel ? 'private' : 'public';
        $urls = $this->safe_value($this->options, 'urls', array());
        if (is_array($urls) && array_key_exists($connectId, $urls)) {
            return $urls[$connectId];
        }
        // we store an awaitable to the url
        // so that multiple calls don't asynchronously
        // fetch different $urls and overwrite each other
        $urls[$connectId] = $this->spawn(array($this, 'negotiate_helper'), $privateChannel, $params);
        $this->options['urls'] = $urls;
        return $urls[$connectId];
    }

    public function negotiate_helper($privateChannel, $params = array ()) {
        return Async\async(function () use ($privateChannel, $params) {
            $response = null;
            $connectId = $privateChannel ? 'private' : 'public';
            if ($privateChannel) {
                $response = Async\await($this->futuresPrivatePostBulletPrivate ($params));
                //
                //     {
                //         code => "200000",
                //         $data => {
                //             $instanceServers => array(
                //                 {
                //                     $pingInterval =>  50000,
                //                     $endpoint => "wss://push-private.kucoin.com/endpoint",
                //                     protocol => "websocket",
                //                     encrypt => true,
                //                     pingTimeout => 10000
                //                 }
                //             ),
                //             $token => "2neAiuYvAU61ZDXANAGAsiL4-iAExhsBXZxftpOeh_55i3Ysy2q2LEsEWU64mdzUOPusi34M_wGoSf7iNyEWJ1UQy47YbpY4zVdzilNP-Bj3iXzrjjGlWtiYB9J6i9GjsxUuhPw3BlrzazF6ghq4Lzf7scStOz3KkxjwpsOBCH4=.WNQmhZQeUKIkh97KYgU0Lg=="
                //         }
                //     }
                //
            } else {
                $response = Async\await($this->futuresPublicPostBulletPublic ($params));
            }
            $data = $this->safe_value($response, 'data', array());
            $instanceServers = $this->safe_value($data, 'instanceServers', array());
            $firstInstanceServer = $this->safe_value($instanceServers, 0);
            $pingInterval = $this->safe_integer($firstInstanceServer, 'pingInterval');
            $endpoint = $this->safe_string($firstInstanceServer, 'endpoint');
            $token = $this->safe_string($data, 'token');
            $result = $endpoint . '?' . $this->urlencode(array(
                'token' => $token,
                'privateChannel' => $privateChannel,
                'connectId' => $connectId,
            ));
            $client = $this->client($result);
            $client->keepAlive = $pingInterval;
            return $result;
        }) ();
    }

    public function request_id() {
        $requestId = $this->sum($this->safe_integer($this->options, 'requestId', 0), 1);
        $this->options['requestId'] = $requestId;
        return $requestId;
    }

    public function subscribe($url, $messageHash, $subscriptionHash, $subscription, $params = array ()) {
        return Async\async(function () use ($url, $messageHash, $subscriptionHash, $subscription, $params) {
            $requestId = (string) $this->request_id();
            $request = array(
                'id' => $requestId,
                'type' => 'subscribe',
                'topic' => $subscriptionHash,
                'response' => true,
            );
            $message = array_merge($request, $params);
            $subscriptionRequest = array(
                'id' => $requestId,
            );
            if ($subscription === null) {
                $subscription = $subscriptionRequest;
            } else {
                $subscription = array_merge($subscriptionRequest, $subscription);
            }
            return Async\await($this->watch($url, $messageHash, $message, $subscriptionHash, $subscription));
        }) ();
    }

    public function watch_ticker(string $symbol, $params = array ()) {
        return Async\async(function () use ($symbol, $params) {
            /**
             * watches a price ticker, a statistical calculation with the information calculated over the past 24 hours for a specific $market
             * @see https://docs.kucoin.com/futures/#get-real-time-$symbol-ticker-v2
             * @param {string} $symbol unified $symbol of the $market to fetch the ticker for
             * @param {array} [$params] extra parameters specific to the kucoinfutures api endpoint
             * @return {array} a {@link https://github.com/ccxt/ccxt/wiki/Manual#ticker-structure ticker structure}
             */
            Async\await($this->load_markets());
            $market = $this->market($symbol);
            $symbol = $market['symbol'];
            $url = Async\await($this->negotiate(false));
            $options = $this->safe_value($this->options, 'watchTicker', array());
            $channel = $this->safe_string($options, 'name', 'contractMarket/tickerV2');
            $topic = '/' . $channel . ':' . $market['id'];
            $messageHash = 'ticker:' . $symbol;
            return Async\await($this->subscribe($url, $messageHash, $topic, null, $params));
        }) ();
    }

    public function handle_ticker(Client $client, $message) {
        //
        // market/tickerV2
        //
        //    {
        //        type => 'message',
        //        topic => '/contractMarket/tickerV2:ADAUSDTM',
        //        subject => 'tickerV2',
        //        $data => {
        //            symbol => 'ADAUSDTM',
        //            sequence => 1668007800439,
        //            bestBidSize => 178,
        //            bestBidPrice => '0.35959',
        //            bestAskPrice => '0.35981',
        //            ts => '1668141430037124460',
        //            bestAskSize => 134
        //        }
        //    }
        //
        $data = $this->safe_value($message, 'data', array());
        $marketId = $this->safe_value($data, 'symbol');
        $market = $this->safe_market($marketId, null, '-');
        $ticker = $this->parse_ticker($data, $market);
        $this->tickers[$market['symbol']] = $ticker;
        $messageHash = 'ticker:' . $market['symbol'];
        $client->resolve ($ticker, $messageHash);
        return $message;
    }

    public function watch_trades(string $symbol, ?int $since = null, ?int $limit = null, $params = array ()) {
        return Async\async(function () use ($symbol, $since, $limit, $params) {
            /**
             * get the list of most recent $trades for a particular $symbol
             * @see https://docs.kucoin.com/futures/#execution-data
             * @param {string} $symbol unified $symbol of the $market to fetch $trades for
             * @param {int} [$since] timestamp in ms of the earliest trade to fetch
             * @param {int} [$limit] the maximum amount of $trades to fetch
             * @param {array} [$params] extra parameters specific to the kucoinfutures api endpoint
             * @return {array[]} a list of ~@link https://docs.ccxt.com/en/latest/manual.html?#public-$trades trade structures~
             */
            Async\await($this->load_markets());
            $url = Async\await($this->negotiate(false));
            $market = $this->market($symbol);
            $symbol = $market['symbol'];
            $topic = '/contractMarket/execution:' . $market['id'];
            $messageHash = 'trades:' . $symbol;
            $trades = Async\await($this->subscribe($url, $messageHash, $topic, null, $params));
            if ($this->newUpdates) {
                $limit = $trades->getLimit ($symbol, $limit);
            }
            return $this->filter_by_since_limit($trades, $since, $limit, 'timestamp', true);
        }) ();
    }

    public function handle_trade(Client $client, $message) {
        //
        //    {
        //        type => 'message',
        //        topic => '/contractMarket/execution:ADAUSDTM',
        //        subject => 'match',
        //        $data => {
        //            makerUserId => '62286a4d720edf0001e81961',
        //            $symbol => 'ADAUSDTM',
        //            sequence => 41320766,
        //            side => 'sell',
        //            size => 2,
        //            price => 0.35904,
        //            takerOrderId => '636dd9da9857ba00010cfa44',
        //            makerOrderId => '636dd9c8df149d0001e62bc8',
        //            takerUserId => '6180be22b6ab210001fa3371',
        //            tradeId => '636dd9da0000d400d477eca7',
        //            ts => 1668143578987357700
        //        }
        //    }
        //
        $data = $this->safe_value($message, 'data', array());
        $trade = $this->parse_trade($data);
        $symbol = $trade['symbol'];
        $trades = $this->safe_value($this->trades, $symbol);
        if ($trades === null) {
            $limit = $this->safe_integer($this->options, 'tradesLimit', 1000);
            $trades = new ArrayCache ($limit);
            $this->trades[$symbol] = $trades;
        }
        $trades->append ($trade);
        $messageHash = 'trades:' . $symbol;
        $client->resolve ($trades, $messageHash);
        return $message;
    }

    public function watch_order_book(string $symbol, ?int $limit = null, $params = array ()) {
        return Async\async(function () use ($symbol, $limit, $params) {
            /**
             * watches information on open orders with bid (buy) and ask (sell) prices, volumes and other data
             *   1. After receiving the websocket Level 2 data flow, cache the data.
             *   2. Initiate a REST request to get the snapshot data of Level 2 order book.
             *   3. Playback the cached Level 2 data flow.
             *   4. Apply the new Level 2 data flow to the local snapshot to ensure that the sequence of the new Level 2 update lines up with the sequence of the previous Level 2 data. Discard all the message prior to that sequence, and then playback the change to snapshot.
             *   5. Update the level2 full data based on sequence according to the size. If the price is 0, ignore the messages and update the sequence. If the size=0, update the sequence and remove the price of which the size is 0 out of level 2. For other cases, please update the price.
             *   6. If the sequence of the newly pushed message does not line up to the sequence of the last message, you could pull through REST Level 2 message request to get the updated messages. Please note that the difference between the start and end parameters cannot exceed 500.
             * @see https://docs.kucoin.com/futures/#level-2-$market-data
             * @param {string} $symbol unified $symbol of the $market to fetch the order book for
             * @param {int} [$limit] the maximum amount of order book entries to return
             * @param {array} [$params] extra parameters specific to the kucoinfutures api endpoint
             * @return {array} A dictionary of {@link https://github.com/ccxt/ccxt/wiki/Manual#order-book-structure order book structures} indexed by $market symbols
             */
            if ($limit !== null) {
                if (($limit !== 20) && ($limit !== 100)) {
                    throw new ExchangeError($this->id . " watchOrderBook 'limit' argument must be null, 20 or 100");
                }
            }
            Async\await($this->load_markets());
            $url = Async\await($this->negotiate(false));
            $market = $this->market($symbol);
            $symbol = $market['symbol'];
            $topic = '/contractMarket/level2:' . $market['id'];
            $messageHash = 'orderbook:' . $symbol;
            $subscription = array(
                'method' => array($this, 'handle_order_book_subscription'),
                'symbol' => $symbol,
                'limit' => $limit,
            );
            $orderbook = Async\await($this->subscribe($url, $messageHash, $topic, $subscription, $params));
            return $orderbook->limit ();
        }) ();
    }

    public function handle_delta($orderbook, $delta) {
        $orderbook['nonce'] = $this->safe_integer($delta, 'sequence');
        $timestamp = $this->safe_integer($delta, 'timestamp');
        $orderbook['timestamp'] = $timestamp;
        $orderbook['datetime'] = $this->iso8601($timestamp);
        $change = $this->safe_value($delta, 'change', array());
        $splitChange = explode(',', $change);
        $price = $this->safe_number($splitChange, 0);
        $side = $this->safe_string($splitChange, 1);
        $quantity = $this->safe_number($splitChange, 2);
        $type = ($side === 'buy') ? 'bids' : 'asks';
        $value = array( $price, $quantity );
        if ($type === 'bids') {
            $storedBids = $orderbook['bids'];
            $storedBids->storeArray ($value);
        } else {
            $storedAsks = $orderbook['asks'];
            $storedAsks->storeArray ($value);
        }
    }

    public function handle_deltas($bookside, $deltas) {
        for ($i = 0; $i < count($deltas); $i++) {
            $this->handle_delta($bookside, $deltas[$i]);
        }
    }

    public function handle_order_book(Client $client, $message) {
        //
        // initial snapshot is fetched with ccxt's fetchOrderBook
        // the feed does not include a snapshot, just the deltas
        //
        //    {
        //        type => 'message',
        //        $topic => '/contractMarket/level2:ADAUSDTM',
        //        subject => 'level2',
        //        $data => {
        //            sequence => 1668059586457,
        //            change => '0.34172,sell,456', // type, side, quantity
        //            timestamp => 1668573023223
        //        }
        //    }
        //
        $data = $this->safe_value($message, 'data');
        $topic = $this->safe_string($message, 'topic');
        $topicParts = explode(':', $topic);
        $marketId = $this->safe_string($topicParts, 1);
        $symbol = $this->safe_symbol($marketId, null, '-');
        $messageHash = 'orderbook:' . $symbol;
        $storedOrderBook = $this->orderbooks[$symbol];
        $nonce = $this->safe_integer($storedOrderBook, 'nonce');
        $deltaEnd = $this->safe_integer($data, 'sequence');
        if ($nonce === null) {
            $cacheLength = count($storedOrderBook->cache);
            $topic = $this->safe_string($message, 'topic');
            $subscription = $client->subscriptions[$topic];
            $limit = $this->safe_integer($subscription, 'limit');
            $snapshotDelay = $this->handle_option('watchOrderBook', 'snapshotDelay', 5);
            if ($cacheLength === $snapshotDelay) {
                $this->spawn(array($this, 'load_order_book'), $client, $messageHash, $symbol, $limit);
            }
            $storedOrderBook->cache[] = $data;
            return;
        } elseif ($nonce >= $deltaEnd) {
            return;
        }
        $this->handle_delta($storedOrderBook, $data);
        $client->resolve ($storedOrderBook, $messageHash);
    }

    public function get_cache_index($orderbook, $cache) {
        $firstDelta = $this->safe_value($cache, 0);
        $nonce = $this->safe_integer($orderbook, 'nonce');
        $firstDeltaStart = $this->safe_integer($firstDelta, 'sequence');
        if ($nonce < $firstDeltaStart - 1) {
            return -1;
        }
        for ($i = 0; $i < count($cache); $i++) {
            $delta = $cache[$i];
            $deltaStart = $this->safe_integer($delta, 'sequence');
            if ($nonce < $deltaStart - 1) {
                return $i;
            }
        }
        return count($cache);
    }

    public function handle_order_book_subscription(Client $client, $message, $subscription) {
        $symbol = $this->safe_string($subscription, 'symbol');
        $limit = $this->safe_integer($subscription, 'limit');
        $this->orderbooks[$symbol] = $this->order_book(array(), $limit);
        // moved snapshot initialization to handleOrderBook to fix
        // https://github.com/ccxt/ccxt/issues/6820
        // the general idea is to fetch the snapshot after the first delta
        // but not before, because otherwise we cannot synchronize the feed
    }

    public function handle_subscription_status(Client $client, $message) {
        //
        //     {
        //         $id => '1578090438322',
        //         type => 'ack'
        //     }
        //
        $id = $this->safe_string($message, 'id');
        $subscriptionsById = $this->index_by($client->subscriptions, 'id');
        $subscription = $this->safe_value($subscriptionsById, $id, array());
        $method = $this->safe_value($subscription, 'method');
        if ($method !== null) {
            $method($client, $message, $subscription);
        }
        return $message;
    }

    public function handle_system_status(Client $client, $message) {
        //
        // todo => answer the question whether handleSystemStatus should be renamed
        // and unified for any usage pattern that
        // involves system status and maintenance updates
        //
        //     {
        //         id => '1578090234088', // connectId
        //         type => 'welcome',
        //     }
        //
        return $message;
    }

    public function watch_orders(?string $symbol = null, ?int $since = null, ?int $limit = null, $params = array ()) {
        return Async\async(function () use ($symbol, $since, $limit, $params) {
            /**
             * watches information on multiple $orders made by the user
             * @see https://docs.kucoin.com/futures/#trade-$orders-according-to-the-$market
             * @param {string} $symbol unified $market $symbol of the $market $orders were made in
             * @param {int} [$since] the earliest time in ms to fetch $orders for
             * @param {int} [$limit] the maximum number of  orde structures to retrieve
             * @param {array} [$params] extra parameters specific to the kucoinfutures api endpoint
             * @return {array[]} a list of {@link https://github.com/ccxt/ccxt/wiki/Manual#order-structure order structures}
             */
            Async\await($this->load_markets());
            $url = Async\await($this->negotiate(true));
            $topic = '/contractMarket/tradeOrders';
            $request = array(
                'privateChannel' => true,
            );
            $messageHash = 'orders';
            if ($symbol !== null) {
                $market = $this->market($symbol);
                $symbol = $market['symbol'];
                $messageHash = $messageHash . ':' . $symbol;
            }
            $orders = Async\await($this->subscribe($url, $messageHash, $topic, null, array_merge($request, $params)));
            if ($this->newUpdates) {
                $limit = $orders->getLimit ($symbol, $limit);
            }
            return $this->filter_by_symbol_since_limit($orders, $symbol, $since, $limit, true);
        }) ();
    }

    public function parse_ws_order_status($status) {
        $statuses = array(
            'open' => 'open',
            'filled' => 'closed',
            'match' => 'open',
            'update' => 'open',
            'canceled' => 'canceled',
        );
        return $this->safe_string($statuses, $status, $status);
    }

    public function parse_ws_order($order, $market = null) {
        //
        //         'symbol' => 'XCAD-USDT',
        //     {
        //         'orderType' => 'limit',
        //         'side' => 'buy',
        //         'orderId' => '6249167327218b000135e749',
        //         'type' => 'canceled',
        //         'orderTime' => 1648957043065280224,
        //         'size' => '100.452',
        //         'filledSize' => '0',
        //         'price' => '2.9635',
        //         'clientOid' => 'buy-XCAD-USDT-1648957043010159',
        //         'remainSize' => '0',
        //         'status' => 'done',
        //         'ts' => 1648957054031001037
        //     }
        //
        $id = $this->safe_string($order, 'orderId');
        $clientOrderId = $this->safe_string($order, 'clientOid');
        $orderType = $this->safe_string_lower($order, 'orderType');
        $price = $this->safe_string($order, 'price');
        $filled = $this->safe_string($order, 'filledSize');
        $amount = $this->safe_string($order, 'size');
        $rawType = $this->safe_string($order, 'type');
        $status = $this->parse_ws_order_status($rawType);
        $timestamp = $this->safe_integer_product($order, 'orderTime', 0.000001);
        $marketId = $this->safe_string($order, 'symbol');
        $market = $this->safe_market($marketId, $market);
        $symbol = $market['symbol'];
        $side = $this->safe_string_lower($order, 'side');
        return $this->safe_order(array(
            'info' => $order,
            'symbol' => $symbol,
            'id' => $id,
            'clientOrderId' => $clientOrderId,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601($timestamp),
            'lastTradeTimestamp' => null,
            'type' => $orderType,
            'timeInForce' => null,
            'postOnly' => null,
            'side' => $side,
            'price' => $price,
            'stopPrice' => null,
            'amount' => $amount,
            'cost' => null,
            'average' => null,
            'filled' => $filled,
            'remaining' => null,
            'status' => $status,
            'fee' => null,
            'trades' => null,
        ), $market);
    }

    public function handle_order(Client $client, $message) {
        $messageHash = 'orders';
        $data = $this->safe_value($message, 'data');
        $parsed = $this->parse_ws_order($data);
        $symbol = $this->safe_string($parsed, 'symbol');
        $orderId = $this->safe_string($parsed, 'id');
        if ($symbol !== null) {
            if ($this->orders === null) {
                $limit = $this->safe_integer($this->options, 'ordersLimit', 1000);
                $this->orders = new ArrayCacheBySymbolById ($limit);
            }
            $cachedOrders = $this->orders;
            $orders = $this->safe_value($cachedOrders->hashmap, $symbol, array());
            $order = $this->safe_value($orders, $orderId);
            if ($order !== null) {
                // todo add others to calculate average etc
                $stopPrice = $this->safe_value($order, 'stopPrice');
                if ($stopPrice !== null) {
                    $parsed['stopPrice'] = $stopPrice;
                }
                if ($order['status'] === 'closed') {
                    $parsed['status'] = 'closed';
                }
            }
            $cachedOrders->append ($parsed);
            $client->resolve ($this->orders, $messageHash);
            $symbolSpecificMessageHash = $messageHash . ':' . $symbol;
            $client->resolve ($this->orders, $symbolSpecificMessageHash);
        }
    }

    public function watch_balance($params = array ()) {
        return Async\async(function () use ($params) {
            /**
             * watch balance and get the amount of funds available for trading or funds locked in orders
             * @see https://docs.kucoin.com/futures/#account-balance-events
             * @param {array} [$params] extra parameters specific to the kucoinfutures api endpoint
             * @return {array} a ~@link https://docs.ccxt.com/en/latest/manual.html?#balance-structure balance structure~
             */
            $url = Async\await($this->negotiate(true));
            $topic = '/contractAccount/wallet';
            $request = array(
                'privateChannel' => true,
            );
            $subscription = array(
                'method' => array($this, 'handle_balance_subscription'),
            );
            $messageHash = 'balance';
            return Async\await($this->subscribe($url, $messageHash, $topic, $subscription, array_merge($request, $params)));
        }) ();
    }

    public function handle_balance(Client $client, $message) {
        //
        //    {
        //        id => '6375553193027a0001f6566f',
        //        type => 'message',
        //        topic => '/contractAccount/wallet',
        //        userId => '613a896885d8660006151f01',
        //        channelType => 'private',
        //        subject => 'availableBalance.change',
        //        $data => {
        //            currency => 'USDT',
        //            holdBalance => '0.0000000000',
        //            availableBalance => '14.0350281903',
        //            timestamp => '1668633905657'
        //        }
        //    }
        //
        $data = $this->safe_value($message, 'data', array());
        $this->balance['info'] = $data;
        $currencyId = $this->safe_string($data, 'currency');
        $code = $this->safe_currency_code($currencyId);
        $account = $this->account();
        $account['free'] = $this->safe_string($data, 'availableBalance');
        $account['used'] = $this->safe_string($data, 'holdBalance');
        $this->balance[$code] = $account;
        $this->balance = $this->safe_balance($this->balance);
        $client->resolve ($this->balance, 'balance');
    }

    public function handle_balance_subscription(Client $client, $message, $subscription) {
        $this->spawn(array($this, 'fetch_balance_snapshot'), $client, $message);
    }

    public function fetch_balance_snapshot($client, $message) {
        return Async\async(function () use ($client, $message) {
            Async\await($this->load_markets());
            $this->check_required_credentials();
            $messageHash = 'balance';
            $selectedType = $this->safe_string_2($this->options, 'watchBalance', 'defaultType', 'swap'); // spot, margin, main, funding, future, mining, trade, contract, pool
            $params = array(
                'type' => $selectedType,
            );
            $snapshot = Async\await($this->fetch_balance($params));
            //
            //    {
            //        info => {
            //            $code => '200000',
            //            data => array(
            //                accountEquity => 0.0350281903,
            //                unrealisedPNL => 0,
            //                marginBalance => 0.0350281903,
            //                positionMargin => 0,
            //                orderMargin => 0,
            //                frozenFunds => 0,
            //                availableBalance => 0.0350281903,
            //                currency => 'USDT'
            //            }
            //        ),
            //        timestamp => null,
            //        datetime => null,
            //        USDT => array(
            //            free => 0.0350281903,
            //            used => 0,
            //            total => 0.0350281903
            //        ),
            //        free => array(
            //            USDT => 0.0350281903
            //        ),
            //        used => array(
            //            USDT => 0
            //        ),
            //        total => {
            //            USDT => 0.0350281903
            //        }
            //    }
            //
            $keys = is_array($snapshot) ? array_keys($snapshot) : array();
            for ($i = 0; $i < count($keys); $i++) {
                $code = $keys[$i];
                if ($code !== 'free' && $code !== 'used' && $code !== 'total' && $code !== 'timestamp' && $code !== 'datetime' && $code !== 'info') {
                    $this->balance[$code] = $snapshot[$code];
                }
            }
            $this->balance['info'] = $this->safe_value($snapshot, 'info', array());
            $client->resolve ($this->balance, $messageHash);
        }) ();
    }

    public function handle_subject(Client $client, $message) {
        //
        //    {
        //        type => 'message',
        //        topic => '/contractMarket/level2:ADAUSDTM',
        //        $subject => 'level2',
        //        data => {
        //            sequence => 1668059586457,
        //            change => '0.34172,sell,456', // type, side, quantity
        //            timestamp => 1668573023223
        //        }
        //    }
        //
        $subject = $this->safe_string($message, 'subject');
        $methods = array(
            'level2' => array($this, 'handle_order_book'),
            'tickerV2' => array($this, 'handle_ticker'),
            'availableBalance.change' => array($this, 'handle_balance'),
            'match' => array($this, 'handle_trade'),
            'orderChange' => array($this, 'handle_order'),
            'orderUpdated' => array($this, 'handle_order'),
        );
        $method = $this->safe_value($methods, $subject);
        if ($method === null) {
            return $message;
        } else {
            return $method($client, $message);
        }
    }

    public function ping($client) {
        // kucoin does not support built-in ws protocol-level ping-pong
        // instead it requires a custom json-based text ping-pong
        // https://docs.kucoin.com/#ping
        $id = (string) $this->request_id();
        return array(
            'id' => $id,
            'type' => 'ping',
        );
    }

    public function handle_pong(Client $client, $message) {
        // https://docs.kucoin.com/#ping
        $client->lastPong = $this->milliseconds();
        return $message;
    }

    public function handle_error_message(Client $client, $message) {
        //
        //    {
        //        "id" => "64d8732c856851144bded10d",
        //        "type" => "error",
        //        "code" => 401,
        //        "data" => "token is expired"
        //    }
        //
        $data = $this->safe_string($message, 'data', '');
        $this->handle_errors(null, null, $client->url, null, null, $data, $message, null, null);
    }

    public function handle_message(Client $client, $message) {
        $type = $this->safe_string($message, 'type');
        $methods = array(
            // 'heartbeat' => $this->handleHeartbeat,
            'welcome' => array($this, 'handle_system_status'),
            'ack' => array($this, 'handle_subscription_status'),
            'message' => array($this, 'handle_subject'),
            'pong' => array($this, 'handle_pong'),
            'error' => array($this, 'handle_error_message'),
        );
        $method = $this->safe_value($methods, $type);
        if ($method !== null) {
            return $method($client, $message);
        }
    }
}
