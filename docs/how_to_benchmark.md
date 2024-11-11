---
title: How to Benchmark
---

# Introduction

!!! note

    For benchmarking, it's preferable to use the `SERVER` + `WORKER` modes.

    You can find the guide on how to install in this configuration [here](AdminManual/WorkingModes/worker_to_database.md).

Assuming you have Visionatrix installed, you can proceed with benchmarking.

You don't need to run the benchmark script on the same machine where Visionatrix is installed. Therefore, clone the Visionatrix documentation repository wherever it's convenient for you:

```bash
git clone https://github.com/Visionatrix/VixFlowsDocs.git
```

## Setting Up a Virtual Environment (Optional)

It's recommended to use a virtual environment to avoid conflicts with other Python packages on your system. Here's how you can set up a virtual environment that works on macOS and Linux (assuming all OS packages are installed):

```bash
cd VixFlowsDocs && python3 -m venv venv && source venv/bin/activate
```

This creates a new virtual environment named `venv` and activates it. You can now proceed to install the dependencies:

```bash
pip install -r requirements.txt
```

If you prefer not to use a virtual environment, you can install the dependencies directly:

```bash
cd VixFlowsDocs && pip install -r requirements.txt
```

## Running the Benchmark Script

The benchmark script is located in the `scripts/benchmarks` directory.

You can run the script with the default parameters. The working directory doesn't matter because the script uses relative paths from its own location.

If your Visionatrix instance does not have authentication enabled (for example, it's running in `DEFAULT` mode), simply run the script:

```bash
python3 scripts/benchmarks/benchmark.py
```

The script will prompt you to select the test suite you want to run. Enter the number corresponding to your choice:

```
Please select the test suite you want to run:
1. SDXL Suite
2. PORTRAITS Suite
3. OTHER Suite
4. FLUX Suite
5. HEAVY(24GB+ VRAM) Suite
Enter the number of the suite (1/2/3/4/5):
```

!!! note

    The script will automatically install the flows from the selected test suite if they are not already installed. It will start testing as soon as the first flow is installed and will install the next flows in parallel.

    This should not significantly affect performance (unless your Visionatrix is running in `DEFAULT` mode).

Upon completion of the tests, a folder with results will appear in the `results` directory, named with the date, hardware, and test suite. For example:

```
results/2024-11-11-EPYC_75F3-4090-SDXL/
```

Inside this folder, you will find the summary JSON file (e.g., `summary-2024-11-11-EPYC_75F3-4090-SDXL.json`) and the detailed results for each flow and test case.

The `benchmark.py` script supports resuming interrupted tests. If you run the script again for the same test suite, it will skip tests that have already been completed.

You should set the environment variable `HARDWARE` in the format `"CPU-GPU"` before running the script. If you forget to set it, you can rename the results folder and summary file after the tests are complete to include your hardware specifications.

If you want to add your results to the documentation, copy the summary JSON file to the `hardware_results` folder and open a pull request with this file.

## Generating Hardware Results Table

After running the benchmark and collecting results, you can generate a Markdown table summarizing the hardware test results using the `generate_hardware_results.py` script located in the `scripts/benchmarks` directory.

Run the script to generate the `hardware_results.md` file:

```bash
python3 scripts/benchmarks/generate_hardware_results.py
```

This script will traverse the `results` directory, process the summary JSON files, and generate a Markdown table saved as `hardware_results.md`.

# Supported Environment Variables

As mentioned earlier, the `HARDWARE` variable is supported. Example usage:

```bash
HARDWARE="EPYC_75F3-4090" python3 scripts/benchmarks/benchmark.py
```

Another supported variable is `SERVER_URL`, for example:

```bash
SERVER_URL="http://192.168.1.10:8288" python3 scripts/benchmarks/benchmark.py
```

Use this when Visionatrix is located on another machine.

If you need to provide authentication credentials for the Visionatrix server, you can do so using the variables `USER_NAME` and `USER_PASSWORD`.

Example usage along with `SERVER_URL`:

```bash
SERVER_URL="http://192.168.1.10:8288" USER_NAME="admin" USER_PASSWORD="admin" python3 scripts/benchmarks/benchmark.py
```

The `COUNT` variable controls the number of tasks created for each test case. By default, it is set to `2`. You can set it to `1`, `3`, `4`, etc. The higher the number, the more accurate the hardware test will be.

Another supported variable is `REMOVE_RESULTS`. By default, it is `1`, which means that the tasks created during testing will be deleted from Visionatrix after completion. You can set it to `0` if you don't want the tasks to be deleted.

If you have a slow internet connection and not all flows from your selected test suite are installed, you might want to set a custom value for the `FLOW_INSTALL_TIMEOUT` variable.

By default, it is set to 1800 seconds (30 minutes). If the flow does not download within this time, the script will produce an error (but this does not cancel the flow installation, and eventually it will be installed on the server).

The variables `PAUSE_INTERVAL` (default value `0`) and `PAUSE_INTERVAL_AFTER_WARMUP` (default value `0`) control the pause time between tests.

- The `PAUSE_INTERVAL` variable defines the pause time in seconds between test cases (this might be useful if, during tests, your device heats up and you want to prevent overheating).

- The `PAUSE_INTERVAL_AFTER_WARMUP` variable defines the interval of time to wait after the warm-up run. During the warm-up, models are loaded into memory. This pause can be useful on laptops or devices with insufficient cooling.

The `UNLOAD_MODELS_BEFORE_WARMUP` variable controls whether models are unloaded from memory before the warm-up run. By default, it is set to `1`. Setting it to `0` will skip unloading models before the warm-up.

# Conclusion

By following the steps outlined above, you can successfully benchmark your Visionatrix setup. Adjust the environment variables as needed to suit your specific hardware and network conditions. If you encounter any issues or have results you'd like to share, feel free to contribute to the documentation by opening a pull request.

Happy benchmarking!
