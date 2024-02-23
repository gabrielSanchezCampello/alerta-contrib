import logging
import re
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.alerta2teams')


class Alert2Jira(PluginBase):

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        LOG.info('Se busca la regla a aplicar...')

        rules_path = "/app/proc_rules_jira.txt"
        max_n_matches = 0

        with open(rules_path, "r") as f:
            for rule in f.readlines():
                LOG.debug(f"RULE:{rule}")
                data_rule = rule.split(";")
                if len(data_rule) != 11:
                    LOG.warning("Regla incompleta")
                    continue

                # Values of rule
                category = data_rule[0]
                app = data_rule[1]
                object_alert = data_rule[2]
                node = data_rule[3]
                ip = data_rule[4]
                title = data_rule[5]
                severity = data_rule[6]

                n_matches = 0
                LOG.info(f"Se comprueba category")
                if category:
                    n_matches = n_matches + 1
                    if not re.search(category, alert.group):
                        LOG.debug(f"Falla en category. {category} == {alert.group}")
                        continue
                LOG.info(f"Se comprueba app")
                if app:
                    n_matches = n_matches + 1
                    if "App" in alert.attributes.keys() and not re.search(app, alert.attributes["App"]):
                        LOG.debug(f"Falla en app. {app} == {alert.attributes['App']}")
                        continue

                LOG.info(f"Se comprueba object")
                if object_alert:
                    n_matches = n_matches + 1
                    if not re.search(object_alert, alert.service):
                        LOG.debug(f"Falla en object. {object_alert} == {alert.service}")
                        continue

                LOG.info(f"Se comprueba node")
                if node:
                    n_matches = n_matches + 1
                    if not re.search(node, alert.resource):
                        LOG.debug(f"Falla en node. {node} == {alert.resource}")
                        continue

                LOG.info(f"Se comprueba ip")
                if ip:
                    n_matches = n_matches + 1
                    if "IP" in alert.attributes.keys() and not re.search(ip, alert.attributes["IP"]):
                        LOG.debug(f"Falla en IP. {ip} == {alert.attributes['IP']}")
                        continue

                LOG.info(f"Se comprueba title")
                if title:
                    n_matches = n_matches + 1
                    if not re.search(title, alert.event):
                        LOG.debug(f"Falla en title. {title} == {alert.event}")
                        continue

                LOG.info(f"n_matches: {n_matches}, max_n_matches: {max_n_matches}")
                if n_matches > max_n_matches:
                    max_n_matches = n_matches
                    # Values of jira
                    jira_tile = data_rule[7]
                    jira_summary = data_rule[8]
                    jira_type = data_rule[9]
                    jira_webhook = data_rule[10]
                    jira_severity = severity
                    rule_aplied = rule

        if max_n_matches != 0:
            alert.attributes["JIRA"] = f"ENVIADO"
        else:
            LOG.info("No se envía jira ya que no encaja en ninguna regla.")
        return alert

    def status_change(self, alert, status, text):
        return
