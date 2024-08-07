from django.shortcuts import render
import random
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
def dashboard(request):
    return render(request, 'base.html')

class GetMaxDate(APIView):
    """
            GetMaxDate
    """

    def get(self, request, format=None):
        # Generate a random date
        # start_date = datetime(2000, 1, 1)
        # end_date = datetime(2100, 12, 31)
        # random_date = start_date + timedelta(
        #     days=random.randint(0, (end_date - start_date).days)
        # )
        
        # # Format the date as a string
        # random_date_str = random_date.strftime("%Y-%m-%d")
        
        return Response({
            'min_date': "2024-04-01", 'max_date': "2024-07-01"
        }, status=status.HTTP_200_OK)