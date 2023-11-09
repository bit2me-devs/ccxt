<?php

namespace ccxt\pro;

// PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
// https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

use Exception; // a common import
use ccxt\ExchangeError;
use React\Async;

class gemini extends \ccxt\async\gemini {

    public function describe() {
        return $this->deep_extend(parent::describe(), array(
            'has' => array(
                'ws' => true,
                'watchBalance' => false,
                'watchTicker' => false,
                'watchTickers' => false,
                'watchTrades' => true,
                'watchMyTrades' => false,
                'watchOrders' => true,
                'watchOrderBook' => true,
                'watchOHLCV' => true,
            ),
            'hostname' => 'api.gemini.com',
            'urls' => array(
                'api' => array(
                    'ws' => 'wss://api.gemini.com',
                ),
                'test' => array(
                    'ws' => 'wss://api.sandbox.gemini.com',
                ),
            ),
        ));
    }

    public function watch_trades(string $symbol, ?int $since = null, ?int $limit = null, $params = array ()) {
        return Async\async(function () use ($symbol, $since, $limit, $params) {
            /**
             * watch the list of most recent $trades for a particular $symbol
             * @see https://docs.gemini.com/websocket-api/#$market-data-version-2
             * @param {string} $symbol unified $symbol of the $market to fetch $trades for
             * @param {int} [$since] timestamp in ms of the earliest trade to fetch
             * @param {int} [$limit] the maximum amount of $trades to fetch
             * @param {array} [$params] extra parameters specific to the gemini api endpoint
             * @return {array[]} a list of {@link https://github.com/ccxt/ccxt/wiki/Manual#public-$trades trade structures}
             */
            Async\await($this->load_markets());
            $market = $this->market($symbol);
            $messageHash = 'trades:' . $market['symbol'];
            $marketId = $market['id'];
            $request = array(
                'type' => 'subscribe',
                'subscriptions' => array(
                    array(
                        'name' => 'l2',
                        'symbols' => array(
                            strtoupper($marketId),
                        ),
                    ),
                ),
            );
            $subscribeHash = 'l2:' . $market['symbol'];
            $url = $this->urls['api']['ws'] . '/v2/marketdata';
            $trades = Async\await($this->watch($url, $messageHash, $request, $subscribeHash));
            if ($this->newUpdates) {
                $limit = $trades->getLimit ($market['symbol'], $limit);
            }
            return $this->filter_by_since_limit($trades, $since, $limit, 'timestamp', true);
        }) ();
    }

    public function parse_ws_trade($trade, $market = null) {
        //
        //     {
        //         "type" => "trade",
        //         "symbol" => "BTCUSD",
        //         "event_id" => 122258166738,
        //         "timestamp" => 1655330221424,
        //         "price" => "22269.14",
        //         "quantity" => "0.00004473",
        //         "side" => "buy"
        //     }
        //
        $timestamp = $this->safe_integer($trade, 'timestamp');
        $id = $this->safe_string($trade, 'event_id');
        $priceString = $this->safe_string($trade, 'price');
        $amountString = $this->safe_string($trade, 'quantity');
        $side = $this->safe_string_lower($trade, 'side');
        $marketId = $this->safe_string_lower($trade, 'symbol');
        $symbol = $this->safe_symbol($marketId, $market);
        return $this->safe_trade(array(
            'id' => $id,
            'order' => null,
            'info' => $trade,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601($timestamp),
            'symbol' => $symbol,
            'type' => null,
            'side' => $side,
            'takerOrMaker' => null,
            'price' => $priceString,
            'cost' => null,
            'amount' => $amountString,
            'fee' => null,
        ), $market);
    }

    public function handle_trade(Client $client, $message) {
        //
        //     {
        //         "type" => "trade",
        //         "symbol" => "BTCUSD",
        //         "event_id" => 122278173770,
        //         "timestamp" => 1655335880981,
        //         "price" => "22530.80",
        //         "quantity" => "0.04",
        //         "side" => "buy"
        //     }
        //
        $trade = $this->parse_ws_trade($message);
        $symbol = $trade['symbol'];
        $tradesLimit = $this->safe_integer($this->options, 'tradesLimit', 1000);
        $stored = $this->safe_value($this->trades, $symbol);
        if ($stored === null) {
            $stored = new ArrayCache ($tradesLimit);
            $this->trades[$symbol] = $stored;
        }
        $stored->append ($trade);
        $messageHash = 'trades:' . $symbol;
        $client->resolve ($stored, $messageHash);
    }

    public function handle_trades(Client $client, $message) {
        //
        //     {
        //         "type" => "l2_updates",
        //         "symbol" => "BTCUSD",
        //         "changes" => array(
        //             array( "buy", '22252.37', "0.02" ),
        //             array( "buy", '22251.61', "0.04" ),
        //             array( "buy", '22251.60', "0.04" ),
        //             // some asks
        //         ),
        //         "trades" => array(
        //             array( type => 'trade', $symbol => 'BTCUSD', event_id => 122258166738, timestamp => 1655330221424, price => '22269.14', quantity => "0.00004473", side => "buy" ),
        //             array( type => 'trade', $symbol => 'BTCUSD', event_id => 122258141090, timestamp => 1655330213216, price => '22250.00', quantity => "0.00704098", side => "buy" ),
        //             array( type => 'trade', $symbol => 'BTCUSD', event_id => 122258118291, timestamp => 1655330206753, price => '22250.00', quantity => "0.03", side => "buy" ),
        //         ),
        //         "auction_events" => array(
        //             array(
        //                 "type" => "auction_result",
        //                 "symbol" => "BTCUSD",
        //                 "time_ms" => 1655323200000,
        //                 "result" => "failure",
        //                 "highest_bid_price" => "21590.88",
        //                 "lowest_ask_price" => "21602.30",
        //                 "collar_price" => "21634.73"
        //             ),
        //             array(
        //                 "type" => "auction_indicative",
        //                 "symbol" => "BTCUSD",
        //                 "time_ms" => 1655323185000,
        //                 "result" => "failure",
        //                 "highest_bid_price" => "21661.90",
        //                 "lowest_ask_price" => "21663.79",
        //                 "collar_price" => "21662.845"
        //             ),
        //         )
        //     }
        //
        $marketId = $this->safe_string_lower($message, 'symbol');
        $market = $this->safe_market($marketId);
        $trades = $this->safe_value($message, 'trades');
        if ($trades !== null) {
            $symbol = $market['symbol'];
            $tradesLimit = $this->safe_integer($this->options, 'tradesLimit', 1000);
            $stored = $this->safe_value($this->trades, $symbol);
            if ($stored === null) {
                $stored = new ArrayCache ($tradesLimit);
                $this->trades[$symbol] = $stored;
            }
            for ($i = 0; $i < count($trades); $i++) {
                $trade = $this->parse_ws_trade($trades[$i], $market);
                $stored->append ($trade);
            }
            $messageHash = 'trades:' . $symbol;
            $client->resolve ($stored, $messageHash);
        }
    }

    public function watch_ohlcv(string $symbol, $timeframe = '1m', ?int $since = null, ?int $limit = null, $params = array ()) {
        return Async\async(function () use ($symbol, $timeframe, $since, $limit, $params) {
            /**
             * watches historical candlestick data containing the open, high, low, and close price, and the volume of a $market
             * @see https://docs.gemini.com/websocket-api/#candles-data-feed
             * @param {string} $symbol unified $symbol of the $market to fetch OHLCV data for
             * @param {string} $timeframe the length of time each candle represents
             * @param {int} [$since] timestamp in ms of the earliest candle to fetch
             * @param {int} [$limit] the maximum amount of candles to fetch
             * @param {array} [$params] extra parameters specific to the gemini api endpoint
             * @return {int[][]} A list of candles ordered, open, high, low, close, volume
             */
            Async\await($this->load_markets());
            $market = $this->market($symbol);
            $timeframeId = $this->safe_string($this->timeframes, $timeframe, $timeframe);
            $request = array(
                'type' => 'subscribe',
                'subscriptions' => [
                    array(
                        'name' => 'candles_' . $timeframeId,
                        'symbols' => [
                            strtoupper($market['id']),
                        ],
                    ),
                ],
            );
            $messageHash = 'ohlcv:' . $market['symbol'] . ':' . $timeframeId;
            $url = $this->urls['api']['ws'] . '/v2/marketdata';
            $ohlcv = Async\await($this->watch($url, $messageHash, $request, $messageHash));
            if ($this->newUpdates) {
                $limit = $ohlcv->getLimit ($symbol, $limit);
            }
            return $this->filter_by_since_limit($ohlcv, $since, $limit, 0, true);
        }) ();
    }

    public function handle_ohlcv(Client $client, $message) {
        //
        //     {
        //         "type" => "candles_15m_updates",
        //         "symbol" => "BTCUSD",
        //         "changes" => array(
        //             array(
        //                 1561054500000,
        //                 9350.18,
        //                 9358.35,
        //                 9350.18,
        //                 9355.51,
        //                 2.07
        //             ),
        //             array(
        //                 1561053600000,
        //                 9357.33,
        //                 9357.33,
        //                 9350.18,
        //                 9350.18,
        //                 1.5900161
        //             )
        //             ...
        //         )
        //     }
        //
        $type = $this->safe_string($message, 'type', '');
        $timeframeId = mb_substr($type, 8);
        $timeframeEndIndex = mb_strpos($timeframeId, '_');
        $timeframeId = mb_substr($timeframeId, 0, $timeframeEndIndex - 0);
        $marketId = strtolower($this->safe_string($message, 'symbol', ''));
        $market = $this->safe_market($marketId);
        $symbol = $this->safe_symbol($marketId, $market);
        $changes = $this->safe_value($message, 'changes', array());
        $timeframe = $this->find_timeframe($timeframeId);
        $ohlcvsBySymbol = $this->safe_value($this->ohlcvs, $symbol);
        if ($ohlcvsBySymbol === null) {
            $this->ohlcvs[$symbol] = array();
        }
        $stored = $this->safe_value($this->ohlcvs[$symbol], $timeframe);
        if ($stored === null) {
            $limit = $this->safe_integer($this->options, 'OHLCVLimit', 1000);
            $stored = new ArrayCacheByTimestamp ($limit);
            $this->ohlcvs[$symbol][$timeframe] = $stored;
        }
        $changesLength = count($changes);
        // reverse order of array to store candles in ascending order
        for ($i = 0; $i < $changesLength; $i++) {
            $index = $changesLength - $i - 1;
            $parsed = $this->parse_ohlcv($changes[$index], $market);
            $stored->append ($parsed);
        }
        $messageHash = 'ohlcv:' . $symbol . ':' . $timeframeId;
        $client->resolve ($stored, $messageHash);
        return $message;
    }

    public function watch_order_book(string $symbol, ?int $limit = null, $params = array ()) {
        return Async\async(function () use ($symbol, $limit, $params) {
            /**
             * watches information on open orders with bid (buy) and ask (sell) prices, volumes and other data
             * @see https://docs.gemini.com/websocket-api/#$market-data-version-2
             * @param {string} $symbol unified $symbol of the $market to fetch the order book for
             * @param {int} [$limit] the maximum amount of order book entries to return
             * @param {array} [$params] extra parameters specific to the gemini api endpoint
             * @return {array} A dictionary of {@link https://github.com/ccxt/ccxt/wiki/Manual#order-book-structure order book structures} indexed by $market symbols
             */
            Async\await($this->load_markets());
            $market = $this->market($symbol);
            $messageHash = 'orderbook:' . $market['symbol'];
            $marketId = $market['id'];
            $request = array(
                'type' => 'subscribe',
                'subscriptions' => array(
                    array(
                        'name' => 'l2',
                        'symbols' => array(
                            strtoupper($marketId),
                        ),
                    ),
                ),
            );
            $subscribeHash = 'l2:' . $market['symbol'];
            $url = $this->urls['api']['ws'] . '/v2/marketdata';
            $orderbook = Async\await($this->watch($url, $messageHash, $request, $subscribeHash));
            return $orderbook->limit ();
        }) ();
    }

    public function handle_order_book(Client $client, $message) {
        $changes = $this->safe_value($message, 'changes', array());
        $marketId = $this->safe_string_lower($message, 'symbol');
        $market = $this->safe_market($marketId);
        $symbol = $market['symbol'];
        $messageHash = 'orderbook:' . $symbol;
        $orderbook = $this->safe_value($this->orderbooks, $symbol);
        if ($orderbook === null) {
            $orderbook = $this->order_book();
        }
        for ($i = 0; $i < count($changes); $i++) {
            $delta = $changes[$i];
            $price = $this->safe_number($delta, 1);
            $size = $this->safe_number($delta, 2);
            $side = ($delta[0] === 'buy') ? 'bids' : 'asks';
            $bookside = $orderbook[$side];
            $bookside->store ($price, $size);
            $orderbook[$side] = $bookside;
        }
        $orderbook['symbol'] = $symbol;
        $this->orderbooks[$symbol] = $orderbook;
        $client->resolve ($orderbook, $messageHash);
    }

    public function handle_l2_updates(Client $client, $message) {
        //
        //     {
        //         "type" => "l2_updates",
        //         "symbol" => "BTCUSD",
        //         "changes" => array(
        //             array( "buy", '22252.37', "0.02" ),
        //             array( "buy", '22251.61', "0.04" ),
        //             array( "buy", '22251.60', "0.04" ),
        //             // some asks
        //         ),
        //         "trades" => array(
        //             array( type => 'trade', symbol => 'BTCUSD', event_id => 122258166738, timestamp => 1655330221424, price => '22269.14', quantity => "0.00004473", side => "buy" ),
        //             array( type => 'trade', symbol => 'BTCUSD', event_id => 122258141090, timestamp => 1655330213216, price => '22250.00', quantity => "0.00704098", side => "buy" ),
        //             array( type => 'trade', symbol => 'BTCUSD', event_id => 122258118291, timestamp => 1655330206753, price => '22250.00', quantity => "0.03", side => "buy" ),
        //         ),
        //         "auction_events" => array(
        //             array(
        //                 "type" => "auction_result",
        //                 "symbol" => "BTCUSD",
        //                 "time_ms" => 1655323200000,
        //                 "result" => "failure",
        //                 "highest_bid_price" => "21590.88",
        //                 "lowest_ask_price" => "21602.30",
        //                 "collar_price" => "21634.73"
        //             ),
        //             array(
        //                 "type" => "auction_indicative",
        //                 "symbol" => "BTCUSD",
        //                 "time_ms" => 1655323185000,
        //                 "result" => "failure",
        //                 "highest_bid_price" => "21661.90",
        //                 "lowest_ask_price" => "21663.79",
        //                 "collar_price" => "21662.845"
        //             ),
        //         )
        //     }
        //
        $this->handle_order_book($client, $message);
        $this->handle_trades($client, $message);
    }

    public function watch_orders(?string $symbol = null, ?int $since = null, ?int $limit = null, $params = array ()) {
        return Async\async(function () use ($symbol, $since, $limit, $params) {
            /**
             * watches information on multiple $orders made by the user
             * @see https://docs.gemini.com/websocket-api/#order-events
             * @param {string} $symbol unified $market $symbol of the $market $orders were made in
             * @param {int} [$since] the earliest time in ms to fetch $orders for
             * @param {int} [$limit] the maximum number of  orde structures to retrieve
             * @param {array} [$params] extra parameters specific to the gemini api endpoint
             * @return {array[]} a list of {@link https://github.com/ccxt/ccxt/wiki/Manual#order-structure order structures}
             */
            $url = $this->urls['api']['ws'] . '/v1/order/events?eventTypeFilter=initial&eventTypeFilter=accepted&eventTypeFilter=rejected&eventTypeFilter=fill&eventTypeFilter=cancelled&eventTypeFilter=booked';
            Async\await($this->load_markets());
            $authParams = array(
                'url' => $url,
            );
            Async\await($this->authenticate($authParams));
            if ($symbol !== null) {
                $market = $this->market($symbol);
                $symbol = $market['symbol'];
            }
            $messageHash = 'orders';
            $orders = Async\await($this->watch($url, $messageHash, null, $messageHash));
            if ($this->newUpdates) {
                $limit = $orders->getLimit ($symbol, $limit);
            }
            return $this->filter_by_symbol_since_limit($orders, $symbol, $since, $limit, true);
        }) ();
    }

    public function handle_heartbeat(Client $client, $message) {
        //
        //     {
        //         "type" => "heartbeat",
        //         "timestampms" => 1659740268958,
        //         "sequence" => 7,
        //         "trace_id" => "25b3d92476dd3a9a5c03c9bd9e0a0dba",
        //         "socket_sequence" => 7
        //     }
        //
        return $message;
    }

    public function handle_subscription(Client $client, $message) {
        //
        //     {
        //         "type" => "subscription_ack",
        //         "accountId" => 19433282,
        //         "subscriptionId" => "orderevents-websocket-25b3d92476dd3a9a5c03c9bd9e0a0dba",
        //         "symbolFilter" => array(),
        //         "apiSessionFilter" => array(),
        //         "eventTypeFilter" => array()
        //     }
        //
        return $message;
    }

    public function handle_order(Client $client, $message) {
        //
        //     array(
        //         {
        //             "type" => "accepted",
        //             "order_id" => "134150423884",
        //             "event_id" => "134150423886",
        //             "account_name" => "primary",
        //             "client_order_id" => "1659739406916",
        //             "api_session" => "account-pnBFSS0XKGvDamX4uEIt",
        //             "symbol" => "batbtc",
        //             "side" => "sell",
        //             "order_type" => "exchange $limit",
        //             "timestamp" => "1659739407",
        //             "timestampms" => 1659739407576,
        //             "is_live" => true,
        //             "is_cancelled" => false,
        //             "is_hidden" => false,
        //             "original_amount" => "1",
        //             "price" => "1",
        //             "socket_sequence" => 139
        //         }
        //     )
        //
        $messageHash = 'orders';
        if ($this->orders === null) {
            $limit = $this->safe_integer($this->options, 'ordersLimit', 1000);
            $this->orders = new ArrayCacheBySymbolById ($limit);
        }
        $orders = $this->orders;
        for ($i = 0; $i < count($message); $i++) {
            $order = $this->parse_ws_order($message[$i]);
            $orders->append ($order);
        }
        $client->resolve ($this->orders, $messageHash);
    }

    public function parse_ws_order($order, $market = null) {
        //
        //     {
        //         "type" => "accepted",
        //         "order_id" => "134150423884",
        //         "event_id" => "134150423886",
        //         "account_name" => "primary",
        //         "client_order_id" => "1659739406916",
        //         "api_session" => "account-pnBFSS0XKGvDamX4uEIt",
        //         "symbol" => "batbtc",
        //         "side" => "sell",
        //         "order_type" => "exchange limit",
        //         "timestamp" => "1659739407",
        //         "timestampms" => 1659739407576,
        //         "is_live" => true,
        //         "is_cancelled" => false,
        //         "is_hidden" => false,
        //         "original_amount" => "1",
        //         "price" => "1",
        //         "socket_sequence" => 139
        //     }
        //
        $timestamp = $this->safe_number($order, 'timestampms');
        $status = $this->safe_string($order, 'type');
        $marketId = $this->safe_string($order, 'symbol');
        $typeId = $this->safe_string($order, 'order_type');
        $behavior = $this->safe_string($order, 'behavior');
        $timeInForce = 'GTC';
        $postOnly = false;
        if ($behavior === 'immediate-or-cancel') {
            $timeInForce = 'IOC';
        } elseif ($behavior === 'fill-or-kill') {
            $timeInForce = 'FOK';
        } elseif ($behavior === 'maker-or-cancel') {
            $timeInForce = 'PO';
            $postOnly = true;
        }
        return $this->safe_order(array(
            'id' => $this->safe_string($order, 'order_id'),
            'clientOrderId' => $this->safe_string($order, 'client_order_id'),
            'info' => $order,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601($timestamp),
            'lastTradeTimestamp' => null,
            'status' => $this->parse_ws_order_status($status),
            'symbol' => $this->safe_symbol($marketId, $market),
            'type' => $this->parse_ws_order_type($typeId),
            'timeInForce' => $timeInForce,
            'postOnly' => $postOnly,
            'side' => $this->safe_string($order, 'side'),
            'price' => $this->safe_number($order, 'price'),
            'stopPrice' => null,
            'average' => $this->safe_number($order, 'avg_execution_price'),
            'cost' => null,
            'amount' => $this->safe_number($order, 'original_amount'),
            'filled' => $this->safe_number($order, 'executed_amount'),
            'remaining' => $this->safe_number($order, 'remaining_amount'),
            'fee' => null,
            'trades' => null,
        ), $market);
    }

    public function parse_ws_order_status($status) {
        $statuses = array(
            'accepted' => 'open',
            'booked' => 'open',
            'fill' => 'closed',
            'cancelled' => 'canceled',
            'cancel_rejected' => 'rejected',
            'rejected' => 'rejected',
        );
        return $this->safe_string($statuses, $status, $status);
    }

    public function parse_ws_order_type($type) {
        $types = array(
            'exchange limit' => 'limit',
            'market buy' => 'market',
            'market sell' => 'market',
        );
        return $this->safe_string($types, $type, $type);
    }

    public function handle_error(Client $client, $message) {
        //
        //     {
        //         "reason" => "NoValidTradingPairs",
        //         "result" => "error"
        //     }
        //
        throw new ExchangeError($this->json($message));
    }

    public function handle_message(Client $client, $message) {
        //
        //  public
        //     {
        //         "type" => "trade",
        //         "symbol" => "BTCUSD",
        //         "event_id" => 122278173770,
        //         "timestamp" => 1655335880981,
        //         "price" => "22530.80",
        //         "quantity" => "0.04",
        //         "side" => "buy"
        //     }
        //
        //  private
        //     array(
        //         {
        //             "type" => "accepted",
        //             "order_id" => "134150423884",
        //             "event_id" => "134150423886",
        //             "account_name" => "primary",
        //             "client_order_id" => "1659739406916",
        //             "api_session" => "account-pnBFSS0XKGvDamX4uEIt",
        //             "symbol" => "batbtc",
        //             "side" => "sell",
        //             "order_type" => "exchange limit",
        //             "timestamp" => "1659739407",
        //             "timestampms" => 1659739407576,
        //             "is_live" => true,
        //             "is_cancelled" => false,
        //             "is_hidden" => false,
        //             "original_amount" => "1",
        //             "price" => "1",
        //             "socket_sequence" => 139
        //         }
        //     )
        //
        $isArray = gettype($message) === 'array' && array_keys($message) === array_keys(array_keys($message));
        if ($isArray) {
            return $this->handle_order($client, $message);
        }
        $reason = $this->safe_string($message, 'reason');
        if ($reason === 'error') {
            $this->handle_error($client, $message);
        }
        $methods = array(
            'l2_updates' => array($this, 'handle_l2_updates'),
            'trade' => array($this, 'handle_trade'),
            'subscription_ack' => array($this, 'handle_subscription'),
            'heartbeat' => array($this, 'handle_heartbeat'),
        );
        $type = $this->safe_string($message, 'type', '');
        if (mb_strpos($type, 'candles') !== false) {
            return $this->handle_ohlcv($client, $message);
        }
        $method = $this->safe_value($methods, $type);
        if ($method !== null) {
            $method($client, $message);
        }
    }

    public function authenticate($params = array ()) {
        $url = $this->safe_string($params, 'url');
        if (($this->clients !== null) && (is_array($this->clients) && array_key_exists($url, $this->clients))) {
            return;
        }
        $this->check_required_credentials();
        $startIndex = count($this->urls['api']['ws']);
        $urlParamsIndex = mb_strpos($url, '?');
        $urlLength = count($url);
        $endIndex = ($urlParamsIndex >= 0) ? $urlParamsIndex : $urlLength;
        $request = mb_substr($url, $startIndex, $endIndex - $startIndex);
        $payload = array(
            'request' => $request,
            'nonce' => $this->nonce(),
        );
        $b64 = base64_encode($this->json($payload));
        $signature = $this->hmac($this->encode($b64), $this->encode($this->secret), 'sha384', 'hex');
        $defaultOptions = array(
            'ws' => array(
                'options' => array(
                    'headers' => array(),
                ),
            ),
        );
        $this->options = array_merge($defaultOptions, $this->options);
        $originalHeaders = $this->options['ws']['options']['headers'];
        $headers = array(
            'X-GEMINI-APIKEY' => $this->apiKey,
            'X-GEMINI-PAYLOAD' => $b64,
            'X-GEMINI-SIGNATURE' => $signature,
        );
        $this->options['ws']['options']['headers'] = $headers;
        $this->client($url);
        $this->options['ws']['options']['headers'] = $originalHeaders;
    }
}
