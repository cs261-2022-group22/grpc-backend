import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(16, 'worker_')

# Python doesn't support varadic parameter forwarding, so we use function overloading...
# TODO: Find a better way


async def run_in_thread(func):
    return await asyncio.get_event_loop().run_in_executor(executor, func)


async def run_in_thread(func, arg):
    return await asyncio.get_event_loop().run_in_executor(executor, func, arg)


async def run_in_thread(func, arg1, arg2):
    return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2)


async def run_in_thread(func, arg1, arg2, arg3):
    return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3)


async def run_in_thread(func, arg1, arg2, arg3, arg4):
    return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3, arg4)


async def run_in_thread(func, arg1, arg2, arg3, arg4, arg5):
    return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3, arg4, arg5)


async def run_in_thread(func, arg1, arg2, arg3, arg4, arg5, arg6):
    return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3, arg4, arg5, arg6)


async def run_in_thread(func, arg1, arg2, arg3, arg4, arg5, arg6, arg7):
    return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3, arg4, arg5, arg6, arg7)


async def run_in_thread(func, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8):
    return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8)
