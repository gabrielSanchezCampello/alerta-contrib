import logging
import re
from alerta.plugins import PluginBase
from alerta.plugins import app

LOG = logging.getLogger('alerta.plugins.assign_proc')

plugin_conf = app.config.get('PLUGIN_CONF')

class AssignProcedure(PluginBase):

    def normalise_alert_tienda(self, alert):
        for info in alert.tags:

            if "=" not in info:
                continue

            key = info.split("=")[0]
            value = info.split("=")[1]

            if key == "cloud":
                LOG.debug(f"Se asigna la category {value}")
                alert.group = value

            if key == "namespace":
                LOG.debug(f"Se asigna la App {value}")
                alert.attributes["Aplicacion"] = value

            if key == "object":
                LOG.debug(f"Se asigna el objeto {value}")
                alert.service = value

            if key == "host_name":
                LOG.debug(f"Se asigna el nodo {value}")
                alert.resource = value

    def pre_receive(self, alert):
        #Se normalizan las alertas recibidas de tiendas
        if "source=tienda" in alert.tags:
            self.normalise_alert_tienda(alert)

        #Si la alerta es warning se considera major
        if alert.severity == "warning":
            alert.severity = "major"

        #Se evita reprocesar alertas ya procesadas.
        if alert.repeat:
            return alert

        alert.attributes["Procedimiento"] = plugin_conf["classifyproc"]["generic_proc"]["proc"]
        alert.attributes["Responsable"] = plugin_conf["classifyproc"]["generic_proc"]["responsible"]

        rules_path = plugin_conf["classifyproc"]["rules_file"]
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
                        LOG.debug(f"Falla en category. {rule_category} == {alert.group}")
                        continue

                if rule_app:
                    n_matches = n_matches + 1
                    if "Aplicacion" in alert.attributes.keys() and not re.search(rule_app, alert.attributes["Aplicacion"]):
                        LOG.debug(f"Falla en app. {rule_app} == {alert.attributes['Aplicacion']}")
                        continue

                if rule_object:
                    n_matches = n_matches + 1
                    if not re.search(rule_object, alert.service):
                        LOG.debug(f"Falla en object. {rule_object} == {alert.service}")
                        continue

                if rule_node:
                    n_matches = n_matches + 1
                    if not re.search(rule_node, alert.resource):
                        LOG.debug(f"Falla en node. {rule_node} == {alert.resource}")
                        continue

                if rule_ip:
                    n_matches = n_matches + 1
                    if "IP" in alert.attributes.keys() and not re.search(rule_ip, alert.attributes["IP"]):
                        LOG.debug(f"Falla en IP. {rule_ip} == {alert.attributes['IP'] }")
                        continue

                if rule_title:
                    n_matches = n_matches + 1
                    if not re.search(rule_title, alert.event):
                        LOG.debug(f"Falla en title. {rule_title} == {alert.event}")
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

        return alert

    def post_receive(self, alert):
        return

    def status_change(self, alert, status, text):
        return
