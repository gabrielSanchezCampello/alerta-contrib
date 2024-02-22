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
            for rule in f.readlines():
                LOG.info(f"RULE:{rule}")


                data_rule = rule.split(";")
                if len(data_rule) != 8:
                    LOG.warning("Regla incompleta")
                    continue
                category = data_rule[0]
                app = data_rule[1]
                object_alert = data_rule[2]
                node = data_rule[3]
                ip = data_rule[4]
                title = data_rule[5]
                manager = data_rule[6]
                instruction = data_rule[7]

                n_matches = 0

                if category:
                    n_matches = n_matches + 1
                    if not re.search(category, alert.group):
                        LOG.debug(f"Falla en category. {category} == {alert.group}")
                        continue

                if app:
                    n_matches = n_matches + 1
                    if "App" in alert.attributes.keys() and not re.search(app, alert.attributes["App"]):
                        LOG.debug(f"Falla en app. {app} == {alert.attributes['App']}")
                        continue

                if object_alert:
                    n_matches = n_matches + 1
                    if not re.search(object_alert, alert.service):
                        LOG.debug(f"Falla en object. {object_alert} == {alert.service}")
                        continue

                if node:
                    n_matches = n_matches + 1
                    if not re.search(node, alert.resource):
                        LOG.debug(f"Falla en node. {node} == {alert.resource}")
                        continue

                if ip:
                    n_matches = n_matches + 1
                    if "IP" in alert.attributes.keys() and not re.search(ip, alert.attributes["IP"]):
                        LOG.debug(f"Falla en IP. {ip} == {alert.attributes['IP'] }")
                        continue

                if title:
                    n_matches = n_matches + 1
                    if not re.search(title, alert.event):
                        LOG.debug(f"Falla en title. {title} == {alert.event}")
                        continue

                if n_matches > max_n_matches:
                    alert.attributes["Procedimiento"] = instruction
                    alert.attributes["Responsable"] = manager
                    max_n_matches = n_matches
                    rule_aplied = rule
        LOG.info(f"Se aplica la regla {rule_aplied}")
        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
