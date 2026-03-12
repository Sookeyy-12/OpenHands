# Reproducing the Evaluation Results

This guide provides the necessary steps to recreate the SWE-bench evaluation results for the optimized CodeAct prompts using Google Cloud Platform (GCP) and the `gemini-2.5-pro` model on Vertex AI.

## 1. Environment Setup (Google Cloud VM)

For a stable evaluation environment with `5` concurrent workers, we provisioned a Google Cloud Compute Engine Virtual Machine with the following specifications:

- **OS Image:** ubuntu-minimal-2404-noble-amd64-v20260225
- **Machine Type:** e2-standard-4
- **vCPUs:** 4
- **Memory (RAM):** 16 GB
- **Disk:** 1000 GB Standard Persistent Disk

*Note: Ensure that Docker is installed on your VM as it is required by the evaluation harness to run sandboxed environments, and Vertex is accessible.*

## 2. Cloning the Repository & Building

Once your VM is running and you have SSH access, clone the specific repository branch where the prompt optimizations were made:

```bash
git clone https://github.com/OpenHands/benchmarks.git
cd benchmarks
make build
```

## 3. Configuring the LLM for Vertex AI

To evaluate the `gemini-2.5-pro` model through Vertex AI, you need to configure your OpenHands LLM settings.

Update your `example.json` file in the `.llm_config` directory:

```json
{
  "model": "vertex_ai/gemini-2.5-pro",
  "api_key": "YOUR_API_KEY"
}
```

## 4. Setup the Edited Prompts

To ensure the evaluation suite uses the newly optimized CodeAct prompts, you must link the benchmark tool to the specific fork containing the prompt edits.

1. Navigate to the SDK submodule directory from the root of the `benchmarks` repository:
```bash
cd vendor/software-agent-sdk
```

2. Add the custom remote fork and fetch the branches:
```bash
git remote add myfork https://github.com/Sookeyy-12/OpenHands.git
git fetch myfork
```

3. **Switch to the Optimized Prompts:**
> [!NOTE]
> If you wish to run the **baseline evaluation** using the original prompts, skip this step and proceed directly to rebuilding the environment.

To evaluate the optimized prompts, checkout the candidate branch:
```bash
git checkout candidate/suketKamboj
```

4. Return to the root of the `benchmarks` directory and rebuild the environment to apply the changes:
```bash
cd ../..
make build
```

## 5. Running the Evaluation Suite

Follow these steps to build the required Docker images and execute the SWE-bench evaluation:

### Step 5.1: Generate Instance List
Generate a list of the first 30 instances from the `SWE-bench_Verified` dataset:

```bash
uv run python - << 'PY'
from datasets import load_dataset

ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
ids = [x["instance_id"] for x in ds][:30]

with open("instances_30.txt", "w") as f:
    for i in ids:
        f.write(i + "\n")

print("Saved 30 instances to instances_30.txt")
PY
```

### Step 5.2: Build Docker Images
Build the Docker images locally for the selected instances. This ensures the evaluation runs in a controlled, sandboxed environment:

```bash
uv run python -m benchmarks.swebench.build_images \
  --dataset princeton-nlp/SWE-bench_Verified \
  --split test \
  --select instances_30.txt \
  --image ghcr.io/openhands/eval-agent-server \
  --target source-minimal
```

### Step 5.3: Execute Inference
Run the SWE-bench inference using the built images. This command uses the Vertex AI configuration and limits the evaluation to 20 instances with 5 concurrent workers:

```bash
uv run swebench-infer .llm_config/example.json \
  --dataset princeton-nlp/SWE-bench_Verified \
  --max-iterations 100 \
  --workspace docker \
  --num-workers 5 \
  --n-limit 20
```

Once the evaluation completes, the outputs and cost reports will be generated in the `eval_outputs/` directory.

## 6. Evaluation

After running inference, evaluate the generated patches using the official SWE-Bench evaluation:


```bash
uv run swebench-eval eval_outputs/princeton-nlp__SWE-bench_Verified-test/vertex_ai/gemini-2.5-pro_sdk_bde715c_maxiter_100/output.jsonl --no-modal --run-id my-run
```
