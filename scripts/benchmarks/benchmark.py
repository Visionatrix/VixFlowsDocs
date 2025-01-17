from __future__ import annotations

import asyncio
import json
import math
import os
import statistics
import typing
from datetime import datetime
from pathlib import Path

import httpx
import yaml
from pydantic import BaseModel, Field

os.chdir(Path(__file__).parent)

# ------------------------------------------
# Global variables and constants
# ------------------------------------------

SERVER_URL = os.environ.get("SERVER_URL", "http://127.0.0.1:8288")
REMOVE_RESULTS_FROM_VISIONATRIX = int(os.environ.get("REMOVE_RESULTS", "1"))
DEFAULT_NUMBER_OF_TEST_CASE_RUNS = int(os.environ.get("COUNT", "2"))
HARDWARE = os.environ.get("HARDWARE", "YOUR_CPU-YOUR_GPU").strip("\"'")
FLOW_INSTALL_TIMEOUT = int(os.environ.get("FLOW_INSTALL_TIMEOUT", "1800"))
TEST_START_TIME = datetime.now()
RESULTS_DIR: Path
SELECTED_WORKER: dict

USER_NAME, USER_PASSWORD = os.getenv("USER_NAME", "admin"), os.getenv(
    "USER_PASSWORD", "admin"
)
BASIC_AUTH = (
    httpx.BasicAuth(USER_NAME, USER_PASSWORD) if USER_NAME and USER_PASSWORD else None
)
if BASIC_AUTH:
    print(f"Using authentication for connect, user: '{USER_NAME}'")

PAUSE_INTERVAL = int(os.environ.get("PAUSE_INTERVAL", "0"))
PAUSE_INTERVAL_AFTER_WARMUP = int(os.environ.get("PAUSE_INTERVAL_AFTER_WARMUP", "0"))
UNLOAD_MODELS_BEFORE_WARMUP = os.environ.get("UNLOAD_MODELS_BEFORE_WARMUP", "1")
EXECUTION_PROFILER = True

FIRST_TEST_FLAG = True
SELECTED_TEST_FLOW_SUITES: list[tuple[str, list["FlowTest"]]] = []
SELECTED_TEST_FLOW_SUITE = []
INSTALLED_FLOWS_CACHE = []

PARALLEL_INSTALLS = 5  # up to 5 flows can be installed in parallel

# ------------------------------------------
# Pydantic models
# ------------------------------------------


class TestCase(BaseModel):
    name: str = Field(
        ..., description="The name of the test case for this specific flow."
    )
    input_params: dict[str, typing.Any] = Field(
        {},
        description="A set of input parameters to pass to the flow during the task creation.",
    )
    input_files: dict[str, str | Path] = Field(
        {},
        description="A set of input files to pass to the flow during the task creation.",
    )
    count: int = Field(
        DEFAULT_NUMBER_OF_TEST_CASE_RUNS,
        description="Number of task executions to perform after the warm-up run.",
    )


class FlowTest(BaseModel):
    flow_name: str = Field(..., description="The name of the flow that will be tested.")
    test_cases: list[TestCase] = Field(
        ...,
        description="A list of test cases with different parameter sets for this flow.",
    )


# ------------------------------------------
# Utilities / Shared functions
# ------------------------------------------


def validate_flows_test_cases(flows_test_cases: list[FlowTest]):
    """
    Basic validation to ensure that each flow_name is unique (within a single suite),
    and that each test_case name is unique for that flow.
    """
    flow_names = set()
    for flow_test in flows_test_cases:
        if flow_test.flow_name in flow_names:
            raise ValueError(f"Duplicate flow_name found: {flow_test.flow_name}")
        flow_names.add(flow_test.flow_name)

        test_names = set()
        for test_case in flow_test.test_cases:
            if test_case.name in test_names:
                raise ValueError(
                    f"Duplicate test name '{test_case.name}' found in flow '{flow_test.flow_name}'"
                )
            test_names.add(test_case.name)


async def is_server_online() -> bool:
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.get(f"{SERVER_URL}/vapi/flows/installed")
            response.raise_for_status()  # Ensure server responds correctly
            return True
        except (httpx.RequestError, httpx.HTTPStatusError):
            print(f"Server at {SERVER_URL} is unreachable.")
            return False


async def get_installed_flows() -> list:
    global INSTALLED_FLOWS_CACHE

    if INSTALLED_FLOWS_CACHE:
        return INSTALLED_FLOWS_CACHE
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        response = await client.get(f"{SERVER_URL}/vapi/flows/installed", timeout=60)
        response.raise_for_status()
        INSTALLED_FLOWS_CACHE = response.json()
        return INSTALLED_FLOWS_CACHE


async def is_flow_installed(flow_name: str) -> bool:
    installed_flows = await get_installed_flows()
    return any(flow["name"] == flow_name for flow in installed_flows)


async def get_flow_display_names() -> dict[str, str]:
    installed_flows = await get_installed_flows()
    return {flow["name"]: flow["display_name"] for flow in installed_flows}


async def install_flow(flow_name: str) -> bool:
    """Request installation of a single flow, then wait for completion or error."""
    print(f"Installing flow '{flow_name}'...")
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.post(
                f"{SERVER_URL}/vapi/flows/flow", params={"name": flow_name}
            )
            if response.status_code == 204:
                print(f"Successfully started the installation of flow '{flow_name}'.")
                success = await wait_for_installation_to_complete(flow_name)
                if success:
                    INSTALLED_FLOWS_CACHE.clear()
                return success
            if response.status_code == 404:
                print(f"Flow '{flow_name}' not found.")
            elif response.status_code == 409:
                print("Another flow installation is in progress.")
            else:
                print(f"Unexpected response: {response.status_code} - {response.text}")
        except httpx.RequestError as exc:
            print(f"An error occurred during installation: {exc.request.url!r}: {exc}")
    return False


async def wait_for_installation_to_complete(
    flow_name: str, poll_interval: int = 5, timeout: int = FLOW_INSTALL_TIMEOUT
) -> bool:
    """Poll server for installation progress of a given flow until it's complete or fails."""
    elapsed_time = 0
    max_read_timeout_count = 20
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        while elapsed_time < timeout:
            try:
                response = await client.get(f"{SERVER_URL}/vapi/flows/install-progress")
                response.raise_for_status()
                install_progress = response.json()

                for flow in install_progress:
                    if flow["name"] == flow_name:
                        if flow["error"]:
                            print(
                                f"Error during installation of flow '{flow_name}': {flow['error']}"
                            )
                            return False
                        if flow["progress"] == 100:
                            print(f"Flow '{flow_name}' installation completed.")
                            return True
                        rounded_flow_progress = math.floor(flow["progress"] * 10) / 10
                        print(
                            f"Flow '{flow_name}' installation progress: {rounded_flow_progress}%"
                        )
                        break

                await asyncio.sleep(poll_interval)
                elapsed_time += poll_interval
                max_read_timeout_count = 20
            except httpx.ReadTimeout:
                max_read_timeout_count -= 1
                print(
                    f"Flow '{flow_name}': ReadTimeout error during installation progress check, "
                    f"continuing... {max_read_timeout_count} tries left"
                )
                if not max_read_timeout_count:
                    print(
                        f"Installation of flow '{flow_name}' failed due to repeated timeouts."
                    )
                    return False
            except httpx.RequestError as exc:
                print(
                    f"An error occurred while checking installation progress: {exc.request.url!r}: {exc}"
                )
                return False

    print(f"Installation of flow '{flow_name}' timed out after {timeout} seconds.")
    return False


# ------------------------------------------
# Task creation, monitoring, and results
# ------------------------------------------


async def create_task(
    flow_name: str,
    input_params: dict,
    count: int,
    input_files: dict | None,
    warm_up: bool,
) -> list[int]:
    """Create one or more tasks on the server for a given flow, with optional file uploads."""
    files_to_upload = {}
    if input_files:
        for param_id, file_name in input_files.items():
            file_path = os.path.join("input_files", file_name)
            try:
                files_to_upload[param_id] = open(file_path, "rb")
            except FileNotFoundError:
                print(f"File {file_name} not found in the input_files directory.")
                return []

    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            form_data = {
                "count": count,
                **input_params,
            }
            response = await client.put(
                f"{SERVER_URL}/vapi/tasks/create/{flow_name}",
                data=form_data,
                files=files_to_upload,
                headers={
                    "X-WORKER-EXECUTION-PROFILER": (
                        "0" if warm_up else str(int(EXECUTION_PROFILER))
                    ),
                    "X-WORKER-UNLOAD-MODELS": (
                        UNLOAD_MODELS_BEFORE_WARMUP if warm_up else "0"
                    ),
                    "X-WORKER-ID": SELECTED_WORKER["worker_id"],
                },
                timeout=60,
            )
            if response.status_code == 200:
                return response.json().get("tasks_ids", [])
            else:
                print(
                    f"Failed to create task for {flow_name}. Status code: {response.status_code}"
                )
        except httpx.RequestError as exc:
            print(f"An error occurred during task creation: {exc.request.url!r}: {exc}")
        finally:
            for file_handle in files_to_upload.values():
                file_handle.close()

    return []


async def get_task_progress(task_id: int, poll_interval: int = 5) -> dict:
    """Poll the progress for a single task until completion or error, returns the task JSON."""
    max_read_timeout_count = 20
    previous_progress = 0.0
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        while True:
            try:
                response = await client.get(
                    f"{SERVER_URL}/vapi/tasks/progress/{task_id}"
                )
                if response.status_code == 200:
                    task_data = response.json()
                    if task_data.get("error"):
                        print(
                            f"Task with id={task_id} failed with error: {task_data['error']}"
                        )
                        return task_data
                    progress = task_data.get("progress", 0.0)
                    if progress == 100.0:
                        print(
                            f"Task `{task_data['name']}` with id={task_id}, progress: 100%"
                        )
                        return task_data
                    if progress > 0.0 and progress != previous_progress:
                        rounded_task_progress = math.floor(progress * 10) / 10
                        print(
                            f"Task `{task_data['name']}` with id={task_id}, progress: {rounded_task_progress}%"
                        )
                        previous_progress = progress
                        max_read_timeout_count = 20
                await asyncio.sleep(poll_interval)
            except httpx.ReadTimeout:
                max_read_timeout_count -= 1
                print(
                    f"Task with id={task_id}: ReadTimeout error, continuing... {max_read_timeout_count} tries left"
                )
                if not max_read_timeout_count:
                    return {"error": "read timeout error"}
            except httpx.RequestError as exc:
                print(
                    f"An error occurred while fetching task progress: {exc.request.url!r}: {exc}"
                )
                return {"error": "request_error"}


async def run_test_case(
    flow_name: str,
    test_case: TestCase,
    results_summary: dict,
    test_semaphore: asyncio.Semaphore,
    suite_identifier: str,
):
    """
    Runs a single TestCase for a particular flow (with concurrency limited by test_semaphore).
    1) Warm up (optional unload + no execution profiler).
    2) Actual runs (with profiler).
    3) Collect and store results.
    """
    async with test_semaphore:
        global FIRST_TEST_FLAG

        if FIRST_TEST_FLAG:
            FIRST_TEST_FLAG = False
        else:
            if PAUSE_INTERVAL:
                print(
                    f"Pausing for {PAUSE_INTERVAL} seconds before starting next test."
                )
                await asyncio.sleep(PAUSE_INTERVAL)

        input_params = test_case.input_params
        input_files = test_case.input_files

        # Prepare result structures
        flow_results = results_summary.setdefault(flow_name, {})
        test_case_results = flow_results.setdefault(test_case.name, set())

        # Load existing configurations (if any)
        flow_test_case_dir = os.path.join(RESULTS_DIR, f"{flow_name}__{test_case.name}")
        metadata_file = os.path.join(flow_test_case_dir, "metadata.json")
        existing_configurations = set()
        if os.path.exists(metadata_file):
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                existing_configurations.update(metadata["results"].keys())

        test_case_results.update(existing_configurations)

        worker_engine_details = SELECTED_WORKER["engine_details"]
        configuration_key = f"{worker_engine_details['vram_state']}_disable_smart_memory_{worker_engine_details['disable_smart_memory']}"

        # Skip if we already have results for this configuration
        if configuration_key in test_case_results:
            print(
                f"Results for flow '{flow_name}', test case '{test_case.name}', configuration '{configuration_key}' already exist. Skipping."
            )
            return

        print(f"Warming up... (flow_name={flow_name}, test_case={test_case.name})")
        warmup_task_id = await create_task(
            flow_name, input_params, 1, input_files, True
        )
        if not warmup_task_id:
            print(
                f"Failed to create warmup task for flow '{flow_name}', test case: {test_case.name}"
            )
            return
        r = await get_task_progress(warmup_task_id[0])
        if r.get("error", ""):
            print(
                f"Failed to finish warmup task for flow '{flow_name}', test case: {test_case.name}"
                f"\nError: {r['error']}"
            )
            return

        if REMOVE_RESULTS_FROM_VISIONATRIX:
            await delete_task(warmup_task_id[0])

        if PAUSE_INTERVAL_AFTER_WARMUP:
            print(f"Pausing for {PAUSE_INTERVAL_AFTER_WARMUP} seconds after warmup.")
            await asyncio.sleep(PAUSE_INTERVAL_AFTER_WARMUP)

        # Actual test runs
        task_ids = await create_task(
            flow_name, input_params, test_case.count, input_files, False
        )
        if not task_ids:
            print(
                f"Failed to create tasks for flow '{flow_name}', test case: {test_case.name}"
            )
            return

        # Monitor tasks
        task_progress_coroutines = [get_task_progress(task_id) for task_id in task_ids]
        task_results = await asyncio.gather(*task_progress_coroutines)

        # Save results
        summary = await save_results(
            flow_name,
            test_case.name,
            test_case,
            task_results,
            worker_engine_details["vram_state"],
            worker_engine_details["disable_smart_memory"],
        )
        if summary:
            # Update summary on disk
            await generate_results_summary_json(results_summary, suite_identifier)


# ------------------------------------------
# Installation concurrency
# ------------------------------------------


async def install_flows_in_parallel(flow_names: list[str]) -> dict[str, bool]:
    """
    Installs the given list of flows in parallel, up to PARALLEL_INSTALLS concurrency.
    Returns a dict of { flow_name: bool installed_ok }.
    """
    semaphore = asyncio.Semaphore(PARALLEL_INSTALLS)
    results = {}

    async def install_one_flow(name: str):
        async with semaphore:
            if await is_flow_installed(name):
                print(f"Flow '{name}' is already installed.")
                results[name] = True
            else:
                success = await install_flow(name)
                results[name] = success

    tasks = [asyncio.create_task(install_one_flow(fname)) for fname in flow_names]
    await asyncio.gather(*tasks)

    return results


# ------------------------------------------
# Saving, deleting, summarizing results
# ------------------------------------------


async def save_results(
    flow_name: str,
    test_case_name: str,
    test_case: TestCase,
    task_results: list,
    vram_state: str,
    disable_smart_memory: typing.Union[bool, str],
):
    # Ensure results directory
    os.makedirs(RESULTS_DIR, exist_ok=True)
    flow_test_case_dir = os.path.join(RESULTS_DIR, f"{flow_name}__{test_case_name}")
    os.makedirs(flow_test_case_dir, exist_ok=True)

    failed_tasks = [task for task in task_results if task.get("error")]
    if failed_tasks:
        print(
            f"Some tasks failed for flow '{flow_name}', test case '{test_case_name}' with errors:"
        )
        for i in failed_tasks:
            print(f" - {i['error']}")

    # Gather execution times
    execution_times = [
        task["execution_time"] for task in task_results if "execution_time" in task
    ]
    if not execution_times:
        return None

    summary = {
        "min_exec_time": min(execution_times),
        "max_exec_time": max(execution_times),
        "avg_exec_time": statistics.mean(execution_times),
    }

    # Load or create metadata
    metadata_file = os.path.join(flow_test_case_dir, "metadata.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, "r") as f:
            metadata = json.load(f)
    else:
        metadata = {
            "flow_name": flow_name,
            "test_case": test_case.model_dump(),
            "results": {},
        }

    # Remove 'flow_comfy' from the tasks before saving
    for task in task_results:
        task.pop("flow_comfy", None)

    # Update results in metadata
    configuration_key = f"{vram_state}_disable_smart_memory_{disable_smart_memory}"
    metadata["results"][configuration_key] = {
        "summary": summary,
        "task_results": task_results,
    }

    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)

    print(
        f"Results saved to {flow_test_case_dir} for configuration '{configuration_key}'"
    )

    # Save outputs for each task
    for task in task_results:
        task_id = task.get("task_id")
        if task_id:
            for output in task.get("outputs", []):
                node_id = output.get("comfy_node_id")
                if node_id:
                    output_data = await get_task_results(task_id, node_id)
                    if output_data:
                        await save_output(
                            flow_test_case_dir,
                            task_id,
                            node_id,
                            output_data,
                            configuration_key=configuration_key,
                        )

            if REMOVE_RESULTS_FROM_VISIONATRIX:
                await delete_task(task_id)

    # Save the first available flow_comfy (if any)
    for result in task_results:
        if "flow_comfy" in result:
            await save_flow_comfy(
                flow_name, test_case_name, result["flow_comfy"], configuration_key
            )
            break

    return summary


async def get_task_results(task_id: int, node_id: int) -> bytes:
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.get(
                f"{SERVER_URL}/vapi/tasks/results",
                params={"task_id": task_id, "node_id": node_id},
            )
            if response.status_code == 200:
                return response.content
            print(
                f"Failed to get results for task {task_id}, node {node_id}. Status code: {response.status_code}"
            )
        except httpx.RequestError as exc:
            print(
                f"An error occurred while fetching task results: {exc.request.url!r}: {exc}"
            )
        return b""


async def save_output(
    flow_test_case_dir: str,
    task_id: int,
    node_id: int,
    output_data: bytes,
    configuration_key: str,
    file_extension: str = "png",
):
    output_file = os.path.join(
        flow_test_case_dir,
        f"result__task_{task_id}_node_{node_id}_{configuration_key}.{file_extension}",
    )
    with open(output_file, "wb") as f:
        f.write(output_data)
    print(
        f"Output saved for task {task_id}, node {node_id}, configuration '{configuration_key}' to {output_file}"
    )


async def delete_task(task_id: int) -> None:
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.delete(
                f"{SERVER_URL}/vapi/tasks/task", params={"task_id": task_id}
            )
            if response.status_code != 204:
                print(
                    f"Failed to delete results for task {task_id}. Status code: {response.status_code}"
                )
        except httpx.RequestError as exc:
            print(
                f"An error occurred while deleting task results: {exc.request.url!r}: {exc}"
            )


async def save_flow_comfy(
    flow_name: str, test_case_name: str, flow_comfy: dict, configuration_key: str
):
    flow_test_case_dir = os.path.join(RESULTS_DIR, f"{flow_name}__{test_case_name}")
    os.makedirs(flow_test_case_dir, exist_ok=True)
    flow_comfy_file = os.path.join(
        flow_test_case_dir, f"flow_comfy_{configuration_key}.json"
    )
    with open(flow_comfy_file, "w") as f:
        json.dump(flow_comfy, f, indent=4)


async def generate_results_summary_json(results_summary: dict, suite_identifier: str):
    """Create a summarized JSON file in the results folder with average times and memory usage info."""
    summary_file = os.path.join(
        RESULTS_DIR,
        f"summary-{TEST_START_TIME.strftime('%Y-%m-%d')}-{HARDWARE}-{suite_identifier}.json",
    )

    results_data = {
        "test_time": TEST_START_TIME.strftime("%Y/%m/%d"),
        "flows": [],
    }

    flows_display_names = await get_flow_display_names()

    for flow_name in results_summary.keys():
        flow_data = {
            "flow_name": flow_name,
            "flow_display_name": flows_display_names.get(flow_name, flow_name),
            "test_cases": [],
        }

        flow_test_cases = results_summary[flow_name]
        for test_case_name in flow_test_cases.keys():
            flow_test_case_dir = os.path.join(
                RESULTS_DIR, f"{flow_name}__{test_case_name}"
            )
            metadata_file = os.path.join(flow_test_case_dir, "metadata.json")

            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    results = metadata.get("results", {})
                    for configuration_key, config_results in results.items():
                        summary = config_results.get("summary", {})
                        task_results = config_results.get("task_results", [])
                        max_memory_usages = [
                            details.get("max_memory_usage")
                            for details in (
                                result.get("execution_details")
                                for result in task_results
                            )
                            if details and details.get("max_memory_usage") is not None
                        ]
                        # Attempt to parse the config key
                        parts = configuration_key.split("_disable_smart_memory_")
                        if len(parts) == 2:
                            vram_state, disable_smart_memory_str = parts
                            disable_smart_memory = disable_smart_memory_str == "True"
                        else:
                            vram_state = configuration_key
                            disable_smart_memory = None

                        flow_data["test_cases"].append(
                            {
                                "test_case": test_case_name,
                                "vram_state": vram_state,
                                "disable_smart_memory": disable_smart_memory,
                                "avg_exec_time": summary.get("avg_exec_time"),
                                "avg_max_memory_usage": (
                                    statistics.mean(max_memory_usages)
                                    if max_memory_usages
                                    else None
                                ),
                            }
                        )

        results_data["flows"].append(flow_data)

    with open(summary_file, "w") as f:
        json.dump(results_data, f, indent=4)

    print(f"Test results summary saved to {summary_file}")


# ------------------------------------------
# Worker selection
# ------------------------------------------


async def get_available_workers() -> list[dict]:
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.get(f"{SERVER_URL}/vapi/workers/info", timeout=60)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            print(
                f"An error occurred while fetching workers: {exc.request.url!r}: {exc}"
            )
            return []


async def select_worker():
    """
    If there's only one available worker, auto-select it;
    otherwise, ask the user which worker to use.
    """
    global SELECTED_WORKER

    workers = await get_available_workers()
    if not workers:
        print("No available workers found.")
        exit(1)

    if len(workers) == 1:
        selected_worker_id = workers[0]["worker_id"]
        print(f"Only one worker available. Auto-selecting: '{selected_worker_id}'")
        SELECTED_WORKER = workers[0]
        return

    print("Available workers:")
    for i, worker in enumerate(workers):
        print(f"{i + 1}. '{worker['worker_id']}'")

    while True:
        try:
            choice = int(input("Select a worker by number: ")) - 1
            if 0 <= choice < len(workers):
                selected_worker_id = workers[choice]["worker_id"]
                print(f"Selected worker: '{selected_worker_id}'")
                SELECTED_WORKER = workers[choice]
                return
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")


# ------------------------------------------
# Test suite loading and user selection
# ------------------------------------------


def load_test_suites_from_yaml(path="benchmarks.yaml") -> dict[str, list[FlowTest]]:
    """
    Loads test suites from a YAML file. Each top-level key (like SDXL, PORTRAITS, etc.)
    maps to a list of flow definitions. Each flow definition must match the FlowTest model.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    test_suites = {}
    for suite_name, flows_data in data.items():
        # Convert each dictionary in flows_data to a FlowTest model
        flows_test = [FlowTest(**flow_dict) for flow_dict in flows_data]
        # Validate each suite
        validate_flows_test_cases(flows_test)
        test_suites[suite_name] = flows_test

    return test_suites


async def select_test_flow_suite(test_suites: dict[str, list[FlowTest]]):
    """
    Let the user pick which suites to run from the loaded YAML.
    Populates SELECTED_TEST_FLOW_SUITES with (suite_name, [FlowTest, FlowTest, ...]) items.
    """
    global SELECTED_TEST_FLOW_SUITES
    suite_names = list(test_suites.keys())

    print("Please select the test suites you want to run:")
    for idx, name in enumerate(suite_names, start=1):
        print(f"{idx}. {name} Suite")

    user_choice = input(
        "Enter the numbers of the suites to run, separated by commas (e.g., 1,3,5): "
    )

    selected_numbers = [num.strip() for num in user_choice.split(",")]
    SELECTED_TEST_FLOW_SUITES.clear()

    for num in selected_numbers:
        try:
            idx = int(num)
            if 1 <= idx <= len(suite_names):
                suite_key = suite_names[idx - 1]
                SELECTED_TEST_FLOW_SUITES.append((suite_key, test_suites[suite_key]))
                print(f"Selected {suite_key} Suite.")
            else:
                print(f"Invalid selection '{num}'. Skipping.")
        except ValueError:
            print(f"Invalid selection '{num}'. Skipping.")

    if not SELECTED_TEST_FLOW_SUITES:
        print(
            "No valid suites selected. Please restart and select at least one valid suite."
        )
        exit(1)


# ------------------------------------------
# Main entry point
# ------------------------------------------


async def benchmarker():
    # Check if the server is online
    if not await is_server_online():
        print("Cannot proceed as the server is down.")
        return

    await select_worker()

    # Load all test suites from the YAML file
    test_suites = load_test_suites_from_yaml("benchmarks.yaml")

    # Ask the user which suites to run
    await select_test_flow_suite(test_suites)

    # We'll run each selected suite
    for suite_name, suite_test_cases in SELECTED_TEST_FLOW_SUITES:
        global RESULTS_DIR, SELECTED_TEST_FLOW_SUITE
        SELECTED_TEST_FLOW_SUITE = suite_test_cases

        # Prepare the results directory for this suite
        RESULTS_DIR = Path("results").joinpath(
            f"{TEST_START_TIME.strftime('%Y-%m-%d')}-{HARDWARE}-{suite_name}"
        )

        print(f"\nRunning test suite: {suite_name}\n")

        # 1) Install all flows in parallel
        flows_to_install = list({flow_test.flow_name for flow_test in suite_test_cases})
        install_results = await install_flows_in_parallel(flows_to_install)
        # if any flow fails to install, skip them in the next step
        installed_ok = {flow_name for flow_name, ok in install_results.items() if ok}

        # 2) Once all are installed, proceed with tests (flows that installed successfully)
        test_semaphore = asyncio.Semaphore(
            1
        )  # Only 1 test at a time for consistent timing
        # Load or create results summary
        results_summary = {}

        for flow_test in suite_test_cases:
            # Skip flows that failed installation
            if flow_test.flow_name not in installed_ok:
                print(
                    f"Skipping flow '{flow_test.flow_name}' since installation failed."
                )
                continue

            # Initialize in summary
            if flow_test.flow_name not in results_summary:
                results_summary[flow_test.flow_name] = {}

            # Now run each test case
            for test_case in flow_test.test_cases:
                await run_test_case(
                    flow_test.flow_name,
                    test_case,
                    results_summary,
                    test_semaphore,
                    suite_name,
                )

        # Generate final summary JSON after all flow tests in this suite
        await generate_results_summary_json(results_summary, suite_name)


if __name__ == "__main__":
    asyncio.run(benchmarker())
