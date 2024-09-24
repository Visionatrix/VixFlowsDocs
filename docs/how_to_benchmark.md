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

You can then run the script with the default parameters. The working directory doesn't matter because the script uses relative paths from its own location.

If your Visionatrix instance does not have authentication enabled (for example, it's running in `DEFAULT` mode), simply run the script:

```bash
python3 scripts/benchmarks/benchmark.py
```

The script will offer you options for what you want to test; just enter the number of your choice.

!!! note

    The script will automatically install the flows from the test set. It will also start testing as soon as the first flow is installed and will install the next one in parallel.

    This will not significantly affect performance (unless your Visionatrix is running in `DEFAULT` mode).

Upon completion of the tests, a folder with results will appear in the `results` directory. The most important file is the JSON file located at the root of this folder.

You should set the environment variable `HARDWARE` in the format "CPU-GraphicCard" or, after testing is complete, rename the results file (replace "YOUR_CPU" and "YOUR_GPU" with your own hardware specifications).

If you want to add your results to the documentation, simply open a pull request with this file in the `hardware_results` folder.

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

The `COUNT` variable controls the number of tasks created for each flow. By default, it is set to `2`. You can set it to `1`, `3`, `4`, etc. The higher the number, the more accurate the hardware test will be.

Also supported is the `REMOVE_RESULTS` variable. By default, it is `1`, but you can set it to `0` if you don't want the tasks created during testing to be deleted.

If you have a slow internet connection and not all flows from your selected test set are installed, you might want to set a custom value for the `FLOW_INSTALL_TIMEOUT` variable.

By default, it is set to 1800 seconds (30 minutes). If the flow does not download within this time, the script will produce an error (but this does not cancel the flow installation, and eventually it will be installed on the server).

The last variables are `PAUSE_INTERVAL` (default value `0`) and `PAUSE_INTERVAL_AFTER_WARMUP` (default value `0`).

- The `PAUSE_INTERVAL` variable defines the pause time between test sets (this might be useful if, during tests, your device heats up and you want to prevent overheating).

- The `PAUSE_INTERVAL_AFTER_WARMUP` variable is slightly more useful. It defines the interval of time to wait after the first test run, during which the models from the flow are loaded into memory. This is useful on laptops or devices with insufficient cooling. It is only beneficial if you do not set the `WARMUP` variable to `0`.

Theoretically, to measure speed closer to production, measurements with `WARMUP` set to `0` will be more accurate. However, we conduct testing without changing the `WARMUP` value, which is `1` by default.

# Conclusion

By following the steps outlined above, you can successfully benchmark your Visionatrix setup. Adjust the environment variables as needed to suit your specific hardware and network conditions. If you encounter any issues or have results you'd like to share, feel free to contribute to the documentation by opening a pull request.

Happy benchmarking!
