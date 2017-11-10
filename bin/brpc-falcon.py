#!/usr/bin/env python

import yaml

import brpcmetrics

with open('conf/brpc-open-falcon.yml', 'r') as ymlfile:
    config = yaml.load(ymlfile)

for brpc_server in config['brpc-servers']:
    metric_thread = brpcmetrics.BrpcMetrics(config['falcon']['push_url'],
                                            brpc_server['endpoint'],
                                            brpc_server['url'],
                                            brpc_server['tags'])
    metric_thread.gauge_keywords.extend(config['gauge_bvars'])
    metric_thread.counter_keywords.extend(config['counter_bvars'])
    metric_thread.start()
