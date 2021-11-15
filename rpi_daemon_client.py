#!/usr/bin/python3

from datetime import datetime, timedelta
import paho.mqtt.client as mqtt
import json
import logging
import random
import string
import time

TOPIC_OUTPUT = 'ee/info/rpi-list'
TOPIC_CONTROL = 'ee/info/rpi-list/control'

LOG = logging.getLogger('rpi_daemon_client')
LOG.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
LOG.addHandler(ch)


class RpiDaemonClient:
    def __init__(self, address, port, user, password):
        self.address = address
        self.port = port
        self.user = user
        self.password = password
        self.userdata = None
        self.started = False

    def _on_message(self, client, userdata, msg):
        LOG.debug('_on_message')
        try:
            jdata = json.loads(msg.payload)
            if jdata['token'] == userdata['token']:
                LOG.debug("_on_message - some data")
                userdata['data'] = jdata

                """Set new token for next request"""
                userdata['token'] = self._new_token()

        except Exception as error:
            LOG.error(f'_on_message json error: {error}')

    def _on_connect(self, client, userdata, flags, rc):
        LOG.debug('_on_connect')
        try:
            client.subscribe(userdata['topic'])
        except Exception as error:
            LOG.error(f'subscribe error: {error}')

    def _start_client(self):
        self.userdata = {'topic': TOPIC_OUTPUT,
                         'token': self._new_token()}

        self.client = mqtt.Client(userdata=self.userdata)
        self.client.enable_logger(LOG)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.tls_set(ca_certs='/etc/ssl/certs/ca-certificates.crt')
        self.client.tls_insecure_set(True)
        self.client.username_pw_set(self.user, self.password)
        self.client.connect(self.address, self.port)
        self.started = True

        return self.userdata

    def _stop_client(self):
        self.client.disconnect()
        self.client.loop_stop()
        self.started = False

    def _new_token(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

    def _send_command(self, key):
        if not self.started:
            raise Exception('Client not started. You have to call start() first')

        LOG.debug(f"send command key: {key}")
        self.userdata['data'] = None
        token = self.userdata['token']
        msg = f'key {token} {key}'
        self.client.publish(TOPIC_CONTROL, msg, 1)

    def _wait(self, timeout):
        start = datetime.now()
        while self.userdata.get('data', None) is None:
            LOG.debug('waiting...')
            time.sleep(0.1)
            time_diff = datetime.now() - start
            if time_diff >= timedelta(seconds=timeout):
                LOG.warning("Timeout :(")
                return None
        LOG.debug("return true")
        return self.userdata.get('data')

    def _send_command_and_wait(self, key, timeout):
        self._send_command(key)
        return self._wait(timeout)

    def stop(self):
        self._stop_client()

    def start(self):
        try:
            self._start_client()
            self.client.loop_start()
        except Exception as error:
            LOG.error(f'start client error: {error}')

    def get_key(self, key, timeout=3):
        try:
            result = self._send_command_and_wait(key, timeout)
            if result:
                LOG.debug(f"return data for {key}: {result}")
        except Exception as error:
            LOG.error(f"get_key_one error: {error}")
            result = None

        return result

    @staticmethod
    def is_online(key, address, port, user, password):
        client = RpiDaemonClient(address, port, user, password)
        client.start()
        result = client.get_key(key)
        client.stop()

        return result and bool(result['data'])


if __name__ == '__main__':
    pass
