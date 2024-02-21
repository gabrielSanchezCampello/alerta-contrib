import logging

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.normalise')


class AssignProcedure(PluginBase):

    def pre_receive(self, alert):

        LOG.info('Assign procedure...')

        # supply different default values if missing
        if not alert.value or alert.value == '':
            alert.value = 'AGP-00001'

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
