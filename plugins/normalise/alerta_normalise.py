import logging

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.normalise')


class NormaliseAlert(PluginBase):

    def pre_receive(self, alert):

        LOG.info('Normalising alert...')

        # prepend severity to alert text
        alert.text = '{}: {}'.format(alert.severity.upper(), alert.text)

        # supply different default values if missing
        if not alert.group or alert.group == '':
            alert.group = 'PROC-AG000'
        if not alert.value or alert.value == 'n/a':
            alert.value = '--'

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
