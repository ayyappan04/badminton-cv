import os
import time
import requests
from threading import Thread
import uvicorn
from src.web.app import app

# Running server in thread for test
def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

def verify_api():
    print("Starting API Server...")
    t = Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(3) # Wait for boot
    
    base_url = "http://127.0.0.1:8001"
    
    # 1. Upload Dummy Video
    video_path = "data/test/dummy_match.mp4"
    if not os.path.exists(video_path):
        print(f"Error: {video_path} not found. Run dummy gen first.")
        return

    print("Uploading video...")
    with open(video_path, 'rb') as f:
        files = {'file': ('test.mp4', f, 'video/mp4')}
        resp = requests.post(f"{base_url}/analyze", files=files)
        
    if resp.status_code != 200:
        print(f"Upload failed: {resp.text}")
        return
        
    data = resp.json()
    task_id = data['task_id']
    print(f"Task ID: {task_id}")
    
    # 2. Poll Status
    print("Polling status...")
    for _ in range(60): # Timeout 60s
        status_resp = requests.get(f"{base_url}/status/{task_id}")
        status_data = status_resp.json()
        status = status_data['status']
        print(f"Status: {status}")
        
        if status == 'completed':
            break
        if status == 'failed':
            print(f"Analysis Failed: {status_data.get('error')}")
            return
        time.sleep(2)
        
    # 3. Get Results
    print("Fetching results...")
    results_resp = requests.get(f"{base_url}/results/{task_id}")
    if results_resp.status_code == 200:
        res = results_resp.json()
        if 'report_markdown' in res:
            print("SUCCESS: Report retrieved.")
            print("Preview:", res['report_markdown'][:100])
        else:
            print("FAILURE: Report missing in response.")
    else:
        print(f"FAILURE: Could not get results. Code {results_resp.status_code}")

if __name__ == "__main__":
    verify_api()
