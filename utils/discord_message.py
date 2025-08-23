import requests

def send_discord_alert(content, webhook_url):
    data = {"content": content}
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"❌ Discord alert failed: {response.status_code} {response.text}")
    else:
        print("✅ Discord alert sent!")
