import asyncio
import services.FeedbackService as FeedbackService
from utils import InitService

if __name__ == '__main__':
    port, ConnectionString = InitService("FEEDBACK_SERVICE_PORT")
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(FeedbackService.beginServe(ConnectionString, port))
    except KeyboardInterrupt:
        loop.run_until_complete(FeedbackService.endServe())
    finally:
        loop.close()
