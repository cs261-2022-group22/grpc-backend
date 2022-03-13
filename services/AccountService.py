import datetime
from typing import List, Optional

from compiled_protos.account_package import (AccountServiceBase,
                                             AuthenticateReply,
                                             ListBusinessAreasReply,
                                             ListSkillsReply,
                                             NotificationsReply,
                                             ProfileSignupReply, ProfilesReply,
                                             ProfileType, RegistrationReply,
                                             UpdateProfileDetailsResponse)
from grpclib.server import Server
from utils.thread_execute import run_in_thread, shutdown_thread_pool

from services.AccountServiceImpl import (accountProfilesImpl,
                                         accountServiceConnectionPool,
                                         getNotificationsImpl,
                                         listBusinessAreasImpl, listSkillsImpl,
                                         registerProfileImpl, registerUserImpl,
                                         tryLoginImpl,
                                         updateProfileDetailsImpl)

gRPCServer: Server


class AccountService(AccountServiceBase):
    async def try_login(self, username: str, password: str) -> AuthenticateReply:
        return await run_in_thread(tryLoginImpl, username, password)

    async def register_user(self, name: str, date_of_birth: datetime, email: str, password: str, business_area_id: int) -> RegistrationReply:
        return await run_in_thread(registerUserImpl, name, date_of_birth, email, password, business_area_id)

    async def account_profiles(self, userid: int) -> ProfilesReply:
        return await run_in_thread(accountProfilesImpl, userid)

    async def list_business_areas(self) -> ListBusinessAreasReply:
        return await run_in_thread(listBusinessAreasImpl)

    async def get_notifications(self, userid: int, target_profile_type: ProfileType) -> NotificationsReply:
        return await run_in_thread(getNotificationsImpl, userid, target_profile_type)

    async def register_mentee(self, userid: int, desired_skills: list[str]) -> ProfileSignupReply:
        return await run_in_thread(registerProfileImpl, userid, desired_skills, "Mentee")

    async def list_skills(self) -> ListSkillsReply:
        return await run_in_thread(listSkillsImpl)

    async def register_mentor(self, userid: int, desired_skills: list[str]) -> ProfileSignupReply:
        return await run_in_thread(registerProfileImpl, userid, desired_skills, "Mentor")

    async def update_profile_details(self, userid: int, profile_type: ProfileType, new_email: Optional[str], new_bs_id: Optional[int], skills: Optional[List[int]]) -> UpdateProfileDetailsResponse:
        return await run_in_thread(updateProfileDetailsImpl, userid, profile_type, new_email, new_bs_id, skills)


async def beginServe(connectionString: str, port: int, listenAddress: str):
    accountServiceConnectionPool.initialise_connection_pool(connectionString)

    global gRPCServer
    gRPCServer = Server([AccountService()])
    await gRPCServer.start(listenAddress, port)
    print(f"Account Service Server started. Listening on {listenAddress}:{port}")
    await gRPCServer.wait_closed()


async def endServe():
    print("Stopping Account Service...")
    shutdown_thread_pool()

    # clean up connection pool
    accountServiceConnectionPool.shutdown_connection_pool()

    global gRPCServer
    gRPCServer.close()
    await gRPCServer.wait_closed()
    print("Account Service Stopped.")
