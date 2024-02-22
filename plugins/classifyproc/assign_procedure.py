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
                category = data_rule[0]
                app = data_rule[1]
                object_alert = data_rule[2]
                node = data_rule[3]
                ip = data_rule[4]
                title = data_rule[5]
                manager = data_rule[6]
                instruction = data_rule[7]
                if alert.group and alert.group != category:
                    break
                if alert.app and alert.app != app:
                    break
                if alert.service and alert.service != object_alert:
                    break
                if alert.resource and alert.resource != node:
                    break
                if alert.ip and alert.ip != ip:
                    break
                if alert.event and alert.event != title:
                    break
                alert.attributes["Procedimiento"] = instruction
                alert.attributes["Responsable"] = manager

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
