import csv
import time
import os
import json
from datetime import datetime
from mitmproxy import http, ctx
from urllib.parse import urlparse, parse_qs

def load(loader):
    loader.add_option(
        name = "url_filter",
        typespec = str,
        default = "",
        help = "只录制包含此字符串的URL"
    )

def configure(updated):
    ctx.recorder = TrafficRecorder()

class TrafficRecorder:
    def __init__(self):
        self.output_dir = "mitmproxy_records"
        os.makedirs(self.output_dir, exist_ok=True)
        self.url_filter = getattr(ctx.options, "url_filter", "") # 读取 mitmproxy --set 传递的参数
        print( "trafficrecorder 中过滤网址为" + self.url_filter)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.record_file = os.path.join(self.output_dir, f"record_{timestamp}.csv")
        self.summary_file = os.path.join(self.output_dir, f"summary_{timestamp}.csv")
        
        # CSV 文件头
        self.record_headers = [
            "timestamp", "request_method", "request_url", 
            "request_headers", "request_params", "request_body",
            "response_status", "response_headers", "response_body",
            "response_time_ms", "content_type"
        ]
        
        self.summary_headers = [
            "timestamp", "request_url", "request_method",
            "response_status", "response_time_ms", "success"
        ]
        
        # 初始化文件
        with open(self.record_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.record_headers)
            
        with open(self.summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.summary_headers)
        
        ctx.log.info(f"Recording traffic to {self.record_file}")
        ctx.log.info(f"Summary will be saved to {self.summary_file}")

    def _get_params(self, url):
        parsed = urlparse(url)
        return parse_qs(parsed.query)

    def _format_headers(self, headers):
        return json.dumps(dict(headers))

    def _should_record(self, url):
        return self.url_filter in url if self.url_filter else True

    def request(self, flow: http.HTTPFlow):
        if not self._should_record(flow.request.url):
            return
        flow.start_time = time.time()

    def response(self, flow: http.HTTPFlow):
        print (self._should_record(flow.request.url))
        if not self._should_record(flow.request.url):
            return
        try:
            if hasattr(flow, "start_time"):
                response_time = (time.time() - flow.start_time) * 1000
            else:
                response_time = 0  # 或者其他默认值
            
            # 准备详细记录
            record_row = [
                datetime.now().isoformat(),
                flow.request.method,
                flow.request.url,
                self._format_headers(flow.request.headers),
                json.dumps(self._get_params(flow.request.url)),
                flow.request.content.decode('utf-8', errors='replace') if flow.request.content else "",
                flow.response.status_code,
                self._format_headers(flow.response.headers),
                flow.response.content.decode('utf-8', errors='replace') if flow.response.content else "",
                f"{response_time:.2f}",
                flow.response.headers.get("Content-Type", "")
            ]
            
            # 准备摘要记录
            summary_row = [
                datetime.now().isoformat(),
                flow.request.url,
                flow.request.method,
                flow.response.status_code,
                f"{response_time:.2f}",
                flow.response.status_code < 400
            ]
            
            # 写入文件
            with open(self.record_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(record_row)
                
            with open(self.summary_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(summary_row)
                
        except Exception as e:
            ctx.log.error(f"Error recording request: {e}")


def request(flow: http.HTTPFlow):
    ctx.recorder.request(flow)

def response(flow: http.HTTPFlow):
    ctx.recorder.response(flow)