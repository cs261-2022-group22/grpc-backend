from compiled_protos.meeting_package import ListAppointmentsReply, ProfileType
from utils.connection_pool import ConnectionPool

meetingServiceConnectionPool = ConnectionPool()


def list5AppointmentsByUserIdImpl(userid: int, profile_type: ProfileType) -> ListAppointmentsReply:
    return ListAppointmentsReply()
