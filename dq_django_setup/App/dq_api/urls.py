from django.urls import path
from .views import *

urlpatterns = [
    path('top_card/', Top_card.as_view(), name='top_card'),
    path('radial_chart_data/', Radial_chart_Data.as_view(), name='radial_chart_data'),
    path('cancel_highest_missing_pid_data/', CancelHighestMissingPidData.as_view(), name='cancel_highest_missing_pid_data'),
    path('detail_cancel_table_data/', DetailCancelTableData.as_view(), name='detail_cancel_table_data'),
    path('detail_completed_table_data/', DetailCompletedTableData.as_view(), name='detail_completed_table_data'),
    path('trend_1/', MissingOrdersTrend.as_view(), name='trend_1'),
    path('trend_2/', CancellationTrend.as_view(), name='trend_2'),

    

]
