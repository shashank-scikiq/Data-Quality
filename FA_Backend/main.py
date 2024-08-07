from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import json

from Logic import base_queries as bq

current_dir = os.path.dirname(os.path.realpath(__file__))
json_file = "API/api_struct.json"

app = FastAPI()

# dir_lib = os.path.join(current_dir, "Web/lib/")
# dir_assets = os.path.join(current_dir, "Web/assets/")
# app.mount("/lib", StaticFiles(directory=dir_lib), name="libraries")
# app.mount("/assets", StaticFiles(directory=dir_assets), name="assets")

static_dir = os.path.join(current_dir, "static/ng-workspace/dist/data_quality/browser/static/")
static_build_dir = os.path.join(current_dir, "static/ng-workspace/dist/data_quality/browser/")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/build", StaticFiles(directory=static_build_dir), name="static")

# All Results in Json format
with open(json_file, "r") as f:
    data = f.read()
result = json.loads(data)


# Serve the custom HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = os.path.join(current_dir, "static/ng-workspace/dist/data_quality/browser/index.html")
    # html_path = os.path.join(current_dir, "Web/index.html")
    return FileResponse(html_path)


@app.get("/api/dq_report/top_card/")
async def top_card():
    resp = result["dq_report"]["top_card"]
    return JSONResponse(content=resp)


@app.get("/api/dq/missing_percentage/")
async def missing_percentage():
    resp = result["missing_percentage"]
    return JSONResponse(content=resp)


@app.get("/api/retail/overall/get-max-date/")
async def get_max_date():
    dt_rng = bq.get_date_range()
    resp = {
        "min_date": dt_rng[0].strftime("%Y-%m-%d"),
        "max_date": dt_rng[1].strftime("%Y-%m-%d")
    }
    print(resp)
    return JSONResponse(content=resp)


@app.get("/api/dq_report/trend_1/")
async def trend_missing_orders():
    resp = result["dq_report"]["trend"]["missing_orders"]
    return JSONResponse(content=resp)


@app.get("/api/dq_report/trend_2/")
async def trend_cancellation():
    resp = result["dq_report"]["trend"]["cancellation"]
    return JSONResponse(content=resp)


@app.get("/api/dq_report/detail_completed_table_data/")
async def tbl_detail_completed():
    resp = result["dq_report"]["detail_completed_table_data"]
    return JSONResponse(content=resp)


@app.get("/api/dq_report/detail_cancel_table_data/")
async def tbl_detail_cancelled():
    resp = result["dq_report"]["detail_cancel_table_data"]
    return JSONResponse(content=resp)


@app.get("/api/dq_report/cancel_highest_missing_pid_data/")
async def cancel_highest_missing_pids():
    resp = result["dq_report"]["cancel_highest_missing_pid_data"]
    return JSONResponse(content=data)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
