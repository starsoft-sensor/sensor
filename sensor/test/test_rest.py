import requests

# 发送 GET 请求到 Flask 程序的 /data 路由
response = requests.get('http://127.0.0.1:5000/sensor/20240414183236')

# 打印响应内容
print(response.json())