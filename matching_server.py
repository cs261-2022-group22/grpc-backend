import asyncio
import services.MatchingService as MatchingService
from utils import InitService

if __name__ == '__main__':
    port, ConnectionString = InitService("MATCHING_SERVICE_PORT")
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(MatchingService.beginServe(ConnectionString, port))
    except KeyboardInterrupt:
        loop.run_until_complete(MatchingService.endServe())
    finally:
        loop.close()
