import logging

from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.normalise')


class AssignProcedure(PluginBase):

    def pre_receive(self, alert):

        LOG.info('Assign procedure...')
        rules_path = "/app/proc_rules.txt"
        event = alert.event
        with open(rules_path, "r") as f:
            LOG.info("Se lee el fichero")
            for rule in f.readlines():
                data_rule = rule.split(";")
                error = data_rule[0]
                proc = data_rule[1]
                extra = data_rule[2]
                LOG.info(f"Se buscan coincidencias... {event}=={error}")
                if event == error:
                    LOG.info("Coincide")
                    alert.attributes["Procedimiento"] = proc
                    break
                if extra:
                    alert.extra = extra

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
