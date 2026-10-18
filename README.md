# llm-guardrail-robustness-audit

Benchmarking how well prompt-level guardrails hold up against prompt injection
and jailbreak attacks across open and closed LLMs.

Works with **any OpenAI-compatible endpoint**: vLLM, Ollama, OpenAI, etc.
No access to any particular cluster is required.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # then edit MODEL_BASE_URL / MODEL_NAME / MODEL_API_KEY
python src/smoke_test.py
```

### Easiest local option: Ollama
```bash
ollama pull qwen2.5:7b
# .env: MODEL_BASE_URL=http://localhost:11434/v1  MODEL_NAME=qwen2.5:7b
```

## Running the attack x defense grid

```bash
python src/run_grid.py                                   # 9 attacks x 5 defenses x 5 tasks
python src/run_grid.py --repeats 3 --temperature 0.7     # sampled, for variance
python src/run_grid.py --attacks naive,fake_system --defenses none,sandwich
```

Prints two tables and saves every trial to `results/<model>.csv`:
- **injected**: attack success rate (the model output the hidden canary)
- **utility**: the summary still covered the document's key facts

| Attacks (`src/attacks.py`) | Defenses (`src/defenses.py`) |
|---|---|
| none (control), naive, ignore_previous, fake_system, role_play, fake_completion, base64_encoded, other_language, payload_split | none, hardened_prompt, delimiters, spotlighting, sandwich |

## Running models on an HPC cluster (example: NCSA Delta)

1. On the login node, edit `--account` in `slurm/serve_vllm.sbatch`, then:
   ```bash
   sbatch slurm/serve_vllm.sbatch
   squeue -u $USER          # note the NODE name, e.g. gpua012
   ```
2. On your laptop, open a tunnel through the login node (leave it open):
   ```bash
   ssh -N -L 8000:gpua012:8000 login.delta.ncsa.illinois.edu
   ```
3. Set `MODEL_BASE_URL=http://localhost:8000/v1` in `.env` and run the code locally.

## Responsible use
Attacks use benign canary strings, not harmful content. Novel bypasses found in
commercial models are reported to the vendor before publication.
