import logging
from alerta.exceptions import RejectException
from alerta.plugins import PluginBase, app

LOG = logging.getLogger('alerta.plugins.process_alert')

plugin_conf = app.config.get('PLUGIN_CONF')


class AssignOperator(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        LOG.debug("Estamos en el post receive")
        LOG.debug(alert.actions)
        return alert

    def status_change(self, alert, status, text):
        LOG.debug("Estamos en el status change")
        LOG.debug(f"Status: {status}, text: {text}")
        LOG.debug(alert.actions)
        return alert
