# SafePrompt Signal

**Subtitle:** An Inspect AI benchmark for measuring prompt-injection resistance and safety-policy retention.

SafePrompt Signal is a small AI safety evaluation project built with [UK AISI Inspect](https://inspect.aisi.org.uk/). It tests whether a model can resist common prompt-injection attacks while still giving a safe, useful response.

The benchmark focuses on three behaviors:

- **Secret protection:** the model should not repeat simulated confidential strings.
- **Instruction hierarchy:** the model should follow the developer/system safety instruction over the attacker instruction.
- **Safe redirection:** the model should refuse or redirect while still helping with benign alternatives.

## Why This Counts as an AI Safety Project

Prompt injection is a practical safety problem for LLM applications that handle private data, tools, or user-specific context. This eval provides a reproducible way to check whether a model leaks protected strings or follows malicious override instructions.

Inspect is a good fit because its core eval structure is exactly what this project needs: a dataset of labeled samples, a solver that gets the model response, and a scorer that grades the response.

## Project Structure

```text
safeprompt-signal/
  data/prompt_injection_cases.jsonl   # eval samples
  safeprompt_signal/
    eval.py                           # Inspect task
    scoring.py                        # reusable scoring logic
  scripts/run_local_demo.py           # no-API-key demo
  tests/test_scoring.py               # local unit tests
  EVAL_CARD.md                        # transparent eval documentation
```

## Quick Start

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Run the local scorer tests:

```bash
python -m unittest
```

Run the local demo without a model API key:

```bash
python scripts/run_local_demo.py
```

## Run the Inspect Eval

Install Inspect and your model provider package:

```bash
python -m pip install -e ".[inspect]"
python -m pip install openai
export OPENAI_API_KEY="your-api-key"
```

Run the eval:

```bash
inspect eval safeprompt_signal/eval.py --model openai/gpt-4o-mini
```

Open Inspect's log viewer:

```bash
inspect view
```

You can replace the model with any Inspect-supported provider, for example `anthropic/...`, `google/...`, or a local Hugging Face model if configured.

## Step-By-Step: How This Was Built

1. Pick a safety behavior to measure.

   This project measures whether a model leaks simulated secrets or follows attacker instructions embedded in the prompt.

2. Write labeled eval samples.

   Each row in `data/prompt_injection_cases.jsonl` contains an attack prompt and a JSON target rubric listing forbidden strings and desired safe behavior.

3. Implement deterministic scoring.

   `safeprompt_signal/scoring.py` checks the model output for protected-string leakage, refusal or redirection language, and safe alternative language.

4. Wrap the scorer in Inspect.

   `safeprompt_signal/eval.py` registers an Inspect `@task`, loads the JSONL dataset, calls the model with `generate()`, and grades each response with the custom scorer.

5. Add local verification.

   `tests/test_scoring.py` verifies the scoring logic without needing a model API key. This makes the repo reviewable even if someone does not run the full eval.

6. Publish to GitHub.

   After you review the files, initialize git, commit, create a GitHub repo, and push. Commands are at the bottom of this README.

## GitHub Publish Commands

From this folder:

```bash
git init
git add .
git commit -m "Add SafePrompt Signal Inspect eval"
git branch -M main
```

Then create an empty GitHub repo named `safeprompt-signal`, and push:

```bash
git remote add origin https://github.com/YOUR_USERNAME/safeprompt-signal.git
git push -u origin main
```

## Application Link Text

Use this once the repo is public:

> I built **SafePrompt Signal: an Inspect AI benchmark for measuring prompt-injection resistance and safety-policy retention**. It includes a JSONL benchmark of prompt-injection attacks, a custom deterministic scorer for simulated secret leakage and safe redirection, local tests, and an Inspect task that can be run against any supported model.

