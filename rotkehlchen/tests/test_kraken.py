import pytest

from rotkehlchen.assets.asset import Asset
from rotkehlchen.assets.converters import asset_from_kraken
from rotkehlchen.constants.assets import A_BTC, A_ETH
from rotkehlchen.errors import UnprocessableTradePair
from rotkehlchen.fval import FVal
from rotkehlchen.kraken import KRAKEN_ASSETS, kraken_to_world_pair, trade_from_kraken
from rotkehlchen.order_formatting import Trade
from rotkehlchen.utils.misc import ts_now


def test_coverage_of_kraken_balances(kraken):
    all_assets = set(kraken.query_public('Assets').keys())
    diff = set(KRAKEN_ASSETS).symmetric_difference(all_assets)
    assert len(diff) == 0, (
        f"Our known assets don't match kraken's assets. Difference: {diff}"
    )
    # Make sure all assets are covered by our from and to functions
    for kraken_asset in all_assets:
        asset = asset_from_kraken(kraken_asset)
        assert asset.to_kraken() == kraken_asset


def test_querying_balances(kraken):
    result, error_or_empty = kraken.query_balances()
    assert error_or_empty == ''
    assert isinstance(result, dict)
    for name, entry in result.items():
        # Make sure this does not fail
        Asset(name)
        assert 'usd_value' in entry
        assert 'amount' in entry


def test_querying_trade_history(kraken):
    now = ts_now()
    result = kraken.query_trade_history(
        start_ts=1451606400,
        end_ts=now,
        end_at_least_ts=now,
    )
    assert isinstance(result, list)
    assert len(result) != 0

    for kraken_trade in result:
        trade = trade_from_kraken(kraken_trade)
        assert isinstance(trade, Trade)


def test_querying_deposits_withdrawals(kraken):
    now = ts_now()
    result = kraken.query_trade_history(
        start_ts=1451606400,
        end_ts=now,
        end_at_least_ts=now,
    )
    assert isinstance(result, list)
    assert len(result) != 0


def test_kraken_to_world_pair():
    assert kraken_to_world_pair('QTUMXBT') == 'QTUM_BTC'
    assert kraken_to_world_pair('ADACAD') == 'ADA_CAD'
    assert kraken_to_world_pair('BCHUSD') == 'BCH_USD'
    assert kraken_to_world_pair('DASHUSD') == 'DASH_USD'
    assert kraken_to_world_pair('XTZETH') == 'XTZ_ETH'
    assert kraken_to_world_pair('XXBTZGBP.d') == 'BTC_GBP'

    with pytest.raises(UnprocessableTradePair):
        kraken_to_world_pair('GABOOBABOO')


def test_find_fiat_price(kraken):
    """
    Testing that find_fiat_price works correctly

    Also regression test for https://github.com/rotkehlchenio/rotkehlchen/issues/323
    """
    kraken.first_connection()
    # A single YEN should cost less than 1 bitcoin
    jpy_price = kraken.find_fiat_price('ZJPY')
    assert jpy_price < FVal('1')

    # Kraken fees have no value
    assert kraken.find_fiat_price('KFEE') == FVal('0')


def test_kraken_query_balances_unknown_asset(function_scope_kraken):
    """Test that if a kraken balance query returns unknown asset no exception
    is raised and a warning is generated"""
    kraken = function_scope_kraken
    kraken.random_balance_data = False
    balances, msg = kraken.query_balances()

    assert msg == ''
    assert len(balances) == 2
    assert balances[A_BTC]['amount'] == FVal('5.0')
    assert balances[A_ETH]['amount'] == FVal('10.0')

    warnings = kraken.msg_aggregator.consume_warnings()
    assert len(warnings) == 1
    assert 'unsupported/unknown kraken asset NOTAREALASSET' in warnings[0]


@pytest.mark.parametrize('use_clean_caching_directory', [True])
def test_kraken_query_deposit_withdrawals_unknown_asset(function_scope_kraken):
    """Test that if a kraken deposits_withdrawals query returns unknown asset
    no exception is raised and a warning is generated"""
    kraken = function_scope_kraken
    kraken.random_ledgers_data = False

    movements = kraken.query_deposits_withdrawals(
        start_ts=1408994442,
        end_ts=1498994442,
        end_at_least_ts=1498994442,
    )

    assert len(movements) == 4
    assert movements[0].asset == A_BTC
    assert movements[0].amount == FVal('5.0')
    assert movements[0].category == 'deposit'
    assert movements[1].asset == A_ETH
    assert movements[1].amount == FVal('10.0')
    assert movements[1].category == 'deposit'
    assert movements[2].asset == A_BTC
    assert movements[2].amount == FVal('5.0')
    assert movements[2].category == 'withdrawal'
    assert movements[3].asset == A_ETH
    assert movements[3].amount == FVal('10.0')
    assert movements[3].category == 'withdrawal'

    warnings = kraken.msg_aggregator.consume_warnings()
    assert len(warnings) == 2
    assert 'unknown kraken asset IDONTEXIST' in warnings[0]
    assert 'unknown kraken asset IDONTEXISTEITHER' in warnings[1]
