from django.shortcuts import render
from django.views.generic import View
from .services import median_rate_per_platform, data_per_time
from .concurrency import ConcurrentRunner
class DashboardView(View):

    def get(self, request):
        context = {}

        runner = ConcurrentRunner()
        results = runner.run_concurrently(median_rate_per_platform, data_per_time)
        data = results['median_rate_per_platform']
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