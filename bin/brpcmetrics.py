#!/usr/bin/env python

import threading
import json
import time
from datetime import datetime
import requests
import yaml
import re

class BrpcMetrics(threading.Thread):
    def __init__(self, falcon_url, endpoint, url, tags = '', falcon_step = 60, daemon = False):
        self.falcon_url = falcon_url
        self.falcon_step = falcon_step
        self.url = url
        self.endpoint = endpoint
        self.tags = tags

        self.gauge_keywords = ['bthread_count', 'bthread_worker_count', 'bthread_worker_usage',
                               'process_cpu_usage', 'process_fd_count',
                               'process_disk_read_bytes_second', 'process_disk_write_bytes_second',
                               'process_io_read_bytes_second', 'process_io_write_bytes_second',
                               'process_thread_count', 'process_uptime',
                               'rpc_socket_count', 'system_loadavg_1m',]
        self.counter_keywords = []

        super(BrpcMetrics, self).__init__(None, name=endpoint)
        self.setDaemon(daemon)

    def run(self):
        falcon_metrics = []
        # Statistics
        try:
            timestamp = int(time.time())
            # brpc returns plain text for curl header
            headers = {'user-agent': 'curl/7.47.0 brpc-open-falcon/0.1'}
            response = requests.get(self.url, headers=headers)
            if response.status_code != 200:
                return
            bvars = yaml.load(response.text)
            # Original metrics
            for keyword in self.gauge_keywords:
                bvar_abbr = keyword.split(':')
                keyword = bvar_abbr[0]
                if len(bvar_abbr) > 1:
                    metric = 'brpc.' + bvar_abbr[1]
                else:
                    metric = 'brpc.' + keyword
                falcon_metric = {
                    'counterType': 'GAUGE',
                    'metric': metric,
                    'endpoint': self.endpoint,
                    'timestamp': timestamp,
                    'step': self.falcon_step,
                    'tags': self.tags,
                    'value': bvars[keyword]
                }
                falcon_metrics.append(falcon_metric)
            for keyword in self.counter_keywords:
                bvar_abbr = keyword.split(':')
                keyword = bvar_abbr[0]
                if len(bvar_abbr) > 1:
                    metric = 'brpc.' + bvar_abbr[1]
                else:
                    metric = 'brpc.' + keyword
                falcon_metric = {
                    'counterType': 'COUNTER',
                    'metric': metric,
                    'endpoint': self.endpoint,
                    'timestamp': timestamp,
                    'step': self.falcon_step,
                    'tags': self.tags,
                    'value': bvars[keyword]
                }
                falcon_metrics.append(falcon_metric)
            #print json.dumps(falcon_metrics)
            req = requests.post(self.falcon_url, data=json.dumps(falcon_metrics))
            print datetime.now(), "INFO: [%s]" % self.endpoint, "[%s]" % self.falcon_url, req.text
        except Exception as e:
            print datetime.now(), "ERROR: [%s]" % self.endpoint, e
            return