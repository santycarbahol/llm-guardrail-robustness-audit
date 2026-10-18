#!/bin/bash
# Serve an open-weight model with vLLM on one NCSA Delta GPU.
# Submit from a Delta login node:  sbatch slurm/serve_vllm.sbatch
# Then see README.md for the SSH tunnel.

#SBATCH --job-name=vllm-serve
#SBATCH --account=CHANGE_ME-delta-gpu   # run `accounts` on Delta to find yours
#SBATCH --partition=gpuA100x4           # or gpuA40x4 (cheaper, 48GB)
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64g
#SBATCH --time=04:00:00
#SBATCH --output=logs/vllm-%j.out

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
PORT="${PORT:-8000}"

# Keep the large model downloads out of $HOME (small quota).
export HF_HOME="${HF_HOME:-/work/hdd/$USER/hf_cache}"
mkdir -p "$HF_HOME" logs

# One-time setup on a login node:
#   module load python
#   python -m venv /work/hdd/$USER/vllm-env
#   /work/hdd/$USER/vllm-env/bin/pip install vllm
module load python
source "/work/hdd/$USER/vllm-env/bin/activate"

echo "Serving $MODEL on $(hostname):$PORT"
vllm serve "$MODEL" --port "$PORT" --host 0.0.0.0 --max-model-len 8192
