from django.shortcuts import render
from django.views.generic import View
from .services import median_rate_per_platform
# Create your views here.

class DashboardView(View):

    def get(self, request):
        data = median_rate_per_platform()
        median = {item['platform']: item['number of swappers'] for item in data}
        context = {}
        context['median'] = median
        return render(request, 'dashboard.html', context=context)