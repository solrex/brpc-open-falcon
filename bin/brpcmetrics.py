#!/usr/bin/env python

import threading
import json
import time
from datetime import datetime
import requests
import yaml

class BrpcMetrics(threading.Thread):
    def __init__(self, falcon_conf, brpc_conf):
        self.falcon_conf = falcon_conf
        self.brpc_conf = brpc_conf
        # Assign default conf
        if 'test_run' not in self.falcon_conf:
            self.falcon_conf['test_run'] = False
        if 'step' not in self.falcon_conf:
            self.falcon_conf['step'] = 60

        self.gauge_keywords = ['bthread_count', 'bthread_worker_count', 'bthread_worker_usage',
                               'process_cpu_usage', 'process_fd_count',
                               'process_disk_read_bytes_second', 'process_disk_write_bytes_second',
                               'process_io_read_bytes_second', 'process_io_write_bytes_second',
                               'process_thread_count', 'process_uptime',
                               'rpc_socket_count', 'system_loadavg_1m',]
        self.counter_keywords = []

        super(BrpcMetrics, self).__init__(None, name=self.brpc_conf['endpoint'])
        self.setDaemon(False)

    def new_metric(self, metric, value, type = 'GAUGE'):
        return {
            'counterType': type,
            'metric': metric,
            'endpoint': self.brpc_conf['endpoint'],
            'timestamp': self.timestamp,
            'step': self.falcon_conf['step'],
            'tags': self.brpc_conf['tags'],
            'value': value
        }

    def run(self):
        falcon_metrics = []
        # Statistics
        try:
            self.timestamp = int(time.time())
            # brpc returns plain text for curl header
            headers = {'user-agent': 'curl/7.47.0 brpc-open-falcon/0.1'}
            response = requests.get(self.brpc_conf['url'], headers=headers)
            if response.status_code != 200:
                print datetime.now(), "ERROR: [%s] BRPC http error" % self.brpc_conf['endpoint']
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
                falcon_metric = self.new_metric(metric, bvars[keyword])
                falcon_metrics.append(falcon_metric)
            for keyword in self.counter_keywords:
                bvar_abbr = keyword.split(':')
                keyword = bvar_abbr[0]
                if len(bvar_abbr) > 1:
                    metric = 'brpc.' + bvar_abbr[1]
                else:
                    metric = 'brpc.' + keyword
                falcon_metric = self.new_metric(metric, bvars[keyword], type='COUNTER')
                falcon_metrics.append(falcon_metric)
            if self.falcon_conf['test_run']:
                print json.dumps(falcon_metrics)
            else:
                req = requests.post(self.falcon_conf['push_url'], data=json.dumps(falcon_metrics))
                print datetime.now(), "INFO: [%s]" % self.brpc_conf['endpoint'], "[%s]" % self.falcon_conf['push_url'], req.text
        except Exception as e:
            if self.falcon_conf['test_run']:
                raise
            else:
                print datetime.now(), "ERROR: [%s]" % self.brpc_conf['endpoint'], e.message