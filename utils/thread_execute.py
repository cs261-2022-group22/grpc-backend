import asyncio
from concurrent.futures import ThreadPoolExecutor

from utils import CONCURRENCY_SIZE

# TODO: Allocate executor for each services
executor = ThreadPoolExecutor(CONCURRENCY_SIZE, 'worker_')


def shutdown_thread_pool():
    executor.shutdown(wait=True)


async def run_in_thread(func, *args, **kwargs):
    return await asyncio.get_event_loop().run_in_executor(executor, func, *args, **kwargs)
