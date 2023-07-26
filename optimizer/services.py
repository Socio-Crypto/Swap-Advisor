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


def get_routes(network):

    sql_query = f"""
       	SELECT 
            symbol_in,
            symbol_out,
            token_in,
            token_out,
            platform,
            AVG(amount_in/amount_out) as "Avg.Exch Rate",
            AVG(gas_used) as "Avg Gas Used"
        FROM {network}.core.ez_dex_swaps a
        JOIN {network}.core.fact_transactions b using(tx_hash)
        WHERE a.block_timestamp::date > dateadd('week' , -1, current_date)
        AND a.block_timestamp < current_date
        AND amount_out >0
        AND platform != 'curve'
        GROUP BY 1 , 2 , 3 , 4 , 5
    """
   
    return get_result_from_query(sql_query)