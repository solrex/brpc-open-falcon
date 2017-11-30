#!/usr/bin/env python

import yaml

import brpcmetrics

with open('conf/brpc-open-falcon.yml', 'r') as ymlfile:
    config = yaml.load(ymlfile)

threads = []

for brpc_server in config['brpc-servers']:
    metric_thread = brpcmetrics.BrpcMetrics(config['falcon'], brpc_server)
    metric_thread.gauge_keywords.extend(config['gauge_bvars'])
    metric_thread.counter_keywords.extend(config['counter_bvars'])
    metric_thread.start()
    threads.append(metric_thread)

for thread in threads:
    thread.join(5)
