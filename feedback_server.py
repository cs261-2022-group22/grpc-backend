import asyncio

import services.FeedbackService as FeedbackService
from utils import InitService

if __name__ == '__main__':
    port, ConnectionString, listenAddress = InitService("FEEDBACK")
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(FeedbackService.beginServe(ConnectionString, port, listenAddress))
    except KeyboardInterrupt:
        loop.run_until_complete(FeedbackService.endServe())
    finally:
        loop.close()
