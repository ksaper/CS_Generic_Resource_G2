from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.cli.service.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.service.command_mode import CommandMode
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.shell.core.driver_context import InitCommandContext, ResourceCommandContext, AutoLoadResource, \
    AutoLoadAttribute, AutoLoadDetails, CancellationContext
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from log_helper import LogHelper
from re import sub
from data_model import *  # run 'shellfoundry generate' to generate data model classes


class CsGenericResourceG2Driver (ResourceDriverInterface):
    class UnImplementedCliConnectionType(Exception):
        pass

    class UnSupportedCliConnectionType(Exception):
        pass

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        pass

    def __init__(self):
        self.address = None
        self.cli = None
        self.cli_connection_type = None
        self.cli_prompt_regex = None
        self.cli_session = None
        self.cs_session = None
        self.mode = None
        self.password_hash = None
        self.session_types = None
        self.user = None
        self.resource = None

    def initialize(self, context):
        self.cli = CLI()

    def get_inventory(self, context):
        self.run_command(context, 'hostname')

        return AutoLoadDetails()

    def run_command(self, context, command):
        """

        :param ResourceCommandContext context:
        :param str command:
        :return:
        """
        logger = LogHelper.get_logger(context)
        logger.info(context)
        logger.info('Command: {}'.format(command))

        self._cli_session_handler(context)

        self.cs_session.WriteMessageToReservationOutput(context.reservation.reservation_id,
                                                        '\n> Running "{}" command now:\n'.format(command))

        with self.cli.get_session(self.session_types, self.mode, logger) as default_session:
            output = default_session.send_command(command)
            logger.info(output)

        # self.cs_session.WriteMessageToReservationOutput(context.reservation.reservation_id, x_return)

        return sub(self.cli_prompt_regex, '', output)

    def _cs_session_handler(self, context):
        """

        :param ResourceCommandContext context:
        :return:
        """
        self.resource = CsGenericResourceG2.create_from_context(context)

        self.address = context.resource.address
        assert self.address, 'Address cannot be blank'

        self.user = self.resource.user
        assert self.user, 'User Attribute cannot be blank'

        self.password_hash = self.resource.password
        assert self.password_hash, 'Password Attribute cannot be blank'

        domain = None
        try:
            domain = context.reservation.domain
        except AttributeError:
            domain = 'Global'

        self.cs_session = CloudShellAPISession(host=context.connectivity.server_address,
                                               token_id=context.connectivity.admin_auth_token,
                                               domain=domain)

    def _cli_session_handler(self, context):
        """

        :param ResourceCommandContext context:
        :return:
        """
        self._cs_session_handler(context)
        logger = LogHelper.get_logger(context)

        self.cli_connection_type = self.resource.attributes.get('cli_connection_type', 'Auto')
        self.cli_prompt_regex = self.resource.attributes.get('cli_prompt_regex', '[#>$]')
        self.mode = CommandMode(self.cli_prompt_regex)
        self.session_types = None

        logger.info('CLI Connection Type: "{}"'.format(self.cli_connection_type))
        logger.info('CLI Prompt Regular Expression: "{}"'.format(self.cli_prompt_regex))
        logger.info('Hashed Password: {}'.format(self.password_hash))
        logger.info('Full Resource Attributes: {}'.format(self.resource.attributes))

        if self.cli_connection_type == 'Auto':
            self.session_types = [SSHSession(host=self.address,
                                             username=self.user,
                                             password=self.cs_session.DecryptPassword(self.password_hash).Value),
                                  TelnetSession(host=self.address,
                                                username=self.user,
                                                password=self.cs_session.DecryptPassword(self.password_hash).Value)]
        elif self.cli_connection_type == 'Console':
            message = 'Unimplemented CLI Connection Type: "{}"'.format(self.cli_connection_type)
            logger.error(message)
            raise CsGenericResourceG2Driver.UnImplementedCliConnectionType(message)
        elif self.cli_connection_type == 'SSH':
            self.session_types = [SSHSession(host=self.address,
                                             username=self.user,
                                             password=self.cs_session.DecryptPassword(self.password_hash).Value)]
        elif self.cli_connection_type == 'TCP':
            message = 'Unimplemented CLI Connection Type: "{}"'.format(self.cli_connection_type)
            logger.error(message)
            raise CsGenericResourceG2Driver.UnImplementedCliConnectionType(message)
        elif self.cli_connection_type == 'Telnet':
            self.session_types = [TelnetSession(host=self.address,
                                                username=self.user,
                                                password=self.cs_session.DecryptPassword(self.password_hash).Value)]
        else:
            message = 'Unsupported CLI Connection Type: "{}"'.format(self.cli_connection_type)
            logger.error(message)
            raise CsGenericResourceG2Driver.UnSupportedCliConnectionType(message)

    # </editor-fold>

    # <editor-fold desc="Orchestration Save and Restore Standard">
    def orchestration_save(self, context, cancellation_context, mode, custom_params):
      """
      Saves the Shell state and returns a description of the saved artifacts and information
      This command is intended for API use only by sandbox orchestration scripts to implement
      a save and restore workflow
      :param ResourceCommandContext context: the context object containing resource and reservation info
      :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
      :param str mode: Snapshot save mode, can be one of two values 'shallow' (default) or 'deep'
      :param str custom_params: Set of custom parameters for the save operation
      :return: SavedResults serialized as JSON
      :rtype: OrchestrationSaveResult
      """

      # See below an example implementation, here we use jsonpickle for serialization,
      # to use this sample, you'll need to add jsonpickle to your requirements.txt file
      # The JSON schema is defined at:
      # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/saved_artifact_info.schema.json
      # You can find more information and examples examples in the spec document at
      # https://github.com/QualiSystems/sandbox_orchestration_standard/blob/master/save%20%26%20restore/save%20%26%20restore%20standard.md
      '''
            # By convention, all dates should be UTC
            created_date = datetime.datetime.utcnow()

            # This can be any unique identifier which can later be used to retrieve the artifact
            # such as filepath etc.

            # By convention, all dates should be UTC
            created_date = datetime.datetime.utcnow()

            # This can be any unique identifier which can later be used to retrieve the artifact
            # such as filepath etc.
            identifier = created_date.strftime('%y_%m_%d %H_%M_%S_%f')

            orchestration_saved_artifact = OrchestrationSavedArtifact('REPLACE_WITH_ARTIFACT_TYPE', identifier)

            saved_artifacts_info = OrchestrationSavedArtifactInfo(
                resource_name="some_resource",
                created_date=created_date,
                restore_rules=OrchestrationRestoreRules(requires_same_resource=True),
                saved_artifact=orchestration_saved_artifact)

            return OrchestrationSaveResult(saved_artifacts_info)
      '''
      pass

    def orchestration_restore(self, context, cancellation_context, saved_artifact_info, custom_params):
        """
        Restores a saved artifact previously saved by this Shell driver using the orchestration_save function
        :param ResourceCommandContext context: The context object for the command with resource and reservation info
        :param CancellationContext cancellation_context: Object to signal a request for cancellation. Must be enabled in drivermetadata.xml as well
        :param str saved_artifact_info: A JSON string representing the state to restore including saved artifacts and info
        :param str custom_params: Set of custom parameters for the restore operation
        :return: None
        """
        '''
        # The saved_details JSON will be defined according to the JSON Schema and is the same object returned via the
        # orchestration save function.
        # Example input:
        # {
        #     "saved_artifact": {
        #      "artifact_type": "REPLACE_WITH_ARTIFACT_TYPE",
        #      "identifier": "16_08_09 11_21_35_657000"
        #     },
        #     "resource_name": "some_resource",
        #     "restore_rules": {
        #      "requires_same_resource": true
        #     },
        #     "created_date": "2016-08-09T11:21:35.657000"
        #    }

        # The example code below just parses and prints the saved artifact identifier
        saved_details_object = json.loads(saved_details)
        return saved_details_object[u'saved_artifact'][u'identifier']
        '''
        pass

    # </editor-fold>
