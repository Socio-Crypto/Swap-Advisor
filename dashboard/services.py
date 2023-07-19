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

    # sql_query = f"""
    #    	SELECT platform,
    #     avg(amount_in/amount_out) as "average_of_exch_rate",
    #     median(amount_in/amount_out) as "median_of_exch_rate",
    #     count(DISTINCT tx_hash) as "number_of_swaps",
    #     count (DISTINCT sender) as "number_of_swappers"
    #     FROM {network}.core.ez_dex_swaps
    #     WHERE token_in ilike '{token_in}' AND token_out ilike '{token_out}'
    #     AND amount_out >0
    #     AND block_timestamp  > dateadd('month', -{time}, current_date)
    #     AND platform != 'curve' --excluded as it has a problem in WETH/USDC convertion rate
    #     GROUP BY 1
    #     ORDER BY 3 DESC
    # """
   
    sql_query = f"""
       	SELECT 
        platform,
        avg(gas_used) as "avg_gas_used",
        avg(tx_fee) as "avg_tx_fee",
        avg(amount_in/amount_out) as "average_of_exch_rate",
        median(amount_in/amount_out) as "median_of_exch_rate",
        count(DISTINCT a.tx_hash) as "number_of_swaps",
        count (DISTINCT a.origin_from_address) as "number_of_swappers"
        FROM {network}.core.ez_dex_swaps a 
        LEFT JOIN {network}.core.fact_transactions b using(tx_hash)
        WHERE token_in LIKE lower('{token_in}') AND token_out LIKE lower('{token_out}')
        AND a.block_timestamp > dateadd('month', -1*{time}, current_date)
        AND a.block_timestamp < current_date
        AND amount_out >0
        AND platform != 'curve' --excluded as it has a problem in WETH/USDC convertion rate
        GROUP BY platform
        HAVING "number_of_swaps" > 10 
        ORDER BY "median_of_exch_rate" 
    """
   

    return get_result_from_query(sql_query)


def data_per_time(network, token_in, token_out, time):

    "Flipside: https://flipsidecrypto.xyz/SocioCrypto/q/C3OmwFf0Pglv/stats"

    # sql_query = f"""
    #    	SELECT 
    #     Platform,
    #     DAYname(block_timestamp) as DAY,
    #     hour(block_timestamp) as time,
    #     avg(amount_in/amount_out) as avg,
    #     count(DISTINCT tx_hash) as n_txn
    #     FROM {network}.core.ez_dex_swaps
    #     WHERE token_in ilike '{token_in}'
    #     AND token_out ilike '{token_out}'
    #     AND amount_out >0
    #     AND block_timestamp  > dateadd('month', -{time}, current_date)
    #     GROUP BY 1,2,3
    #     ORDER BY 1,2,3
    # """
    sql_query = f"""
       	SELECT 
            Platform,
            DAYname(block_timestamp) as DAY,
            hour(block_timestamp) as time,
            avg(amount_in/amount_out) as avg,
            count(DISTINCT a.tx_hash) as n_txn,
            avg(gas_used) as avg_gas_used,
            avg(tx_fee) as avg_tx_fee
        FROM {network}.core.ez_dex_swaps a 
        LEFT JOIN {network}.core.fact_transactions b using(tx_hash)
        WHERE token_in like lower('{token_in}')
        AND token_out like lower('{token_out}')
        AND amount_out >0
        AND block_timestamp  > dateadd('month', -{time}, current_date)
        GROUP BY 1,2,3
        HAVING n_txn > 10 
        ORDER BY 1,2,3
    """
    return get_result_from_query(sql_query)


def get_stats_table(network, token_in, token_out, time):

    # sql_query = f"""
    #     WITH first_query AS (
    #     SELECT platform,
    #         avg(amount_in/amount_out) as "Average of Exch. Rate",
    #         median(amount_in/amount_out) as "Median of Exch. Rate",
    #         count(DISTINCT tx_hash) as "Number of Swaps",
    #         count(DISTINCT sender) as "Number of Swappers"
    #     FROM {network}.core.ez_dex_swaps
    #     WHERE token_in ilike '{token_in}' AND token_out ilike '{token_out}'
    #         AND amount_out > 0
    #         AND block_timestamp  > dateadd('month', -{time}, current_date)
    #     GROUP BY 1
    #     ORDER BY 3 DESC
    #     ),
    #     second_query AS (
    #     WITH tb0 AS (
    #         SELECT date_trunc('day', block_timestamp) as date,
    #         platform,
    #         zeroifnull (count(DISTINCT tx_hash)) as n_swaps,
    #         count(DISTINCT sender) as n_swappers
    #         FROM {network}.core.ez_dex_swaps
    #     WHERE token_in ilike '{token_in}' AND token_out ilike '{token_out}'
    #         AND amount_out > 0 
    #         AND block_timestamp  > dateadd('month', -{time}, current_date)
    #         GROUP BY 1, 2
    #     )
    #     SELECT platform,
    #         ARRAY_AGG(coalesce(n_swaps, 0)) as swaps,
    #         ARRAY_AGG(coalesce(n_swappers, 0)) as swappers
    #     FROM tb0
    #     GROUP BY 1
        
    #     )
    #     SELECT first_query.platform,
    #     first_query."Average of Exch. Rate",
    #     first_query."Median of Exch. Rate",
    #     second_query.swaps,
    #     second_query.swappers
    #     FROM first_query
    #     JOIN second_query ON first_query.platform = second_query.platform;
    # """
    
    sql_query = f"""
       WITH first_query AS (
        SELECT 
              platform,
              avg(gas_used) as "avg.gas_used",
              avg(tx_fee) as "avg.tx_fee",
              avg(amount_in/amount_out) as "avg.exch rate",
              median(amount_in/amount_out) as "median.exch rate",
              count(DISTINCT a.tx_hash) as "number_of_swaps",
              count (DISTINCT a.origin_from_address) as "number of swappers"
    FROM {network}.core.ez_dex_swaps a 
    LEFT JOIN {network}.core.fact_transactions b using(tx_hash)
    WHERE token_in LIKE lower('{token_in}') AND token_out LIKE lower('{token_out}')
    AND a.block_timestamp > dateadd('month', -1*{time}, current_date)
    AND a.block_timestamp < current_date
    AND amount_out >0
    AND platform != 'curve' --excluded as it has a problem in WETH/USDC convertion rate
    GROUP BY platform
    HAVING "number_of_swaps" > 10 
    ORDER BY "median.exch rate" 
        ),
        second_query AS (
        WITH tb0 AS (
            SELECT date_trunc('day', block_timestamp) as date,
            platform,
            zeroifnull(count(DISTINCT tx_hash)) as n_swaps,
            count(DISTINCT origin_from_address) as n_swappers
            FROM {network}.core.ez_dex_swaps
            WHERE token_in LIKE lower('{token_in}') AND token_out LIKE '{token_out}'
            AND amount_out > 0 
            AND block_timestamp  > dateadd('month', -1*{time}, current_date)
            GROUP BY 1, 2
        )
        SELECT platform,
            ARRAY_AGG(coalesce(n_swaps, 0)) as swaps,
            ARRAY_AGG(coalesce(n_swappers, 0)) as swappers
        FROM tb0
        GROUP BY 1
        
        )
        SELECT first_query.platform,
        first_query."avg.exch rate",
        first_query."median.exch rate",
        first_query."avg.gas_used",
        first_query."avg.tx_fee",
        second_query.swaps,
        second_query.swappers
        FROM first_query
        JOIN second_query ON first_query.platform = second_query.platform;
    """
    
    return get_result_from_query(sql_query)
 


def get_initial_stats_table(network, token_in, token_out, time):

    sql_query = f"""
        WITH first_query AS (
        SELECT platform,
            avg(amount_in/amount_out) as "Average of Exch. Rate",
            median(amount_in/amount_out) as "Median of Exch. Rate",
            count(DISTINCT tx_hash) as "Number of Swaps",
            count(DISTINCT sender) as "Number of Swappers"
        FROM {network}.core.ez_dex_swaps
        WHERE amount_out > 0
            AND block_timestamp  > dateadd('month', -{time}, current_date)
        GROUP BY 1
        ORDER BY 3 DESC
        ),
        second_query AS (
        WITH tb0 AS (
            SELECT date_trunc('day', block_timestamp) as date,
            platform,
            zeroifnull (count(DISTINCT tx_hash)) as n_swaps,
            count(DISTINCT sender) as n_swappers
            FROM {network}.core.ez_dex_swaps
        WHERE amount_out > 0 
            AND block_timestamp  > dateadd('month', -{time}, current_date)
            GROUP BY 1, 2
        )
        SELECT platform,
            ARRAY_AGG(coalesce(n_swaps, 0)) as swaps,
            ARRAY_AGG(coalesce(n_swappers, 0)) as swappers
        FROM tb0
        GROUP BY 1
        
        )
        SELECT first_query.platform,
        first_query."Average of Exch. Rate",
        first_query."Median of Exch. Rate",
        second_query.swaps,
        second_query.swappers
        FROM first_query
        JOIN second_query ON first_query.platform = second_query.platform;
    """
    
    return get_result_from_query(sql_query)
 
 
# def get_token_in():

#     sql_query = """ 
#         SELECT 
#         DISTINCT symbol_in
#         FROM avalanche.core.ez_dex_swaps
#         WHERE BLOCK_TIMESTAMP > dateadd('month', -1, current_date)
#     """

#     return get_result_from_query(sql_query)


# def get_token_out():

#     sql_query = """ 
#         SELECT 
#         DISTINCT symbol_out
#         FROM avalanche.core.ez_dex_swaps
#         WHERE BLOCK_TIMESTAMP > dateadd('month', -1, current_date)
#     """

#     return get_result_from_query(sql_query)


# def get_top_10_tokens():

#     sql_query = """
#         SELECT symbols
#         FROM(
#         SELECT 
#         coalesce(symbol_in,symbol_out) as symbols,
#         count(1)
#         FROM avalanche.core.ez_dex_swaps
#         WHERE BLOCK_TIMESTAMP > dateadd('month', -1, current_date)
#         GROUP BY 1
#         ORDER BY 2 DESC 
#         LIMIT 10 
#         )
#     """
#     return get_result_from_query(sql_query)
