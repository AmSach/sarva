#!/usr/bin/env python3
"""
Sarva Node Agent v1.0 — Compute Pool Node
Works as: python3 agent.py OR ./SarvaNode (binary)
No install needed. One file. One command.
"""
import os, time, json, traceback, sys, platform, hashlib, uuid

API = os.getenv("SARVA_API", "https://e65440d9-cfb0-47fa-b11a-d2070bf13013.up.railway.app")
NODE_NAME = os.getenv("SARVA_NODE_NAME", f"{platform.node()}-{platform.system().lower()}")
GPU_TIER = os.getenv("SARVA_GPU_TIER", "cpu")
CPU_CORES = os.cpu_count() or 4
RAM_GB = 8
OWNER_ID = os.getenv("SARVA_OWNER_ID", "anonymous")
REGION = os.getenv("SARVA_REGION", "in")
HEARTBEAT_INTERVAL = int(os.getenv("SARVA_HEARTBEAT_SECS", "30"))
PULL_INTERVAL = int(os.getenv("SARVA_PULL_SECS", "5"))

class Node:
    def __init__(self):
        self.id = os.getenv("SARVA_NODE_ID", "")
        self.registered = False
        self.status = "idle"
        self.job_id = None
        self.current_job = None

    def api(self, path, data=None):
        import requests
        try:
            if data:
                r = requests.post(f"{API}{path}", json=data, timeout=15)
            else:
                r = requests.get(f"{API}{path}", timeout=15)
            return r.json()
        except Exception as e:
            print(f"[SARVA] API error {path}: {e}")
            return {"error": str(e)}

    def detect_gpu(self):
        try:
            import subprocess
            out = subprocess.check_output("nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null", shell=True).decode().strip()
            if out:
                name = out.lower()
                if "4090" in name: return "rtx-4090"
                if "3090" in name: return "rtx-3090"
                if "4070" in name: return "rtx-4070"
                if "3060" in name: return "rtx-3060"
                if "2070" in name: return "rtx-2070"
                if "1080" in name: return "gtx-1080"
                if "1660" in name: return "gtx-1660"
                return "gpu-unknown"
        except:
            pass
        return GPU_TIER

    def register(self):
        gpu = self.detect_gpu()
        resp = self.api("/nodes/register", {
            "nodeName": NODE_NAME,
            "gpuTier": gpu,
            "cpuCores": CPU_CORES,
            "ramGb": RAM_GB,
            "ownerId": OWNER_ID,
            "region": REGION
        })
        if "nodeId" in resp:
            self.id = resp["nodeId"]
            self.registered = True
            self.gpu_tier = gpu
            print(f"[SARVA] ✅ Registered as node {self.id} ({gpu})")
            print(f"[SARVA] 💰 Quality Score: {resp.get('qualityScore', 1.0)}x")
            return True
        else:
            print(f"[SARVA] ❌ Registration failed: {resp}")
            return False

    def heartbeat(self):
        if not self.id: return
        resp = self.api("/nodes/heartbeat", {"nodeId": self.id, "status": self.status})
        if resp.get("ok"):
            pass  # silent

    def pull_job(self):
        if not self.id: return None
        resp = self.api(f"/jobs/next?nodeId={self.id}")
        if resp.get("job"):
            self.current_job = resp["job"]
            self.job_id = resp["job"]["id"]
            self.status = "busy"
            return resp["job"]
        return None

    def run_job(self, job):
        print(f"[SARVA] 🔥 Running job {job['id']} ({job['type']}) — {job['slices']} slices")
        print(f"[SARVA] 📦 Script: {job.get('script', 'N/A')[:80]}")
        try:
            # Simulate job work
            time.sleep(3)
            self.api(f"/jobs/complete", {
                "jobId": job["id"],
                "resultCid": f"result-{job['id']}-done",
                "error": None
            })
            print(f"[SARVA] ✅ Job {job['id']} completed!")
        except Exception as e:
            self.api(f"/jobs/complete", {
                "jobId": job["id"],
                "resultCid": None,
                "error": str(e)
            })
            print(f"[SARVA] ❌ Job {job['id']} failed: {e}")
        finally:
            self.current_job = None
            self.job_id = None
            self.status = "idle"

    def start(self):
        print("=" * 50)
        print("  SARVA NODE v1.0")
        print("  API: " + API)
        print("  Node Name: " + NODE_NAME)
        print("  Owner: " + OWNER_ID)
        print("  Heartbeat: " + str(HEARTBEAT_INTERVAL) + "s")
        print("  Job Pull: " + str(PULL_INTERVAL) + "s")
        print("=" * 50)

        if not self.register():
            print("[SARVA] ⚠️  Retrying registration in 10s...")
            time.sleep(10)
            self.register()

        print("[SARVA] 🚀 Node running. Press Ctrl+C to stop.")

        last_heartbeat = 0
        while True:
            try:
                # Send heartbeat every HEARTBEAT_INTERVAL seconds
                now = time.time()
                if now - last_heartbeat >= HEARTBEAT_INTERVAL:
                    self.heartbeat()
                    last_heartbeat = now

                # Try to pull a job
                job = self.pull_job()
                if job:
                    self.run_job(job)
                else:
                    time.sleep(PULL_INTERVAL)

            except KeyboardInterrupt:
                print("\n[SARVA] ⛔ Node stopped.")
                break
            except Exception as e:
                print(f"[SARVA] ⚠️  Error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    Node().start()

# ── INSTALLER SCRIPT (append this to agent.py to create install) ──
# Copy this entire file + run: python3 agent.py --install
# Or just run directly: python3 SarvaNode   (or ./SarvaNode for binary)