import urllib.request
import json

url = "http://127.0.0.1:3000/api/v1/agent/stream"
data = json.dumps({"query": "hello"}).encode("utf-8")
headers = {"Content-Type": "application/json"}

try:
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print("Response body:")
        for line in response:
            print(line.decode("utf-8").strip())
except Exception as e:
    print(f"Error: {e}")
