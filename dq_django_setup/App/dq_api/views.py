from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response




class Top_card(APIView):
    """
            fetch top card data
    
    """
    
    def get(self, request):
            try:
                data = [
                    {
                        'title': "Total Orders",
                        'count': "0.81%",
                        'increased': True,
                        'variancePercentage': "1.2%",
                        'varianceText': "vs Yesterday"
                        },
                        {
                        'title': "Total Cancellations",
                        'count': "3,137",
                        'increased': False,
                        'variancePercentage': "0.7%",
                        'varianceText': "vs. Yesterday"
                        },
                        {
                        'title': "Orders Completed %",
                        'count': "$306.20",
                        'increased': False,
                        'variancePercentage': "0.3%",
                        'varianceText': "vs. Yesterday"
                        },
                        {
                        'title': "Orders Cancelled %",
                        'count': "1,650",
                        'increased': False,
                        'variancePercentage': "2.1%",
                        'varianceText': "vs. Yesterday"
                    },
                    ]
            
            except Exception as e:
                print("cannot load top card api ", e)
            
            
            return Response(data=data)


class Radial_chart_Data(APIView):
     """
            fetch radial chart data
     """
     
     def get(self, request):
            try:
               data = [
                        {
                        'title': 'Delivery City',
                        'series': [3.1, 2.1]
                        }, {
                        'title': 'Item Category',
                        'series': [2.3, 2.2]
                        }, {
                        'title': 'Consolidated Category',
                        'series': [2.16, 2.06]
                        }, {
                        'title': 'Seller Pincode',
                        'series': [0.12, .30]
                        }, {
                        'title': 'Seller City',
                        'series': [0.040,0.029 ]
                        }, {
                        'title': 'Provider Pincode',
                        'series': [0.0060, 0.089]
                        },
               ]
               
            except Exception as e:
                print("cannot load radial chart data api", e)

            return Response(data=data)
      
            
class CancelHighestMissingPidData(APIView):
     """
            fetch cancelled highest missing pid data
     
     """  
     
     def get(self, request):
        try:
            data = [
                    {
                        'id': "ondc-otipy.crofarm.com",
                        'count': "0.81%",
                        'increased': True,
                        'variancePercentage': "1.2%",
                        'varianceText': "vs. Yesterday"
                        },
                        {
                        'id': "ondc-otipy.crofarm.com",
                        'count': "0.81%",
                        'increased': True,
                        'variancePercentage': "1.2%",
                        'varianceText': "vs. Yesterday"
                        },
                        {
                        'id': "ondc-otipy.crofarm.com",
                        'count': "0.81%",
                        'increased': True,
                        'variancePercentage': "1.2%",
                        'varianceText': "vs. Yesterday"
                    }
                ]  
            
        except Exception as e:
            print("api is not loading for cancelled highest missing pid ", e)

        return Response(data=data)

class DetailCancelTableData(APIView):
    """
      DetailCancelTableData
    """
    
    def get(self, request):
        try:
            data = [
                        {
                        "seller_np": "webapi.magicpin.in/oms_partner/ondc",
                        "null_itm_cat": 590,
                        "total_orders": 75689,
                        },
                        {
                        "seller_np": "webapi.magicpin.in/oms_partner/ondc",
                        "null_itm_cat": 590,
                        "total_orders": 75689,
                        },
                        {
                        "seller_np": "webapi.magicpin.in/oms_partner/ondc",
                        "null_itm_cat": 590,
                        "total_orders": 75689,
                        },
                        {
                        "seller_np": "webapi.magicpin.in/oms_partner/ondc",
                        "null_itm_cat": 590,
                        "total_orders": 75689,
                        },
                        {
                        "seller_np": "webapi.magicpin.in/oms_partner/ondc",
                        "null_itm_cat": 590,
                        "total_orders": 75689,
                        },
                    ]
            
        except Exception as e:
            print("api for detail cancel data not loaded ", e)

        return Response(data=data)

class DetailCompletedTableData(APIView):
    """
        DetailCompletedTableData
    """
    
    def get(self, request):
        try:
            data = [
                        {
                        "seller_np": "webapi.magicpin.in/oms_partner/ondc",
                        "null_itm_cat": 590,
                        "total_orders": 75689,
                        },
                        {
                        "seller_np": "webapi.magicpin.in/oms_partner/ondc",
                        "null_itm_cat": 590,
                        "total_orders": 75689,
                        },
                        {
                        "seller_np": "webapi.magicpin.in/oms_partner/ondc",
                        "null_itm_cat": 590,
                        "total_orders": 75689,
                        },
                        {
                        "seller_np": "webapi.magicpin.in/oms_partner/ondc",
                        "null_itm_cat": 590,
                        "total_orders": 75689,
                        },
                        {
                        "seller_np": "webapi.magicpin.in/oms_partner/ondc",
                        "null_itm_cat": 590,
                        "total_orders": 75689,
                        },
                    ]
        
        except Exception as e:
            print("api for detail completed table data not loaded ", e)

        return Response(data=data)


class MissingOrdersTrend(APIView):
    """
        MissingOrdersTrend
    """
    
    def get(self, request):
        try:
            data = [
                        {
                        "title": "title 1",
                        "series": [
                        {
                            "name": "Bengaluru Urban",
                            "data": [
                            9323.0,
                            8519.0,
                            2850.0,
                            5634.0,
                            7109.0,
                            6971.0,
                            95128.0
                            ]
                        },
                        {
                            "name": "West Delhi",
                            "data": [
                            3526.0,
                            3337.0,
                            891.0,
                            2169.0,
                            943.0,
                            2024.0,
                            50588.0
                            ]
                        },
                        {
                            "name": "Hyderabad",
                            "data": [
                            2261.0,
                            2047.0,
                            859.0,
                            1332.0,
                            1359.0,
                            1740.0,
                            36857.0
                            ]
                        }
                        ],
                        "categories": [
                        "Nov-23",
                        "Dec-23",
                        "Jan-24",
                        "Feb-24",
                        "Mar-24",
                        "Apr-24",
                        "May-24"
                        ]
                    }

                ]
            
        except Exception as e:
            print("api for missing orders trend not loaded ", e)
        
        return Response(data=data)

class CancellationTrend(APIView):
    """
        CancellationTrend
    """
    
    def get(self, request):
        try:
            data = [
                    {
                        "title": "title 2",
                        "series": [
                    {
                        "name": "Bengaluru Urban",
                        "data": [
                        9323.0,
                        8519.0,
                        2850.0,
                        5634.0,
                        7109.0,
                        6971.0,
                        95128.0,
                        9323.0,
                        8519.0,
                        2850.0,
                        5634.0,
                        7109.0,
                        6971.0,
                        95128.0
                        ]
                    },
                    {
                        "name": "West Delhi",
                        "data": [
                        3526.0,
                        3337.0,
                        891.0,
                        2169.0,
                        943.0,
                        2024.0,
                        50588.0,
                        3526.0,
                        3337.0,
                        891.0,
                        2169.0,
                        943.0,
                        2024.0,
                        50588.0
                        ]
                    },
                    {
                        "name": "Hyderabad",
                        "data": [
                        2261.0,
                        2047.0,
                        859.0,
                        1332.0,
                        1359.0,
                        1740.0,
                        36857.0,
                        2261.0,
                        2047.0,
                        859.0,
                        1332.0,
                        1359.0,
                        1740.0,
                        36857.0
                        ]
                    },
                    {
                        "name": "Bengaluru Urban",
                        "data": [
                        9323.0,
                        8519.0,
                        2850.0,
                        5634.0,
                        7109.0,
                        6971.0,
                        95128.0,
                        9323.0,
                        8519.0,
                        2850.0,
                        5634.0,
                        7109.0,
                        6971.0,
                        95128.0
                        ]
                    },
                    {
                        "name": "West Delhi",
                        "data": [
                        3526.0,
                        3337.0,
                        891.0,
                        2169.0,
                        943.0,
                        2024.0,
                        50588.0,
                        3526.0,
                        3337.0,
                        891.0,
                        2169.0,
                        943.0,
                        2024.0,
                        50588.0
                        ]
                    },
                    {
                        "name": "Hyderabad",
                        "data": [
                        2261.0,
                        2047.0,
                        859.0,
                        1332.0,
                        1359.0,
                        1740.0,
                        36857.0,
                        2261.0,
                        2047.0,
                        859.0,
                        1332.0,
                        1359.0,
                        1740.0,
                        36857.0
                        ]
                    }
                    ],
                    "categories": [
                    "Nov-23",
                    "Dec-23",
                    "Jan-24",
                    "Feb-24",
                    "Mar-24",
                    "Apr-24",
                    "May-24",
                    "Nov-23",
                    "Dec-23",
                    "Jan-24",
                    "Feb-24",
                    "Mar-24",
                    "Apr-24",
                    "May-24"
                    ]
                }

            ]
            
        except Exception as e:
            print("api for cancellation trend api is not loaded ", e)
        return Response(data=data)
        
    
           
                