## REQUIREMENTS

- Visual Studio Code:
https://code.visualstudio.com/download 
   
- Python:
https://www.python.org/downloads/ 

- Git:
https://git-scm.com/install/

## PROJECT SETUP: CLONING THE PROJECT

1. Open Visual Studio Code
2. Click Source Control (Left sidebar under the magnifying glass icon)
3. Click “Clone Repository” 
4. Paste the repo URL:
   ```
   https://github.com/albertbautista/kth-smallest-element
   ```
5. Sign in if prompted (VS Code may ask for github login the first time)
6. Select the directory where you want to clone the repository
7. After cloning, VS Code will ask you if you want to open the cloned folder, click Open
8. You can now pull, stage, commit, and push changes to the repo

## INSTALLING DEPENDENCIES

From the root of the cloned repository, run:

```bash
pip install -r requirements.txt
```

This installs `numpy` and `matplotlib`, which are required by the benchmark script.

## RUNNING THE BENCHMARK

```bash
cd experiments
```

```bash
python run_benchmarks.py
```

This will:
- Validate correctness of both algorithms and print PASS/FAIL per size
- Append a timestamped results table to `results/runtime.txt`
- Save `results/runtime_chart.png` — runtime vs input size (log-log)
- Save `results/memory_chart.png` — peak memory vs input size (log-log)
