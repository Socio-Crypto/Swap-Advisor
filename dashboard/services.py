import itertools
from datetime import datetime
import json
from flipside import Flipside

def get_result_from_query(sql_query):
    
    flipside = Flipside("0aa823ca-fc7c-485a-9412-4d96b04e54be", "https://api-v2.flipsidecrypto.xyz")
    result = flipside.query(sql_query)

    activity_data = {}
    if result.records is not None:
        activity_data = result.records
    return activity_data


def median_rate_per_platform(network, token_in, token_out, time):

    "Flipside: https://flipsidecrypto.xyz/SocioCrypto/q/C3OmwFf0Pglv/stats"

    sql_query = f"""
       	SELECT platform,
        avg(amount_in/amount_out) as "average_of_exch_rate",
        median(amount_in/amount_out) as "median_of_exch_rate",
        count(DISTINCT tx_hash) as "number_of_swaps",
        count (DISTINCT sender) as "number_of_swappers"
        FROM {network}.core.ez_dex_swaps
        WHERE token_in ilike '{token_in}' AND token_out ilike '{token_out}'
        AND amount_out >0
        AND block_timestamp  > dateadd('month', -{time}, current_date)
        AND platform != 'curve' --excluded as it has a problem in WETH/USDC convertion rate
        GROUP BY 1
        ORDER BY 3 DESC
    """
    return get_result_from_query(sql_query)


def data_per_time():

    "Flipside: https://flipsidecrypto.xyz/SocioCrypto/q/C3OmwFf0Pglv/stats"

    sql_query = f"""
       	SELECT 
        Platform,
        DAYname(block_timestamp) as DAY,
        hour(block_timestamp) as time,
        avg(amount_in/amount_out) as avg,
        count(DISTINCT tx_hash) as n_txn
        FROM avalanche.core.ez_dex_swaps
        WHERE token_in ilike '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7'
        AND token_out ilike '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e'
        AND amount_out >0
        AND block_timestamp >= current_date-7
        GROUP BY 1,2,3
        ORDER BY 1,2,3
    """
    return get_result_from_query(sql_query)


def get_token_in():

    sql_query = """ 
        SELECT 
        DISTINCT symbol_in
        FROM avalanche.core.ez_dex_swaps
        WHERE BLOCK_TIMESTAMP > dateadd('month', -1, current_date)
    """

    return get_result_from_query(sql_query)


def get_token_out():

    sql_query = """ 
        SELECT 
        DISTINCT symbol_out
        FROM avalanche.core.ez_dex_swaps
        WHERE BLOCK_TIMESTAMP > dateadd('month', -1, current_date)
    """

    return get_result_from_query(sql_query)


def get_top_10_tokens():

    sql_query = """
        SELECT symbols
        FROM(
        SELECT 
        coalesce(symbol_in,symbol_out) as symbols,
        count(1)
        FROM avalanche.core.ez_dex_swaps
        WHERE BLOCK_TIMESTAMP > dateadd('month', -1, current_date)
        GROUP BY 1
        ORDER BY 2 DESC 
        LIMIT 10 
        )
    """
    return get_result_from_query(sql_query)
