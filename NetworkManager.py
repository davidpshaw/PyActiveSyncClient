__author__ = 'davidshaw'

from datetime import datetime
import logging
import requests
from requests.auth import HTTPBasicAuth
from ASEnums import STATE_STATUS, EXCHANGE_PROTOCOL_ORDER

# max time in minutes between OPTIONS commands
MAX_INTERVAL_FOR_OPTIONS = 4



class NetworkManager:
    def __init__(self, config):
        self.http_session = None                        # HTTP Requests Session object, None if invalid
        self.options_last_updated = None                # holds the last datetime we ran OPTIONS successfully
        self.server_policy_key = None                   # holds the Exchange policy key from provisioning
        self.supported_versions = None                  # e.g. '2.0,2.1,2.5,12.0,12.1,14.0,14.1'
        self.supported_commands = None                  # e.g. 'Sync,SendMail,SmartForward,SmartReply,...'
        self.server_protocol = None                     # Server protocol,  e.g. '14.3'
        self.server_type = None                         # Server type,      e.g. 'Microsoft-IIS/7.5'
        self.negotiated_protocol = None                 # protocol that both client and server can use

        self.url = self.build_url(config['protocol'],   # 'protocol://server/Microsoft-Server-ActiveSync
                                 config['host'])

        self.username = config['username']              # ActiveSync username
        self.password = config['password']              # ActiveSync password
        self.domain = config['domain']                  # ActiveSync (or Active Directory) domain


    def build_url(self, protocol, host):
        url = "%s://%s/Microsoft-Server-ActiveSync" % (protocol, host)
        logging.debug("Server url: %s" % url)
        return url

    def build_authentication_credential(self, domain, username, password):
        if (username is not None and len(username) > 0 and password is not None and len(password) > 0):
            if (domain is not None and len(domain) > 0 ):
                username = "%s\\%s" % ( domain, username )
            else:
                username = username

            self.http_session.auth = HTTPBasicAuth(username, password)
            return (STATE_STATUS.SUCCESS, None)
        else:
            return (STATE_STATUS.USER_FIX, "Please provide valid credentials")

    # return True if we should run the OPTIONS command
    def is_options_required(self):
        return (self.options_last_updated is None or
                self.datetime_interval_minutes(self.options_last_updated, datetime.now()) > MAX_INTERVAL_FOR_OPTIONS)

    # return True if we have a valid policy key
    def is_policy_key_valid(self):
        return (self.server_policy_key is not None)

    # return the interval in minutes between two datetimes
    def datetime_interval_minutes(self, dt1, dt2):
        return ((dt2 - dt1).seconds/60.0)

    # this is a placeholder for other languages, here we might change the closure method to not handle results
    def stop_all_network_commands(self):
        # No way to do this in python really
        pass

    def negotiate_activesync_protocol_version(self, server_list):
        for version in EXCHANGE_PROTOCOL_ORDER:
            if version in server_list:
                self.negotiated_protocol = version
                return (STATE_STATUS.SUCCESS, 'None')
        logging.error("Could not find a match in the server protocols: %s" % (server_list.join(",")))
        return (STATE_STATUS.ADMIN_FIX, 'Get a compatible Exchange server')

    # EACH Method is synchronous and returns (STATUS, DESCRIPTION) as a Tuple.
    # Status of STATE_STATUS.SUCCESS is success, other statuses are errors errors
    # If the status is success, the description might be None
    def perform_options(self, error_handler):
        if ( self.http_session is None ):
            (status, message) = self.init_http_session()
            if (status != STATE_STATUS.SUCCESS):
                return (status,  message)

        url = self.url
        options_request = self.http_session.options(url)
        status_code = options_request.status_code

        if ( 200 <= status_code < 300 ):
            server_info = options_request.headers
            self.options_last_updated = datetime.now()

            self.supported_versions = server_info['ms-asprotocolversions'].split(",")
            self.supported_commands = server_info['ms-asprotocolcommands'].split(",")
            self.server_protocol = server_info['ms-server-activesync']
            self.server_type = server_info['server']

            (status, message) = self.negotiate_activesync_protocol_version(EXCHANGE_PROTOCOL_ORDER)
            if (status == STATE_STATUS.SUCCESS):
                logging.info("OPTIONS was successful, negotiated protocol %s" % self.negotiated_protocol)
                return (STATE_STATUS.SUCCESS, None)
            else:
                return (status, message)
        else:
            return error_handler(status_code, "Unsuccessful")

    # perform Provision to get a valid ActiveSync policy key
    def perform_provisioning(self):
        self.stop_all_network_commands()

        self.server_policy_key = "FAKE_KEY"
        logging.info("PROVISIONING was successful, new policy key is %s" % self.server_policy_key)
        return (STATE_STATUS.SUCCESS, None)

    # perform Folder Sync
    def perform_foldersync(self):
        logging.info("FOLDERSYNC was successful, folder sync key was X")
        return (STATE_STATUS.SUCCESS, None)

    # Initialize the HTTP session
    def init_http_session(self):
        self.http_session = requests.session()
        #self.http_session.verify = False # ignore SSL errors
        self.http_session.headers.update({
                                            'User-Agent': 'AirWatch Inbox Apple/iOS 2.5'
                                        })
        (status, message) = self.build_authentication_credential(self.domain, self.username, self.password)
        return (status, message)

    def clear_http_session(self):
        self.http_session = None

    def clear_policy_key(self):
        self.server_policy_key = None

