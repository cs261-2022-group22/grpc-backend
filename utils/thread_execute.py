import asyncio
from concurrent.futures import ThreadPoolExecutor

# TODO: Allocate executor for each services
executor = ThreadPoolExecutor(16, 'worker_')


def shutdown_thread_pool():
    executor.shutdown(wait=True)


# TODO: Find a better way of doing this
async def run_in_thread(func, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None, arg8=None):
    if arg1 is None:
        return await asyncio.get_event_loop().run_in_executor(executor, func)
    elif arg2 is None:
        return await asyncio.get_event_loop().run_in_executor(executor, func, arg1)
    elif arg3 is None:
        return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2)
    elif arg4 is None:
        return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3)
    elif arg5 is None:
        return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3, arg4)
    elif arg6 is None:
        return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3, arg4, arg5)
    elif arg7 is None:
        return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3, arg4, arg5, arg6)
    elif arg8 is None:
        return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3, arg4, arg5, arg6, arg7)
    else:
        return await asyncio.get_event_loop().run_in_executor(executor, func, arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8)
