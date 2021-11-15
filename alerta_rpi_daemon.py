from rpi_daemon_client import RpiDaemonClient
import logging
import os

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.rpi_daemon')


class RpiDaemonCheck(PluginBase):
    def __init__(self):
        super().__init__()
        self.address = os.getenv('MQTT_ADDRESS')
        self.port = int(os.getenv('MQTT_PORT'))
        self.user = os.getenv('MQTT_USER')
        self.password = os.getenv('MQTT_PASSWORD')
        self.client = None

    def pre_receive(self, alert):
        LOG.debug('RpiDaemonCheck pre_receive: %s', alert)
        try:
            if alert.is_duplicate():
                LOG.debug("RpiDaemonCheck alert repeated - ignore")
                return alert
        except Exception as error:
            LOG.error(f"RpiDaemonCheck error: {error}")

        if not self.client:
            self.client = RpiDaemonClient(self.address, self.port, self.user, self.password)
            self.client.start()

        data = self.client.get_key(alert.resource)
        if data is None:
            LOG.error(f"RpiDaemonCheck - none returned for {alert.resource}")
            return alert

        online_status = bool(data['data'])

        LOG.debug(f"RpiDaemonCheck: online status of {alert.resource}: {online_status}")
        alert.attributes['online_status'] = online_status
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return


if __name__ == '__main__':
    pass
