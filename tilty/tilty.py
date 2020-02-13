# -*- coding: utf-8 -*-
""" Class to encapsulate all the emitter logic """
import json

from jinja2 import Template

from tilty.emitters import influxdb, webhook


def emit(config, tilt_data):
    """ Find and call emitters from config

    config (dict): configuration file loaded from disk
    tilt_data (dict): data returned from valid tilt device scan
    """
    if tilt_data is None:
        return
    # <start config sample>
    # [webhook]
    # url = http://www.foo.com
    # self.headers = {"Content-Type": "application/json"}
    # payload_template = {"color": "{{ color }}", "gravity"...
    # method = GET
    if config.has_section('webhook'):
        _template = Template(config['webhook']['payload_template'])
        _config = {
            'url': config['webhook']['url'],
            'headers': config['webhook'].get('headers'),
            'method': config['webhook']['method'],
            'payload': json.loads(_template.render(
                color=tilt_data['color'],
                gravity=tilt_data['gravity'],
                temp=tilt_data['temp'],
                timestamp=tilt_data['timestamp'],
            )),
        }
        _webhook = webhook.Webhook(config=_config)
        _webhook.emit()

    # <start config sample>
    # [influxdb]
    # url = http://www.foo.com
    # database = tilty
    # gravity_payload_template = 'gravity,color={{ color }} value={{ gravity }} {{timestamp}}  # noqa
    # temperature_payload_template = 'temperature,scale=fahrenheit,....
    if config.has_section('influxdb'):
        _gravity_template = Template(config['influxdb']['gravity_payload_template']) # noqa
        _temperature_template = Template(config['influxdb']['temperature_payload_template'])  # noqa
        _config = {
            'url': config['influxdb']['url'],
            'database': config['influxdb']['database'],
            'temperature_payload': _temperature_template.render(
                color=tilt_data['color'],
                gravity=tilt_data['gravity'],
                temp=tilt_data['temp'],
                timestamp=tilt_data['timestamp'],
            ),
            'gravity_payload': _gravity_template.render(
                color=tilt_data['color'],
                gravity=tilt_data['gravity'],
                temp=tilt_data['temp'],
                timestamp=tilt_data['timestamp'],
            ),
        }
        _influxdb = influxdb.InfluxDB(config=_config)
        _influxdb.emit()
