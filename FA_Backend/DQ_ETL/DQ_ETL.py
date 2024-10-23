from .Extract_data import extractData
from .Load_data import dqLoadDb


if __name__ == "__main__":
    asyncio.run(extractData())

def etlMain():
    print(od_dq_base.name)
    asyncio.run(dqLoadDb("D:\\DATA_DUMP\\DATA_QUALITY\\DATA_QUALITY_2024-10-22\\"))
