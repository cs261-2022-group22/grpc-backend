from compiled_protos.meeting_package import (ListAppointmentsReply,
                                             MeetingServiceBase, ProfileType)
from grpclib.server import Server
from utils.thread_execute import run_in_thread, shutdown_thread_pool

from services.MeetingServiceImpl import (list5AppointmentsByUserIdImpl,
                                         meetingServiceConnectionPool)

gRPCServer: Server


class MeetingService(MeetingServiceBase):
    async def list5_appointments_by_user_id(self, userid: int, profile_type: ProfileType) -> ListAppointmentsReply:
        return await run_in_thread(list5AppointmentsByUserIdImpl, userid, profile_type)


async def beginServe(connectionString: str, port: int):
    meetingServiceConnectionPool.initialise_connection_pool(connectionString)

    global gRPCServer
    gRPCServer = Server([MeetingService()])
    await gRPCServer.start("127.0.0.1", port)
    print("Meeting Service Server started. Listening on port:", port)
    await gRPCServer.wait_closed()


async def endServe():
    print("Stopping Meeting Service...")
    shutdown_thread_pool()

    # clean up connection pool
    meetingServiceConnectionPool.shutdown_connection_pool()

    global gRPCServer
    gRPCServer.close()
    await gRPCServer.wait_closed()
    print("Meeting Service Stopped.")
