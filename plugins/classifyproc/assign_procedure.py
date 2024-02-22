import logging

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.normalise')


class AssignProcedure(PluginBase):

    def pre_receive(self, alert):

        LOG.info('Assign procedure...')
        rules_path = "app/proc_rules.txt"
        event = alert.event
        with open(rules_path, "r") as f:
            for rule in f.readlines():
                data_rule = rule.split(";")
                error = data_rule[0]
                proc = data_rule[1]
                extra = data_rule[2]

                if event == error:
                    alert.value = proc
                    break
                if extra:
                    alert.extra = extra

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
