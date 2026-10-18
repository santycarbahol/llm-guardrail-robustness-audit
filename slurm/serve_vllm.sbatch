#!/bin/bash
# Serve an open-weight model with vLLM on one NCSA Delta GPU.
# Submit from the repo root on a Delta login node (run `accounts` for your account):
#   sbatch --account=<yours>-delta-gpu slurm/serve_vllm.sbatch
# Then see README.md for the SSH tunnel.

#SBATCH --job-name=vllm-serve
#SBATCH --partition=gpuA100x4           # or gpuA40x4 (cheaper, 48GB)
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64g
#SBATCH --time=04:00:00
#SBATCH --output=logs/vllm-%j.out

MODEL="${MODEL:-Qwen/Qwen2.5-7B-Instruct}"
PORT="${PORT:-8000}"

# Clone the repo under your project's /work/hdd/<project>/ (see `quota`), not $HOME,
# so the venv and model downloads below land there too.
cd "$SLURM_SUBMIT_DIR"
export HF_HOME="${HF_HOME:-$SLURM_SUBMIT_DIR/hf_cache}"
mkdir -p "$HF_HOME" logs

# One-time setup on a login node, from the repo root:
#   module load python
#   python -m venv vllm-env
#   vllm-env/bin/pip install vllm
module load python
source vllm-env/bin/activate

echo "Serving $MODEL on $(hostname):$PORT"
vllm serve "$MODEL" --port "$PORT" --host 0.0.0.0 --max-model-len 8192
