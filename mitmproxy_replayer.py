import csv
import time
import os
import json
import requests
from datetime import datetime
from urllib.parse import parse_qs

class TrafficReplayer:
    def __init__(self, input_csv, output_csv):
        self.input_csv = input_csv
        self.output_csv = output_csv
        
        # 准备输出文件
        self.output_headers = [
            "replay_timestamp", "original_timestamp", "request_url", 
            "request_method", "response_status", "response_time_ms",
            "success", "error_message", "status_match", "response_diff"
        ]
        
        with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(self.output_headers)
        
        print(f"Replaying from {self.input_csv}, saving results to {self.output_csv}")

    def replay(self):
        with open(self.input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    start_time = time.time()
                    
                    # 准备请求
                    method = row['request_method']
                    url = row['request_url']
                    headers = json.loads(row['request_headers'])
                    params = json.loads(row['request_params'])
                    data = row['request_body']
                    
                    # 发送请求
                    response = requests.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        data=data,
                        verify=False  # 忽略SSL证书验证
                    )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    # 比较响应
                    original_status = int(row['response_status'])
                    status_match = original_status == response.status_code
                    
                    # 比较响应体 (简化比较)
                    original_body = row['response_body']
                    response_diff = "N/A"  # 这里可以添加更详细的比较逻辑
                    
                    # 记录结果
                    result_row = [
                        datetime.now().isoformat(),
                        row['timestamp'],
                        url,
                        method,
                        response.status_code,
                        f"{response_time:.2f}",
                        response.ok,
                        "",
                        status_match,
                        response_diff
                    ]
                    
                except Exception as e:
                    result_row = [
                        datetime.now().isoformat(),
                        row['timestamp'],
                        row['request_url'],
                        row['request_method'],
                        "0",
                        "0",
                        False,
                        str(e),
                        False,
                        "Error"
                    ]
                
                # 写入结果
                with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(result_row)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Replay recorded HTTP traffic from CSV')
    parser.add_argument('input', help='Input CSV file containing recorded traffic')
    parser.add_argument('output', help='Output CSV file for replay results')
    
    args = parser.parse_args()
    
    replayer = TrafficReplayer(args.input, args.output)
    replayer.replay()