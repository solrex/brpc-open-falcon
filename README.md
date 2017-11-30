# brpc-open-falcon

Baidu RPC (BRPC) Monitor Script for Open Falcon

### Step 1: Edit conf

Rename `brpc-open-falcon.yml.default` to `brpc-open-falcon.yml`, then edit the file, and add your brpc servers.

```yml
falcon:
    push_url: http://127.0.0.1:6071/v1/push
    step: 60

# original_bvar_name:metric_name
gauge_bvars: ['rpc_server_8888_echo_service_echo_latency:API_echo_latency',
              'rpc_server_8888_echo_service_echo_latency_50:API_echo_latency_50'
counter_bvars: ['rpc_server_8888_echo_service_echo_count:API_echo_count']

# Brpc Servers
brpc-servers:
    - {endpoint: "localhost", url: "http://127.0.0.1:8888/vars", tags: ""}

```

### Step 2: Add the monitor script to crontab

```
$ crontab -l
*/1 * * * * cd /path/to/brpc-open-falcon && python -u ./bin/brpc-falcon.py >> brpc-open-falcon.log 2>&1
```

# brpc-open-falcon

用于 Open Falcon 的 Baidu RPC (BRPC) 监控采集脚本

### 第一步：编辑配置文件

将 `brpc-open-falcon.yml.default` 重命名为 `brpc-open-falcon.yml`，然后编辑这个文件，添加你要监控的 Baidu RPC 服务器信息。除标准监控项之外，你还可以添加自定义的 BVAR 监控项。你可以使用 ":" 分隔原始 BVAR 名和想要上报的监控项名，当不提供 : 时，默认以 BVAR 名作为监控项名。

```yml
falcon:
    push_url: http://127.0.0.1:6071/v1/push
    step: 60

# original_bvar_name:metric_name
gauge_bvars: ['rpc_server_8888_echo_service_echo_latency:API_echo_latency',
              'rpc_server_8888_echo_service_echo_latency_50:API_echo_latency_50'
counter_bvars: ['rpc_server_8888_echo_service_echo_count:API_echo_count']

# Brpc Servers
brpc-servers:
    - {endpoint: "localhost", url: "http://127.0.0.1:8888/vars", tags: ""}

```

### 第二步：将监控脚本添加到 crontab 中定时执行

```
$ crontab -l
*/1 * * * * cd /path/to/brpc-open-falcon && python -u ./bin/brpc-falcon.py >> brpc-open-falcon.log 2>&1
```

## 好用就给个 Star 呗！