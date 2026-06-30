import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Replace with the user's localtunnel URL
url = "https://witty-crews-mate.loca.lt/api/v1/agent/stream"
data = json.dumps({"query": "hello"}).encode("utf-8")
headers = {
    "Content-Type": "application/json",
    "Bypass-Tunnel-Reminder": "true"
}

try:
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, context=ctx) as response:
        print(f"Status: {response.status}")
        for line in response:
            print(line.decode("utf-8").strip())
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code}")
    print(e.read().decode("utf-8"))
except Exception as e:
    print(f"Error: {e}")
