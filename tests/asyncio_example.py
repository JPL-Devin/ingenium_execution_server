import json
import asyncio
import time

async def count():
    print("One")
    await asyncio.sleep(1)
    print("Two")

async def main1():
    await asyncio.gather(count(), count(), count())

def test1():
    s = time.perf_counter()
    asyncio.run(main1())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")

def test2():
    s = time.perf_counter()
    asyncio.run(count())
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")

if __name__ == "__main__":
    # test1()
    test2()
