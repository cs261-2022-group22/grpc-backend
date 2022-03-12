from datetime import datetime

from compiled_protos.meeting_package import (
    CreatePlansOfActionsReply, ListAppointmentsReply, ListPlansOfActionsReply,
    MeetingServiceBase, ProfileType, ScheduleNewMeetingReply,
    ScheduleNewWorkshopReply, TogglePlansOfActionCompletionReply)
from grpclib.server import Server
from utils.thread_execute import run_in_thread, shutdown_thread_pool

from services.MeetingServiceImpl import (createPlansOfActionsImpl,
                                         list5AppointmentsByUserIdImpl,
                                         listPlansOfActionsImpl,
                                         meetingServiceConnectionPool,
                                         scheduleNewMeetingImpl,
                                         scheduleNewWorkshopImpl,
                                         togglePlansOfActionCompletionImpl)

gRPCServer: Server


class MeetingService(MeetingServiceBase):
    async def list5_appointments_by_user_id(self, userid: int, profile_type: ProfileType) -> ListAppointmentsReply:
        return await run_in_thread(list5AppointmentsByUserIdImpl, userid, profile_type)

    async def list_plans_of_actions(self, userid: int) -> ListPlansOfActionsReply:
        return await run_in_thread(listPlansOfActionsImpl, userid)

    async def toggle_plans_of_action_completion(self, planid: int) -> TogglePlansOfActionCompletionReply:
        return await run_in_thread(togglePlansOfActionCompletionImpl, planid)

    async def create_plans_of_actions(self, mentee_user_id: int,  plans_of_action: str) -> CreatePlansOfActionsReply:
        return await run_in_thread(createPlansOfActionsImpl, mentee_user_id, plans_of_action)

    async def schedule_new_meeting(self, mentee_user_id: int, start: datetime, duration: int, link: str) -> ScheduleNewMeetingReply:
        return await run_in_thread(scheduleNewMeetingImpl, mentee_user_id, start, duration, link)

    async def schedule_new_workshop(self, start: datetime, duration: int, link: str, skill: str) -> ScheduleNewWorkshopReply:
        return await run_in_thread(scheduleNewWorkshopImpl, start, duration, link, skill)


async def beginServe(connectionString: str, port: int, listenAddress: str):
    meetingServiceConnectionPool.initialise_connection_pool(connectionString)

    global gRPCServer
    gRPCServer = Server([MeetingService()])
    await gRPCServer.start(listenAddress, port)
    print(f"Meeting Service Server started. Listening on {listenAddress}:{port}")
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
