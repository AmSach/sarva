SARVA NODE v1.0.0 — One-Click Install
=====================================

WINDOWS:
  1. Download START.bat + agent.py to same folder
  2. Double-click START.bat
  3. Enter your User ID when asked
  4. Done! Node runs. Press Ctrl+C to stop.

LINUX / MAC:
  1. Download SarvaNode (Linux binary)
  2. chmod +x SarvaNode && ./SarvaNode
  
  OR if you have Python:
  1. Download agent.py
  2. pip install requests
  3. python3 agent.py

CONFIGURATION (set environment variables or edit agent.py):
  SARVA_API        = https://e65440d9-cfb0-47fa-b11a-d2070bf13013.up.railway.app
  SARVA_NODE_NAME  = your-node-name (auto-generated if blank)
  SARVA_GPU_TIER   = rtx-4090 / rtx-3090 / rtx-3060 / gtx-1080 / cpu (auto-detected if blank)
  SARVA_OWNER_ID   = your-user-id (credits go here)
  SARVA_REGION     = in / us / eu / uk

GOD MODE: Set SARVA_OWNER_ID=god for unlimited free compute!
