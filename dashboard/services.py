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


def median_rate_per_platform():

    "Flipside: https://flipsidecrypto.xyz/SocioCrypto/q/C3OmwFf0Pglv/stats"

    sql_query = f"""
       	SELECT platform,
        avg(amount_in/amount_out) as "Average of Exch. Rate",
        median(amount_in/amount_out) as "Median of Exch. Rate",
        count(DISTINCT tx_hash) as "Number of Swaps",
        count (DISTINCT sender) as "Number of Swappers"
        FROM avalanche.core.ez_dex_swaps
        WHERE token_in ilike '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7' AND token_out ilike '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e'
        AND amount_out >0
        AND block_timestamp >= current_date-7
        GROUP BY 1
        ORDER BY 3 DESC
    """
    return get_result_from_query(sql_query)
