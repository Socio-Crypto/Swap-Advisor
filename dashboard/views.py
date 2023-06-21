from django.shortcuts import render
from django.views.generic import View
from .services import median_rate_per_platform
# Create your views here.

class DashboardView(View):

    def get(self, request):
        context = {}
        data = median_rate_per_platform()
        context['data'] = data 
        context['median'] = {item['platform']: item['median_of_exch_rate'] for item in data}
        context['average'] = {item['platform']: item['average_of_exch_rate'] for item in data}
        context['swaps'] = {item['platform']: item['number_of_swaps'] for item in data}
        context['swappers'] = {item['platform']: item['number_of_swappers'] for item in data}
   
        return render(request, 'dashboard.html', context=context)