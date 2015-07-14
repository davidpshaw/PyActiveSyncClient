__author__ = 'davidshaw'

import os
import json
import thread
import time
import logging

from NetworkManager import NetworkManager
from ASEnums import SYNC_STATE, STATE_STATUS

class ActiveSyncEngine:
    def __init__(self, passed_config):
        self.state = SYNC_STATE.STOP
        self.config = passed_config
        self.network = NetworkManager(passed_config)

    def start(self):
        thread.start_new_thread(self.start_sync_engine, ())

    def stop_sync_engine(self, error_message=None):
        logging.info("Sync stopped: %s" % error_message)
        self.state = SYNC_STATE.STOP

    # threaded sync engine
    def start_sync_engine(self):
        logging.info("Beginning sync")
        self.state = SYNC_STATE.START

        # Question 1, do I know my server with certainty (updated in the last 10 minutes for now, 24 hours eventually)
        if (self.network.is_options_required()):
            logging.debug("NEED to send OPTIONS")
            (status, message) = self.network.perform_options(self.handle_http_error)
            if (status != STATE_STATUS.SUCCESS):
                self.stop_sync_engine(message)
                logging.fatal("Fatal error with options (%s - %s)" % (status, message))

        else:
            logging.debug("DO NOT NEED to send OPTIONS")

        # Question 2, do I have a policy key?
        if (not self.network.is_policy_key_valid()):
            logging.debug("NEED to send PROVISIONING")
            (status, message) = self.network.perform_provisioning()
            if (status != STATE_STATUS.SUCCESS):
                self.stop_sync_engine()
                return
        else:
            logging.debug("DO NOT NEED to send OPTIONS")

        # Startup always includes a FolderSync
        (status, message) = self.network.perform_foldersync()
        if (status != STATE_STATUS.SUCCESS):
                self.stop_sync_engine()
                return

        # Startup always includes one or more Syncs

    # Add all HTTP error codes here and some sort of remediation
    def handle_http_error(self, status_code, message):
        self.network.clear_http_session()
        logging.fatal("Fatal error, %d is not a good code! (%s)" % (status_code, message))
        return (status_code, "EPIC FAIL")


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)

    config = {}

    # When doing your testing, add your config here
    config_file = "config.json"
    if ( os.path.exists(config_file) ):
        config = json.loads(open('config.json', 'r').read())

        syncEngine = ActiveSyncEngine(config)
        syncEngine.start()


        while (True):
            time.sleep(10)
            logging.debug("State: %s" % syncEngine.state)
    else:
        print """Create a config.json with the following structure:

{
   "protocol" : "https",
   "host" : "server_hostname_here",
   "username" : "username_here",
   "password" : "password_here",
   "domain": "domain_name_here"
}"""
        raise SystemExit
