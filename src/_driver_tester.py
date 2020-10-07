from driver import CsGenericResourceG2Driver
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, CancellationContext, ResourceRemoteCommandContext, AutoLoadCommandContext
import cloudshell.api.cloudshell_api
# from os import getcwd
# from os.path import exists
# import os
# from time import sleep


class RequestObj:
    def __init__(self):
        pass


def main():
    import mock

    shell_name = 'CsGenericResourceG2Driver'

    context = mock.create_autospec(ResourceCommandContext)
    context.resource = mock.MagicMock()
    context.reservation = mock.MagicMock()
    context.connectivity = mock.MagicMock()

    context.reservation.reservation_id = "e59a199c-5e35-4d36-ae78-0644bdc2564e"
    context.reservation.domain = "Global"

    context.resource.name = 'K8_Test'
    context.resource.type = 'Resource'

    context.resource.attributes = dict()
    context.resource.attributes['Generic Resource.User'] = 'svc-user'
    context.resource.attributes['Generic Resource.Password'] = 'zc875XaBH47UmlShANhoSA=='

    # TESTING ONLY ATTRIBUTE
    context.resource.attributes['DEBUG_LOGGING'] = True

    context.connectivity.server_address = 'ksaper.homeip.net'
    # context.connectivity.server_address = "169.60.207.83"
    context.connectivity.cloudshell_api_port = "8029"
    context.connectivity.cloudshell_api_scheme = "http"
    context.connectivity.cloudshell_version = "9.0"
    context.connectivity.quali_api_port = "9000"

    temp_api = cloudshell.api.cloudshell_api.CloudShellAPISession(host=context.connectivity.server_address,
                                                                  username="admin",
                                                                  password="theCS_@dm1n?",
                                                                  domain='Global')

    # temp_api = cloudshell.api.cloudshell_api.CloudShellAPISession(host=context.connectivity.server_address,
    #                                                               username="admin",
    #                                                               password="TSIeda101!",
    #                                                               domain='Global')

    context.connectivity.admin_auth_token = temp_api.token_id

    # d_session = cloudshell.api.cloudshell_api.CloudShellAPISession(host='ksaper.homeip.net',
    #                                                                token_id=temp_api.token_id,
    #                                                                domain='Global')
    # current_res = d_session.GetCurrentReservations('admin').Reservations

    driver = CsGenericResourceG2Driver()
    driver.run_command(context=context, command='ifconfig')


if __name__ == "__main__":
    main()
