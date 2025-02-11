import logging
import re

from alerta.exceptions import RejectException
from alerta.plugins import PluginBase, app

LOG = logging.getLogger('alerta.plugins.process_alert')

plugin_conf = app.config.get('PLUGIN_CONF')


class ProcessAlert(PluginBase):

    def normalise_alert_tienda(self, alert):
        for info in alert.tags:

            if "=" not in info:
                continue

            key = info.split("=")[0]
            value = info.split("=")[1]

            if key == "cloud" and value:
                LOG.debug(f"Se añade el nuevo service {value} a {alert.service}")
                if alert.service[0] == "":
                    alert.service = [value]
                else:
                    services = alert.service
                    services.append(value)
                    alert.service = services

            if key == "type":
                LOG.debug(f"Se asigna el tipo de alerta {value}")
                alert.attributes["TipoAlerta"] = value

            if key == "namespace":
                LOG.debug(f"Se asigna la App {value}")
                alert.attributes["App"] = value

            if key == "host_name" and value:
                LOG.debug(f"Se asigna el nodo {value}")
                alert.resource = value

        if "Message" in alert.attributes.keys():
            LOG.debug(f"Se asigna el titulo (event) {alert.attributes['Message']}")
            alert.event = alert.attributes["Message"]

        LOG.debug(f"Se modifica el environment {alert.environment}")
        value = alert.environment.upper()
        if value.startswith("OCP-"):
            value = value.split("-")[1]
        alert.environment = value

    def normalise_severity(self, alert):
        # Si la alerta es warning se considera minor
        if alert.severity == "warning":
            alert.severity = "minor"

        # Si la alerta es principal se considera warning
        if alert.severity == "principal":
            alert.severity = "major"

    def assign_proc(self, alert):
        alert.attributes["Procedimiento"] = plugin_conf["process_alert"]["generic_proc"]["proc"]
        alert.attributes["Responsable"] = plugin_conf["process_alert"]["generic_proc"]["responsible"]

        rules_path = plugin_conf["process_alert"]["rules_file"]
        max_n_matches = 0
        LOG.info('Se asigna procedimiento generico...')
        with open(rules_path, "r") as f:
            for rule in f.readlines():
                LOG.debug(f"RULE:{rule}")
                data_rule = rule.split(";")
                if len(data_rule) != 8:
                    LOG.warning("Regla incompleta")
                    continue
                rule_category = data_rule[0]
                rule_app = data_rule[1]
                rule_object = data_rule[2]
                rule_node = data_rule[3]
                rule_ip = data_rule[4]
                rule_title = data_rule[5]
                rule_manager = data_rule[6]
                rule_instruction = data_rule[7]

                n_matches = 0

                if rule_category:
                    n_matches = n_matches + 1
                    if not re.search(rule_category, alert.group):
                        LOG.debug(f"No se aplica por la category. {rule_category} == {alert.group}")
                        continue

                if rule_app:
                    n_matches = n_matches + 1
                    if "App" in alert.attributes.keys() and not re.search(rule_app, alert.attributes["App"]):
                        LOG.debug(f"No se aplica por la app. {rule_app} == {alert.attributes['App']}")
                        continue

                if rule_object:
                    n_matches = n_matches + 1
                    if not re.search(rule_object, ", ".join(alert.service)):
                        LOG.debug(f"No se aplica por el object. {rule_object} == {alert.service}")
                        continue

                if rule_node:
                    n_matches = n_matches + 1
                    if not re.search(rule_node, alert.resource):
                        LOG.debug(f"No se aplica por el node. {rule_node} == {alert.resource}")
                        continue

                if rule_ip:
                    n_matches = n_matches + 1
                    if "IP" in alert.attributes.keys() and not re.search(rule_ip, alert.attributes["IP"]):
                        LOG.debug(f"No se aplica por la IP. {rule_ip} == {alert.attributes['IP']}")
                        continue

                if rule_title:
                    n_matches = n_matches + 1
                    if not re.search(rule_title, alert.event):
                        LOG.debug(f"No se aplica por el title. {rule_title} == {alert.event}")
                        continue

                if n_matches > max_n_matches:
                    alert.attributes["Procedimiento"] = rule_instruction
                    alert.attributes["Responsable"] = rule_manager
                    max_n_matches = n_matches
                    rule_aplied = rule

                if n_matches == max_n_matches:
                    LOG.warning(f"Existen dos reglas que aplican a la misma alerta. Rule1: {rule}, Rule:{rule_aplied}")

        if max_n_matches != 0:
            LOG.info(f"Se aplica la regla: {rule_aplied} || n_matches={max_n_matches}")

    def pre_receive(self, alert):
        # Se normalizan las alertas recibidas de tiendas
        if "source=tienda" in alert.tags:
            LOG.debug("Se normalizan los datos recibidos de tiendas.")
            self.normalise_alert_tienda(alert)

        # Se normaliza la severidad
        self.normalise_severity(alert)

        # Se descarta la severity normal para alarmas MANUAL
        if alert.severity == "normal" and "TipoAlerta" in alert.attributes.keys() and alert.attributes[
            "TipoAlerta"] == "MANUAL":
            raise RejectException(f"No se puede desescalar automaticamente una alerta MANUAL")

        if alert.severity == "critical" or alert.severity == "major":
            self.assign_proc(alert)

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
