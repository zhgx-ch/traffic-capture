## 注意⚠️ 使用前需手动打开代理开关需通过访问连接：[http://mitm.it/](http://mitm.it/) 来安装证书后安装sls证书

一个简单的录制回放流量的脚本

# capture 用法 （集成）

```
typer capture.py run --url-filter "www.baidu.com" --port 8080
```

* --port 非必填，默认8080

# 打开/关闭代理开关

```
python mac_proxy.py on
python mac_proxy.py off
```

# 启动录制脚本

```
mitmproxy -s mitmproxy_recorder.py
```

录制完成后，会在 `mitmproxy_records` 目录下生成两个文件：

* `record_<timestamp>.csv` - 包含完整的请求/响应详细信息
* `summary_<timestamp>.csv` - 包含简化的摘要信息

# 回放流量

```
python mitmproxy_replayer.py mitmproxy_records/record_20230101_120000.csv replay_results.csv
```

回放结果将保存到 `replay_results.csv`，包含以下信息：

* 回放时间戳
* 原始记录时间戳
* 请求URL和方法
* 响应状态码和时间
* 是否成功
* 错误信息（如果有）
* 状态码是否匹配原始记录
* 响应体差异（简化版）
