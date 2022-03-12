import asyncio

import services.MeetingService as MeetingService
from utils import InitService

if __name__ == '__main__':
    port, ConnectionString, listenAddress = InitService("MEETING")
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(MeetingService.beginServe(ConnectionString, port, listenAddress))
    except KeyboardInterrupt:
        loop.run_until_complete(MeetingService.endServe())
    finally:
        loop.close()
