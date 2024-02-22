import logging
import re
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.normalise')


class AssignProcedure(PluginBase):

    def pre_receive(self, alert):

        LOG.info('Assign procedure...')
        rules_path = "/app/proc_rules.txt"
        max_n_matches=0
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
                LOG.info(f"Fila: {category}, {app}, {object_alert}, {node}, {ip}, {title}, {manager}, {instruction}")
                
                n_matches = 0
                if category:
                    n_matches = n_matches + 1
                    if not re.search(category, alert.group):
                        LOG.info(f"Falla en category. {category} == {alert.group}")
                        continue

                if app:
                    n_matches = n_matches + 1
                    if "App" in alert.attributes.keys() and not re.search(app, alert.attributes["App"]):
                        LOG.info(f"Falla en app. {app} == {alert.attributes['App']}")
                        continue

                if object_alert:
                    n_matches = n_matches + 1
                    if not re.search(object_alert, alert.service):
                        LOG.info(f"Falla en object. {object_alert} == {alert.service}")
                        continue

                if node:
                    n_matches = n_matches + 1
                    if not re.search(node, alert.resource):
                        LOG.info(f"Falla en node. {node} == {alert.resource}")
                        continue

                if ip:
                    n_matches = n_matches + 1
                    if "IP" in alert.attributes.keys() and not re.search(ip, alert.attributes["IP"]):
                        LOG.info(f"Falla en IP. {ip} == {alert.attributes['IP'] }")
                        continue

                if title:
                    n_matches = n_matches + 1
                    if not re.search(title, alert.event):
                        LOG.info(f"Falla en title. {title} == {alert.event}")
                        continue

                if n_matches > max_n_matches:
                    alert.attributes["Procedimiento"] = instruction
                    alert.attributes["Responsable"] = manager
                    max_n_matches = n_matches
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
