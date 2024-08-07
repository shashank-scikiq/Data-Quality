from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

current_dir = os.path.dirname(os.path.realpath(__file__))

app = FastAPI()

static_dir = os.path.join(current_dir, "static/dist/data_quality/browser/static/")
static_build_dir = os.path.join(current_dir, "static/dist/data_quality/browser/")# Path to the static directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/build", StaticFiles(directory=static_build_dir), name="static")


# Serve the custom HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = os.path.join(current_dir, "static/dist/data_quality/browser/index.html")
    return FileResponse(html_path)


# Define the API endpoint
@app.get("/api/data")
async def get_data():
    data = {"message": "Hello from FastAPI!"}
    return JSONResponse(content=data)


@app.get("/api/dq_report/top_card")
async def get_data():
    data = [{'title': 'Total Orders',
            'count': '200731',
            'increased': False,
            'variancePercentage': '-3.9753',
            'varianceText': 'vs Yesterday'},
            {'title': 'Cancelled Orders',
            'count': '3796',
            'increased': True,
            'variancePercentage': '5.9743',
            'varianceText': 'vs Yesterday'},
            {'title': 'Order Cancellation %',
            'count': '0.0189',
            'increased': True,
            'variancePercentage': '10.5263',
            'varianceText': 'vs Yesterday'},
            {'title': 'Order Completion %',
            'count': '0.9811',
            'increased': False,
            'variancePercentage': '-0.1831',
            'varianceText': 'vs Yesterday'}]
    return JSONResponse(content=data)


@app.get("/api/dq/missing_percentage")
async def get_data():
    data = [{'title': 'Delivery City', 'series': [3.2192]},
            {'title': 'Item Category', 'series': [0.3527]},
            {'title': 'Category', 'series': [3.7428]},
            {'title': 'Seller Pincode', 'series': [0.0085]},
            {'title': 'Seller City', 'series': [0.0085]}
            ]
    return JSONResponse(content=data)


@app.get("/api/retail/overall/get-max-date")
async def get_data():
    return JSONResponse(content={"min_date": "2023-11-01", "max_date": "2024-06-30"})


@app.get("/api/dq_report/trend_1")
async def get_data():
    data = {
    "title": "title 1",
    "series": [
      {
        "name": "Delivery City",
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
        "name": "Item Category",
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
        "name": "Category",
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
    return JSONResponse(content=data)


@app.get("/api/dq_report/trend_2")
async def get_data():
    data = {
    "title": "title 1",
    "series": [
      {
        "name": "Delivery City",
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
        "name": "Item Category",
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
        "name": "Category",
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
    return JSONResponse(content=data)


@app.get("/api/dq_report/detail_completed_table_data")
async def get_data():
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
    return JSONResponse(content=data)


@app.get("/api/dq_report/detail_cancel_table_data")
async def get_data():
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
    return JSONResponse(content=data)


@app.get("/api/dq_report/cancel_highest_missing_pid_data")
async def get_data():
    data = [
    {
      "id": "ondc-otipy.crofarm.com",
      "count": "0.81%",
      "increased": True,
      "variancePercentage": "1.2%",
      "varianceText": "vs. Yesterday"
    },
    {
      "id": "ondc-otipy.crofarm.com",
      "count": "0.81%",
      "increased": True,
      "variancePercentage": "1.2%",
      "varianceText": "vs. Yesterday"
    },
    {
      "id": "ondc-otipy.crofarm.com",
      "count": "0.81%",
      "increased": True,
      "variancePercentage": "1.2%",
      "varianceText": "vs. Yesterday"
    }
  ]
    return JSONResponse(content=data)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
