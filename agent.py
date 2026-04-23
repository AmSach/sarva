#!/usr/bin/env python3
"""
Sarva Node Agent - Lightweight compute node client
Run: python3 agent.py
"""
import os, time, json, traceback, sys

API = os.getenv("SARVA_API", "https://e65440d9-cfb0-47fa-b11a-d2070bf13013.up.railway.app")
NODE_ID = os.getenv("NODE_ID", "")
NODE_NAME = os.getenv("NODE_NAME", "python-node-" + str(os.getpid()))
GPU_TIER = os.getenv("GPU_TIER", "cpu")
OWNER_ID = os.getenv("OWNER_ID", "anonymous")

def get():
    r = __import__("requests").get(f"{API}{sys.argv[1] if len(sys.argv) > 1 else '/'}", timeout=10)
    return r.json()

def post(path, data):
    import requests
    r = requests.post(f"{API}{path}", json=data, timeout=10)
    return r.json()

def register():
    r = post("/nodes/register", {"nodeName": NODE_NAME, "gpuTier": GPU_TIER, "cpuCores": os.cpu_count() or 4, "ramGb": 8, "ownerId": OWNER_ID})
    print(f"[SARVA] Registered: {r}")
    return r.get("node_id", NODE_ID)

def heartbeat(node_id):
    post("/nodes/heartbeat", {"node_id": node_id})

def poll_job(node_id):
    r = get(f"/jobs/next?node_id={node_id}")
    return r.get("job")

def complete_job(job_id, result_cid=None, error=None):
    post(f"/jobs/{job_id}/complete", {"result_cid": result_cid, "error": error})

print(f"[SARVA] Node '{NODE_NAME}' starting...")
node_id = NODE_ID or register()
print(f"[SARVA] Node ID: {node_id}")

while True:
    heartbeat(node_id)
    job = poll_job(node_id)
    if job:
        print(f"[SARVA] Got job: {job['id']} ({job['type']})")
        try:
            print(f"[SARVA] Simulating work on: {job['script'] or job['type']}")
            time.sleep(3)
            complete_job(job["id"], result_cid="simulated_result_cid")
            print(f"[SARVA] Job {job['id']} completed")
        except Exception as e:
            complete_job(job["id"], error=str(e))
    else:
        print(f"[SARVA] No jobs available, waiting...")
    time.sleep(15)