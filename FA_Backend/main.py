from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache

import os
import json

from Logic import base_queries as bq
from Logic import API_calls as ac

current_dir = os.path.dirname(os.path.realpath(__file__))
json_file = "API/api_struct.json"

app = FastAPI()

origins = [
    "http://localhost:4200",  # Angular dev server
    "http://localhost:8000",  # Angular dev server
    # Add any other origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# dir_lib = os.path.join(current_dir, "Web/lib/")
# dir_assets = os.path.join(current_dir, "Web/assets/")
# app.mount("/lib", StaticFiles(directory=dir_lib), name="libraries")
# app.mount("/assets", StaticFiles(directory=dir_assets), name="assets")

static_dir = os.path.join(current_dir, "static/ng-workspace/dist/dq-report/browser/static/")
static_build_dir = os.path.join(current_dir, "static/ng-workspace/dist/dq-report/browser/")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/dq", StaticFiles(directory=static_build_dir), name="static")


@app.get("/api/get-max-date/")
async def get_max_date():
    dt_rng = bq.get_date_range()
    resp = {
        "min_date": dt_rng[0].strftime("%Y-%m-%d"),
        "max_date": dt_rng[1].strftime("%Y-%m-%d")
    }
    print(resp)
    return JSONResponse(content=resp)


# Serve the custom HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = os.path.join(static_build_dir, "index.html")
    # html_path = os.path.join(current_dir, "Web/index.html")
    return FileResponse(html_path)


@app.get("/api/get/sellers/{date_val}")
async def sellers_by_mnth(date_val):
    return "test"


@app.get("/api/dq_report/top_card/")
async def top_card():
    resp = ac.top_cards_delta()
    # resp = result["dq_report"]["top_card"]
    return JSONResponse(content=resp)


@app.get("/api/dq/missing_percentage/")
async def missing_percentage():
    # resp = result["missing_percentage"]
    resp = ac.missing_percentage()
    return JSONResponse(content=resp)


@app.get("/api/dq_report/trend_1/")
async def trend_missing_orders():
    resp = ac.trend_chart()
    return JSONResponse(content=resp)


@app.get("/api/dq_report/detail_completed_table_data/")
async def tbl_detail_completed():
    resp = ac.detailed_completed_table()
    return JSONResponse(content=resp)


@app.get("/api/dq_report/detail_cancel_table_data/")
async def tbl_detail_cancelled():
    resp = ac.detailed_cancelled_table()
    return JSONResponse(content=resp)


@app.get("/api/dq_report/cancel_highest_missing_pid_data/")
async def cancel_highest_missing_pids():
    resp = ac.missing_per_by_seller()
    print(resp)
    return JSONResponse(content=resp)


# DATA SANITY APIS
@lru_cache(maxsize=32)
async def get_ds_last_run_date_report():
    return ac.data_sanity_last_run_date_report()


@app.get("/api/dq_report/data_sanity/last_run_date_data/")
async def get_last_run_date_report():
    resp = get_ds_last_run_date_report()
    return JSONResponse(content=resp)


@lru_cache(maxsize=32)
async def get_ds_variance_report():
    return ac.ds_variance_data_report()


@app.get("/api/dq_report/data_sanity/variance_data/")
async def get_last_run_date_report():
    resp = get_ds_variance_report()
    return JSONResponse(content=resp)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
