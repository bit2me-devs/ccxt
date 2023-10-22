import os
import sys

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(root)

# ----------------------------------------------------------------------------

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

# ----------------------------------------------------------------------------
# -*- coding: utf-8 -*-


from ccxt.base.precise import Precise  # noqa E402
from ccxt.test.base import test_shared_methods  # noqa E402


def test_market(exchange, skipped_properties, method, market):
    format = {
        'id': 'btcusd',
        'symbol': 'BTC/USD',
        'base': 'BTC',
        'quote': 'USD',
        'taker': exchange.parse_number('0.0011'),
        'maker': exchange.parse_number('0.0009'),
        'baseId': 'btc',
        'quoteId': 'usd',
        'active': False,
        'type': 'spot',
        'linear': False,
        'inverse': False,
        'spot': False,
        'swap': False,
        'future': False,
        'option': False,
        'margin': False,
        'contract': False,
        'contractSize': exchange.parse_number('0.001'),
        'expiry': 1656057600000,
        'expiryDatetime': '2022-06-24T08:00:00.000Z',
        'optionType': 'put',
        'strike': exchange.parse_number('56000'),
        'settle': 'XYZ',
        'settleId': 'Xyz',
        'precision': {
            'price': exchange.parse_number('0.001'),
            'amount': exchange.parse_number('0.001'),
            'cost': exchange.parse_number('0.001'),
        },
        'limits': {
            'amount': {
                'min': exchange.parse_number('0.01'),
                'max': exchange.parse_number('1000'),
            },
            'price': {
                'min': exchange.parse_number('0.01'),
                'max': exchange.parse_number('1000'),
            },
            'cost': {
                'min': exchange.parse_number('0.01'),
                'max': exchange.parse_number('1000'),
            },
        },
        'info': {},
    }
    empty_allowed_for = ['linear', 'inverse', 'settle', 'settleId', 'expiry', 'expiryDatetime', 'optionType', 'strike', 'margin', 'contractSize']
    test_shared_methods.assert_structure(exchange, skipped_properties, method, market, format, empty_allowed_for)
    test_shared_methods.assert_symbol(exchange, skipped_properties, method, market, 'symbol')
    log_text = test_shared_methods.log_template(exchange, method, market)
    #
    valid_types = ['spot', 'margin', 'swap', 'future', 'option']
    test_shared_methods.assert_in_array(exchange, skipped_properties, method, market, 'type', valid_types)
    has_index = ('index' in market)  # todo: add in all
    # check if string is consistent with 'type'
    if market['spot']:
        assert market['type'] == 'spot', '\"type\" string should be \"spot\" when spot is true' + log_text
    elif market['swap']:
        assert market['type'] == 'swap', '\"type\" string should be \"swap\" when swap is true' + log_text
    elif market['future']:
        assert market['type'] == 'future', '\"type\" string should be \"future\" when future is true' + log_text
    elif market['option']:
        assert market['type'] == 'option', '\"type\" string should be \"option\" when option is true' + log_text
    elif has_index and market['index']:
        # todo: add index in all implementations
        assert market['type'] == 'index', '\"type\" string should be \"index\" when index is true' + log_text
    # margin check (todo: add margin as mandatory, instead of undefined)
    if market['spot']:
        # for spot market, 'margin' can be either true/false or undefined
        test_shared_methods.assert_in_array(exchange, skipped_properties, method, market, 'margin', [True, False, None])
    else:
        # otherwise, it must be false or undefined
        test_shared_methods.assert_in_array(exchange, skipped_properties, method, market, 'margin', [False, None])
    if not ('contractSize' in skipped_properties):
        test_shared_methods.assert_greater(exchange, skipped_properties, method, market, 'contractSize', '0')
    # typical values
    test_shared_methods.assert_greater(exchange, skipped_properties, method, market, 'expiry', '0')
    test_shared_methods.assert_greater(exchange, skipped_properties, method, market, 'strike', '0')
    test_shared_methods.assert_in_array(exchange, skipped_properties, method, market, 'optionType', ['put', 'call'])
    test_shared_methods.assert_greater(exchange, skipped_properties, method, market, 'taker', '-100')
    test_shared_methods.assert_greater(exchange, skipped_properties, method, market, 'maker', '-100')
    # 'contract' boolean check
    if market['future'] or market['swap'] or market['option'] or (has_index and market['index']):
        # if it's some kind of contract market, then `conctract` should be true
        assert market['contract'], '\"contract\" must be true when \"future\", \"swap\", \"option\" or \"index\" is true' + log_text
    else:
        assert not market['contract'], '\"contract\" must be false when neither \"future\", \"swap\",\"option\" or \"index\" is true' + log_text
    is_swap_or_future = market['swap'] or market['future']
    contract_size = exchange.safe_string(market, 'contractSize')
    # contract fields
    if market['contract']:
        # linear & inverse should have different values (true/false)
        # todo: expand logic on other market types
        if is_swap_or_future:
            assert market['linear'] != market['inverse'], 'market linear and inverse must not be the same' + log_text
            if not ('contractSize' in skipped_properties):
                # contract size should be defined
                assert contract_size is not None, '\"contractSize\" must be defined when \"contract\" is true' + log_text
                # contract size should be above zero
                assert Precise.string_gt(contract_size, '0'), '\"contractSize\" must be > 0 when \"contract\" is true' + log_text
            if not ('settle' in skipped_properties):
                # settle should be defined
                assert (market['settle'] is not None) and (market['settleId'] is not None), '\"settle\" & \"settleId\" must be defined when \"contract\" is true' + log_text
        # spot should be false
        assert not market['spot'], '\"spot\" must be false when \"contract\" is true' + log_text
    else:
        # linear & inverse needs to be undefined
        assert (market['linear'] is None) and (market['inverse'] is None), 'market linear and inverse must be undefined when \"contract\" is true' + log_text
        # contract size should be undefined
        if not ('contractSize' in skipped_properties):
            assert contract_size is None, '\"contractSize\" must be undefined when \"contract\" is false' + log_text
        # settle should be undefined
        assert (market['settle'] is None) and (market['settleId'] is None), '\"settle\" must be undefined when \"contract\" is true' + log_text
        # spot should be true
        assert market['spot'], '\"spot\" must be true when \"contract\" is false' + log_text
    # option fields
    if market['option']:
        # if option, then strike and optionType should be defined
        assert market['strike'] is not None, '\"strike\" must be defined when \"option\" is true' + log_text
        assert market['optionType'] is not None, '\"optionType\" must be defined when \"option\" is true' + log_text
    else:
        # if not option, then strike and optionType should be undefined
        assert market['strike'] is None, '\"strike\" must be undefined when \"option\" is false' + log_text
        assert market['optionType'] is None, '\"optionType\" must be undefined when \"option\" is false' + log_text
    # future, swap and option should be mutually exclusive
    if market['future']:
        assert not market['swap'] and not market['option'], 'market swap and option must be false when \"future\" is true' + log_text
    elif market['swap']:
        assert not market['future'] and not market['option'], 'market future and option must be false when \"swap\" is true' + log_text
    elif market['option']:
        assert not market['future'] and not market['swap'], 'market future and swap must be false when \"option\" is true' + log_text
    # expiry field
    if market['future'] or market['option']:
        # future or option markets need 'expiry' and 'expiryDatetime'
        assert market['expiry'] is not None, '\"expiry\" must be defined when \"future\" is true' + log_text
        assert market['expiryDatetime'] is not None, '\"expiryDatetime\" must be defined when \"future\" is true' + log_text
        # expiry datetime should be correct
        iso_string = exchange.iso8601(market['expiry'])
        assert market['expiryDatetime'] == iso_string, 'expiryDatetime (\"' + market['expiryDatetime'] + '\") must be equal to expiry in iso8601 format \"' + iso_string + '\"' + log_text
    else:
        # otherwise, they need to be undefined
        assert (market['expiry'] is None) and (market['expiryDatetime'] is None), '\"expiry\" and \"expiryDatetime\" must be undefined when it is not future|option market' + log_text
    # check precisions
    if not ('precision' in skipped_properties):
        precision_keys = list(market['precision'].keys())
        keys_length = len(precision_keys)
        assert keys_length >= 2, 'precision should have \"amount\" and \"price\" keys at least' + log_text
        for i in range(0, len(precision_keys)):
            test_shared_methods.check_precision_accuracy(exchange, skipped_properties, method, market['precision'], precision_keys[i])
    # check limits
    if not ('limits' in skipped_properties):
        limits_keys = list(market['limits'].keys())
        keys_length = len(limits_keys)
        assert keys_length >= 3, 'limits should have \"amount\", \"price\" and \"cost\" keys at least' + log_text
        for i in range(0, len(limits_keys)):
            key = limits_keys[i]
            limit_entry = market['limits'][key]
            # min >= 0
            test_shared_methods.assert_greater_or_equal(exchange, skipped_properties, method, limit_entry, 'min', '0')
            # max >= 0
            test_shared_methods.assert_greater(exchange, skipped_properties, method, limit_entry, 'max', '0')
            # max >= min
            min_string = exchange.safe_string(limit_entry, 'min')
            if min_string is not None:
                test_shared_methods.assert_greater_or_equal(exchange, skipped_properties, method, limit_entry, 'max', min_string)
    # check whether valid currency ID and CODE is used
    if not ('currencyIdAndCode' in skipped_properties):
        test_shared_methods.assert_valid_currency_id_and_code(exchange, skipped_properties, method, market, market['baseId'], market['base'])
        test_shared_methods.assert_valid_currency_id_and_code(exchange, skipped_properties, method, market, market['quoteId'], market['quote'])
        test_shared_methods.assert_valid_currency_id_and_code(exchange, skipped_properties, method, market, market['settleId'], market['settle'])
    test_shared_methods.assert_timestamp(exchange, skipped_properties, method, market, None, 'created')
