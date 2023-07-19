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
        data['stat'] = results['func2']
        
        return JsonResponse(data , safe=False)

    return JsonResponse({'error': 'Invalid request'})