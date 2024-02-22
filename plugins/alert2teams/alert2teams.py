import logging
import re
import pymsteams
from alerta.plugins import PluginBase

LOG = logging.getLogger('alerta.plugins.assign_proc')


class Alert2Teams(PluginBase):

    def build_section(self, body):
        section = pymsteams.cardsection()
        section.title("")
        section.activitySubtitle("")

        lines = body.split("\n")
        if lines:
            for line in lines:
                try:
                    key = line.split("@:@")[0]
                    value = line.split("@:@")[1]
                    section.addFact(key, value)
                except Exception:
                    section.addFact(line)
        return section

    def send_message(self, title, body, severity, webhook):
        TEAMS_DEFAULT_COLORS_MAP = {'normal': '00AA5A', 'critical': 'D8122A', 'major': 'EA680F', 'minor': 'FFBE1E',
                                    'warning': '1E90FF'}
        TEAMS_DEFAULT_COLOR = '000000'
        LOG.debug(f"Comienza la construccion del MSG")
        connector_card = pymsteams.connectorcard(webhook)

        # Se crea el titulo
        connector_card.title(title)

        # Se crean las section para el body
        if type(body) == str:
            section = self.build_section(body)
            connector_card.addSection(section)

        if type(body) == list:
            for line in body:
                section = self.build_section(line)
                connector_card.addSection(section)

        if severity in TEAMS_DEFAULT_COLORS_MAP.keys():
            color = TEAMS_DEFAULT_COLORS_MAP[severity]
        else:
            color = TEAMS_DEFAULT_COLOR
        connector_card.color(color)

        connector_card.send()

    def pre_receive(self, alert):

        return

    def post_receive(self, alert):
        LOG.info('Se asigna procedimiento generico...')

        rules_path = "/app/proc_rules_teams.txt"
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
                        LOG.debug(f"Falla en IP. {ip} == {alert.attributes['IP']}")
                        continue

                if title:
                    n_matches = n_matches + 1
                    if not re.search(title, alert.event):
                        LOG.debug(f"Falla en title. {title} == {alert.event}")
                        continue

                if n_matches > max_n_matches:
                    # Values of teams
                    teams_tile = data_rule[7]
                    teams_summary = data_rule[8]
                    teams_type = data_rule[9]
                    teams_webhook = data_rule[10]
                    teams_severity = severity
                    rule_aplied = rule

        if max_n_matches != 0:
            LOG.info(f"Se aplica la regla: {rule_aplied} || n_matches={max_n_matches}")
            body = f"RESUMEN@:@ {teams_summary}"
            body = body + f"SEVERITY@:@ {teams_severity}"
            body = body + f"TYPE@:@ {teams_type}"
            self.send_message(teams_tile, body, severity, teams_webhook)

        return alert

    def status_change(self, alert, status, text):
        return