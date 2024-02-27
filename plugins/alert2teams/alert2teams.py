import logging
import re
import pymsteams
from alerta.plugins import PluginBase, app



LOG = logging.getLogger('alerta.plugins.alerta2teams')

plugin_conf = app.config.get('PLUGIN_CONF')

class Alert2Teams(PluginBase):

    def build_section(self, body, color):

        section = pymsteams.cardsection()
        section.title(f"<hr style='border-color: #{color}; border-width: 5px;'>")

        lines = body.split("\n")
        if lines:
            for line in lines:
                try:
                    key = line.split("@:@")[0] + ":"
                    value = line.split("@:@")[1]
                    LOG.debug(f"{key} {value}")
                    section.addFact(key, value)
                except Exception:
                    if line:
                        section.text(line)
        return section

    def send_message(self, title, body, severity, webhook):
        LOG.debug(f"Comienza la construccion del MSG.")

        TEAMS_DEFAULT_COLORS_MAP = plugin_conf["alert2teams"]["TEAMS_DEFAULT_COLORS_MAP"]
        TEAMS_DEFAULT_COLOR = plugin_conf["alert2teams"]["TEAMS_DEFAULT_COLOR"]

        if severity in TEAMS_DEFAULT_COLORS_MAP.keys():
            color = TEAMS_DEFAULT_COLORS_MAP[severity]
        else:
            color = TEAMS_DEFAULT_COLOR
        LOG.debug(f"Color {color}, severity{severity}")
        connector_card = pymsteams.connectorcard(webhook)

        # Se crea el titulo
        connector_card.title(title)
        connector_card.summary(title)

        # Se crean las section para el body
        if type(body) == str:
            section = self.build_section(body, color)
            connector_card.addSection(section)

        connector_card.send()

    def pre_receive(self, alert):
        return alert

    def post_receive(self, alert):
        # A teams solo se envían las minor
        if alert.severity != "minor" or alert.severity != "normal":
            return alert

        #Evita notificar alertas duplicadas
        if alert.repeat:
            return alert

        #Se obtiene la información de la ALERTA
        alert_node = alert.resource
        alert_category = alert.group
        alert_severity = alert.severity
        try:
            alert_app = alert.attributes["App"]
        except Exception:
            alert_app = ""
        alert_object = alert.service

        #Notificacion en caso de cambio de severidad
        if alert.severity == "normal" and "TEAMS_WEBHOOK" in alert.attributes.keys():
            LOG.debug(f"Se avisa del fin de la alerta.")
            webhook = alert.attributes["TEAMS_WEBHOOK"]
            title = alert.attributes["TEAMS_TITLE"]
            body = f"CATEGORIA@:@ {alert_category} \n"
            body = body + f"NODO@:@ {alert_node} \n"
            body = body + f"APP@:@ {alert_app} \n"
            body = body + f"SEVERIDAD@:@ {alert_severity} \n"
            body = body + f"OBJETO@:@ {alert_object} \n"
            self.send_message(title, body, alert.severity, webhook)
            return alert

        #Notificacion inicial
        LOG.info('Se busca la regla a aplicar...')

        rules_path = plugin_conf["alert2teams"]["rules_file"]
        max_n_matches = 0

        with open(rules_path, "r") as f:
            for rule in f.readlines():
                LOG.debug(f"RULE:{rule}")
                data_rule = rule.split(";")
                if len(data_rule) != 10:
                    LOG.warning("Regla incompleta")
                    continue

                # Values of rule
                rule_category = data_rule[0]
                rule_app = data_rule[1]
                rule_object = data_rule[2]
                rule_node = data_rule[3]
                rule_ip = data_rule[4]
                rule_title = data_rule[5]
                rule_severity = data_rule[6]

                n_matches = 0
                LOG.info(f"Se comprueba category")
                if rule_category:
                    n_matches = n_matches + 1
                    if not re.search(rule_category, alert.group):
                        LOG.debug(f"Falla en category. {rule_category} == {alert.group}")
                        continue

                LOG.info(f"Se comprueba app")
                if rule_app:
                    n_matches = n_matches + 1
                    if "App" in alert.attributes.keys() and not re.search(rule_app, alert.attributes["App"]):
                        LOG.debug(f"Falla en app. {rule_app} == {alert.attributes['App']}")
                        continue

                LOG.info(f"Se comprueba object")
                if rule_object:
                    n_matches = n_matches + 1
                    if not re.search(rule_object, alert.service):
                        LOG.debug(f"Falla en object. {rule_object} == {alert.service}")
                        continue

                LOG.info(f"Se comprueba node")
                if rule_node:
                    n_matches = n_matches + 1
                    if not re.search(rule_node, alert.resource):
                        LOG.debug(f"Falla en node. {rule_node} == {alert.resource}")
                        continue

                LOG.info(f"Se comprueba ip")
                if rule_ip:
                    n_matches = n_matches + 1
                    if "IP" in alert.attributes.keys() and not re.search(rule_ip, alert.attributes["IP"]):
                        LOG.debug(f"Falla en IP. {rule_ip} == {alert.attributes['IP']}")
                        continue

                LOG.info(f"Se comprueba title")
                if rule_title:
                    n_matches = n_matches + 1
                    if not re.search(rule_title, alert.event):
                        LOG.debug(f"Falla en title. {rule_title} == {alert.event}")
                        continue

                LOG.info(f"Se comprueba severity")
                if rule_severity:
                    n_matches = n_matches + 1
                    if not re.search(rule_severity, alert.severity):
                        LOG.debug(f"Falla en severity. {rule_severity} == {alert.severity}")
                        continue

                LOG.info(f"n_matches: {n_matches}, max_n_matches: {max_n_matches}")
                if n_matches > max_n_matches:
                    max_n_matches = n_matches
                    # Values to teams
                    teams_tile = data_rule[7]
                    teams_webhook = data_rule[8].rstrip()
                    rule_aplied = rule

        if max_n_matches != 0:
            LOG.info(f"Se aplica la regla: {rule_aplied} || n_matches={max_n_matches}")

            body = f"CATEGORIA@:@ {alert_category} \n"
            body = body + f"NODO@:@ {alert_node} \n"
            body = body + f"APP@:@ {alert_app} \n"
            body = body + f"SEVERIDAD@:@ {alert_severity} \n"
            body = body + f"OBJETO@:@ {alert_object} \n"
            LOG.info(f"Se manda teams con: webhook: {teams_webhook} || Titulo {teams_tile} || Body: {body} ")
            self.send_message(teams_tile, body, alert_severity, teams_webhook)
            alert.attributes["TEAMS_WEBHOOK"] = f"{teams_webhook}"
            alert.attributes["TEAMS_TITLE"] = f"{teams_tile}"
        else:
            alert.attributes["ENVIA_TEAMS"] = f"NO"
            LOG.info("No se envía teams ya que no encaja en ninguna regla.")
        return alert

    def status_change(self, alert, status, text):
        return alert
