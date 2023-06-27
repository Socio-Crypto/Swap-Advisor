from django.shortcuts import render
from django.views.generic import View
from .services import (data_per_time, get_token_in, get_token_out, get_top_10_tokens, median_rate_per_platform)
from .concurrency import ConcurrentRunner
from django.http import JsonResponse
import json


class DashboardView(View):

    def get(self, request):
        context = {}

        runner = ConcurrentRunner()
        func1 = lambda: median_rate_per_platform('avalanche', '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7', '0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e', 1)
        func2 = data_per_time
        results = runner.run_concurrently(func1, func2)
        data = results['<lambda>']
        context['data'] = data 
        context['median'] = {item['platform']: item['median_of_exch_rate'] for item in data}
        context['average'] = {item['platform']: item['average_of_exch_rate'] for item in data}
        context['swaps'] = {item['platform']: item['number_of_swaps'] for item in data}
        context['swappers'] = {item['platform']: item['number_of_swappers'] for item in data}

        context['heat_map_data'] = results['data_per_time']
        context['platforms'] = list({item['platform'] for item in context['heat_map_data']})
        context['platforms'].remove('gmx')
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
        data = json.loads(request.body)

        network = data['network']
        token_in = data['token_in']
        token_out = data['token_out']
        time = data['time']

        symbols = median_rate_per_platform(network, token_in, token_out, time)
        data = symbols[0]['platform']
        return JsonResponse(data , safe=False)

    return JsonResponse({'error': 'Invalid request'})