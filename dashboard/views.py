from django.shortcuts import render
from django.views.generic import View
from .services import (data_per_time, median_rate_per_platform, get_stats_table, get_initial_stats_table)
from .concurrency import ConcurrentRunner
from django.http import JsonResponse
import json


class DashboardView(View):

    def get(self, request, network, token_in, token_out, time, dexValue):
        context = {}

        runner = ConcurrentRunner()
        func1 = lambda: median_rate_per_platform(network,token_in, token_out, time)
        func2 = lambda: data_per_time(network, token_in, token_out, time)
        results = runner.run_concurrently(func1, func2)
        data = results['func1']
        context['data'] = data 
        context['median'] = {item['platform']: item['median_of_exch_rate'] for item in data}
        context['average'] = {item['platform']: item['average_of_exch_rate'] for item in data}
        context['gas_used'] = {item['platform']: item['avg_gas_used'] for item in data}
        context['tx_fee'] = {item['platform']: item['avg_tx_fee'] for item in data}
        context['swaps'] = {item['platform']: item['number_of_swaps'] for item in data}
        context['swappers'] = {item['platform']: item['number_of_swappers'] for item in data}

        context['heat_map_data'] = results['func2']
        context['platforms'] = list({item['platform'] for item in context['heat_map_data']})

        context['platforms'].remove(dexValue)

        context['network'] = network
        context['platform'] = dexValue

        # {unique(item['platform']) for item in context['data_time']}

        return render(request, 'dashboard.html', context=context)
    

class LandingView(View):

    def get(self, request):
        context = {}

        # runner = ConcurrentRunner()
        # results = runner.run_concurrently(get_top_10_tokens)

        # context['symbols'] = get_top_10_tokens()

        return render(request, 'landing.html', context=context)
    

class Cancel(View):

    def get(self, request):
        context = {}

        import requests
        import json

        # Replace with your actual API key
        api_key = "0aa823ca-fc7c-485a-9412-4d96b04e54be"

        # Replace with the unique identifier of the query run to be canceled
        query_run_id = [
            "clk6sixg500ozon0tnvl74xj8",
            "clk6s6kl10064mu0twcrh0oxm",
            "clk6s5l0t00g8ok0tb043ku74",
            "clk6rxcyv00hwlt0t2hlibkmd",
            "clk6rwyb000hrlt0tmg7sxnst",
        ]

        for item in query_run_id:
            # JSON-RPC endpoint URL
            url = "https://api-v2.flipsidecrypto.xyz/json-rpc"

            # Request headers
            headers = {
                "Content-Type": "application/json",
                "x-api-key": api_key,
            }

            # Request body
            request_data = {
                "jsonrpc": "2.0",
                "method": "cancelQueryRun",
                "params": [{"queryRunId": item}],
                "id": 1,
            }

            # Make the POST request
            response = requests.post(url, headers=headers, data=json.dumps(request_data))

            # Check the response
            if response.status_code == 200:
                # Query was successfully canceled
                data = response.json()
                print("Query was successfully canceled.")
            else:
                # Failed to cancel the query
                print("Failed to cancel the query. Status code:", response.status_code)
                print("Error message:", response.text)
            
            
        return JsonResponse({'error': 'Invalid request'})
    

def find_dex(request):
    if request.method == 'POST':
        data = {}
        network = request.POST.get('network')
        token_in = request.POST.get('token_in')
        token_out = request.POST.get('token_out')
        time = request.POST.get('time')

        runner = ConcurrentRunner()
        func1 = lambda: median_rate_per_platform(network,token_in, token_out, time)
        func2 = lambda: get_stats_table(network, token_in, token_out, time)
        results = runner.run_concurrently(func1, func2)
        
        data['platform'] = results['func1'][0]['platform']
        data['median'] = results['func1'][0]['median_of_exch_rate']

        sorted_func1 = sorted(results['func1'], key=lambda x: x['avg_gas_used'])
        
        data['platform_2'] = sorted_func1[0]['platform']
        data['median_2'] = sorted_func1[0]['median_of_exch_rate']
        
        data['stat'] = results['func2']
        
        return JsonResponse(data , safe=False)

    return JsonResponse({'error': 'Invalid request'})