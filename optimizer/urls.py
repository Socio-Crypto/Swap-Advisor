from django.urls import path
from .views import find_path, SaveDataInJsonView

urlpatterns = [
    path('find_path/', find_path, name='find_path'),
	path('updatejson/', SaveDataInJsonView.as_view(), name='updatejson'),

]
