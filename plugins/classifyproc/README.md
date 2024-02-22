Assign procedures to alerts
==========================

Actions:

  * Read a file with several rules and their associated procedures.
  * Find the most restrictive rule that matches the alert.
  * Assign the procedure to the rule

This repo should be forked or copied and the python plugin modified to suit
the specific Alerta environment.

For help, join [![Slack chat](https://img.shields.io/badge/chat-on%20slack-blue?logo=slack)](https://slack.alerta.dev)

Installation
------------

Clone the GitHub repo and run:

    $ python setup.py install

Or, to install remotely from GitHub run:

    $ pip install git+https://github.com/gabrielSanchezCampello/alerta-contrib.git#subdirectory=plugins/classifyproc


Note: If Alerta is installed in a python virtual environment then plugins
need to be installed into the same environment for Alerta to dynamically
discover them.

Configuration
-------------

Add `classifyproc` to the list of enabled `PLUGINS` in `alertad.conf` server
configuration file and set plugin-specific variables either in the
server configuration file or as environment variables.

**Example**

```python
PLUGINS = ['reject','classifyproc']
```

Troubleshooting
---------------

Restart Alerta API and confirm that the plugin has been loaded and enabled.

Set `DEBUG=True` in the `alertad.conf` configuration file and look for log
entries similar to below:


References
----------

  * Normalize Monitoring Traps: https://techdocs.broadcom.com/us/en/ca-enterprise-software/it-operations-management/service-operations-insight/4-2/administrating/event-management/event-management-example-scenarios/event-management-example-5-normalize-monitoring-traps.html

License
-------

Copyright (c) 2016 Nick Satterly. Available under the MIT License.
