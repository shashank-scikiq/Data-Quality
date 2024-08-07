

from django.urls import path, include
from . import views
from .views import *
urlpatterns = [
    path('api/dq_report/', include('dq_api.urls')),
    path('', views.dashboard, name='dashboard'),
    path('api/retail/overall/get-max-date/', GetMaxDate.as_view(), name='get-max-date')
    
]
