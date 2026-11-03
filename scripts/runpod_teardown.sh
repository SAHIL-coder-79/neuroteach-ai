#!/bin/bash
# ==============================================================================
# NEUROTEACH AI — RunPod Teardown & Immediate Termination Script
# Stops server process, scrubs temporary artifacts, and instructs safe shutdown.
# ==============================================================================
set -euo pipefail

echo "=== Terminating Inference Server Processes ==="
pkill -f "serve_adapter.py" || true
pkill -f "vllm" || true

echo "=== Scrubbing Checkpoint Weights from Worker ==="
rm -rf /workspace/adapter /workspace/serve_adapter.py

echo "=== Syncing Filesystem ==="
sync

echo "=== WORKER SHUTDOWN READY ==="
echo "Please terminate this pod immediately from your RunPod web console or CLI:"
echo "   runpodctl stop pod <POD_ID>"
echo "   runpodctl remove pod <POD_ID>"
echo "This stops all per-second GPU and disk billing immediately."

