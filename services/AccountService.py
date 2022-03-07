import datetime

from compiled_protos.account_package import (AccountServiceBase,
                                             AuthenticateReply,
                                             ListBusinessAreasReply, ProfileType,
                                             ProfilesReply, RegistrationReply, 
                                             NotificationsReply, 
                                             MenteeSignupReply)
from grpclib.server import Server
from utils.thread_execute import run_in_thread, shutdown_thread_pool

from services.AccountServiceImpl import (accountProfilesImpl, 
                                         listBusinessAreasImpl,
                                         registerUserImpl, tryLoginImpl, 
                                         getNotificationsImpl, 
                                         registerMenteeImpl, 
                                         accountServiceConnectionPool)

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

    async def register_mentee(self, userid: int, desired_skills: list[str]) -> MenteeSignupReply:
        return await run_in_thread(registerMenteeImpl, userid, desired_skills)
        

async def beginServe(connectionString: str, port: int):
    accountServiceConnectionPool.initialise_connection_pool(connectionString)

    global gRPCServer
    gRPCServer = Server([AccountService()])
    await gRPCServer.start("127.0.0.1", port)
    print("Account Service Server started. Listening on port:", port)
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
