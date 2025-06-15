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

SERVER_URL = os.environ.get("SERVER_URL", "http://127.0.0.1:8288")
REMOVE_RESULTS_FROM_VISIONATRIX = int(os.environ.get("REMOVE_RESULTS", "1"))
DEFAULT_NUMBER_OF_TEST_CASE_RUNS = min(int(os.environ.get("COUNT", "2")), 3)
HARDWARE = os.environ.get("HARDWARE", "YOUR_CPU-YOUR_GPU").strip("\"'")
FLOW_INSTALL_TIMEOUT = int(os.environ.get("FLOW_INSTALL_TIMEOUT", "2400"))
TEST_START_TIME = datetime.now()
# TEST_START_TIME = datetime(year=2025, month=2, day=2)  # set custom datetime if needed to add results to old results
RESULTS_DIR: Path
SELECTED_WORKER: dict
AUTOMATIC_INSTALL = True  # do not ask before installing flows for test suites

USER_NAME, USER_PASSWORD = os.getenv("USER_NAME", "vadmin"), os.getenv(
    "USER_PASSWORD", "vadmin"
)
BASIC_AUTH = (
    httpx.BasicAuth(USER_NAME, USER_PASSWORD) if USER_NAME and USER_PASSWORD else None
)
if BASIC_AUTH:
    print(f"Using authentication for connect, user: '{USER_NAME}'")

SKIP_SM_DISABLED = int(os.environ.get("SKIP_SM_DISABLED", "0"))

HUGGINGFACE_TOKEN = ""
CIVITAI_TOKEN = ""

PAUSE_INTERVAL = int(os.environ.get("PAUSE_INTERVAL", "0"))
PAUSE_INTERVAL_AFTER_WARMUP = int(os.environ.get("PAUSE_INTERVAL_AFTER_WARMUP", "0"))
UNLOAD_MODELS_BEFORE_WARMUP = os.environ.get("UNLOAD_MODELS_BEFORE_WARMUP", "1")
EXECUTION_PROFILER = True

FIRST_TEST_FLAG = True
SELECTED_TEST_FLOW_SUITES: list[tuple[str, list["FlowTest"]]] = []
SELECTED_TEST_FLOW_SUITE = []
INSTALLED_FLOWS_CACHE = []

PARALLEL_INSTALLS = int(
    os.environ.get("PARALLEL_INSTALLS", "3")
)  # for slow internet(<300MB) set to "2"

GLOBAL_PROMPTS: dict[str, list[str]] = {}


class TestCase(BaseModel):
    name: str = Field(..., description="Name of the test case for this specific flow.")
    input_params: dict[str, typing.Any] = Field(
        {},
        description="Parameters for the flow. If a key has a list value, we handle it the same as prompt lists.",
    )
    input_files: dict[str, str | Path | list[str | Path]] = Field(
        {},
        description="Files to pass to the flow. Each key can be a single string or a list of strings.",
    )
    count: int = Field(
        DEFAULT_NUMBER_OF_TEST_CASE_RUNS,
        description="Number of task executions to perform (beyond warm-up).",
    )
    support_disable_smart_memory: int = Field(
        1,
        description=(
            "If set to 0, skip this test if the worker has disable_smart_memory=True. "
            "If missing or non-zero, run the test."
        ),
    )
    use_settings: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Temporary global settings to override for this test case. "
            "Each key is a global setting, each value is what to set. "
            "After the test finishes, old values are restored."
        ),
    )
    sleep_after: int = Field(
        0,
        description=(
            "If > 0, sleep this many seconds after finishing the test case (while holding the semaphore)."
        ),
    )


class FlowTest(BaseModel):
    flow_name: str = Field(..., description="Name of the flow that will be tested.")
    test_cases: list[TestCase] = Field(
        ...,
        description="List of test cases with different parameter sets for this flow.",
    )


def validate_flows_test_cases(flows_test_cases: list[FlowTest]):
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
            response.raise_for_status()
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
    elapsed_time = 0
    max_read_timeout_count = 20
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        while elapsed_time < timeout:
            try:
                response = await client.get(
                    f"{SERVER_URL}/vapi/flows/install-progress", timeout=15
                )
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
                    f"Flow '{flow_name}': ReadTimeout during installation progress check, "
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


async def create_task(
    flow_name: str,
    input_params: dict,
    count: int,
    input_files: dict | None,
    warm_up: bool,
) -> list[int]:
    files_to_upload = {}
    if input_files:
        for param_id, file_value in input_files.items():
            if isinstance(file_value, (str, Path)):
                file_path = os.path.join("input_files", str(file_value))
                try:
                    files_to_upload[param_id] = open(file_path, "rb")
                except FileNotFoundError:
                    print(f"File {file_value} not found in the input_files directory.")
                    return []
            else:
                # Should not happen here if we handle array logic externally
                print(f"Unexpected file list for key={param_id}: {file_value}")

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
    max_read_timeout_count = 20
    previous_progress = 0.0
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        while True:
            try:
                response = await client.get(
                    f"{SERVER_URL}/vapi/tasks/progress/{task_id}", timeout=15
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
                        rounded_flow_progress = math.floor(progress * 10) / 10
                        print(
                            f"Task `{task_data['name']}` with id={task_id}, progress: {rounded_flow_progress}%"
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


def split_value_for_warmup_and_runs(
    value: typing.Any, count: int, suite_prompts: list[str] | None = None
) -> tuple[typing.Any, list[typing.Any]]:
    """
    Given a value from either input_params or input_files, decide how to split it for warm-up
    vs. main runs. If it's a list, first item is warm-up, the rest are subsequent runs.
    If empty list, we might use suite_prompts logic (only for prompt?), but for input_files
    it should just be blank. If it's a single item, we use that for all runs.
    """
    if isinstance(value, list):
        if not value and suite_prompts is not None:
            # If 'prompt' key is empty, try top-level suite prompts
            if suite_prompts:
                warmup_val = suite_prompts[0] if len(suite_prompts) > 0 else ""
                subsequent_vals = suite_prompts[1 : count + 1]
                return warmup_val, subsequent_vals
            else:
                return "", ["" for _ in range(count)]
        else:
            warmup_val = value[0] if len(value) > 0 else ""
            subsequent_vals = value[1 : count + 1]
            return warmup_val, subsequent_vals
    else:
        # Single value => same for all runs
        return value, [value for _ in range(count)]


def build_warmup_and_runs_dict(
    params: dict[str, typing.Any],
    suite_identifier: str,
    count: int,
    is_input_files: bool,
) -> tuple[dict[str, typing.Any], list[dict[str, typing.Any]]]:
    """
    For each key in `params`, figure out the warm-up value and subsequent values.
    Return (warmup_dict, [dict_for_run0, dict_for_run1, ...]).
    If it's for 'prompt' in input_params and is an empty list => use top-level PROMPTS from GLOBAL_PROMPTS.
    """
    warmup_dict = {}
    runs_list = [dict() for _ in range(count)]

    for key, value in params.items():
        suite_prompts = None
        # If it's the special "prompt" key in input_params and we have an empty list => use top-level suite prompts
        if (
            not is_input_files
            and key == "prompt"
            and isinstance(value, list)
            and not value
        ):
            suite_prompts = GLOBAL_PROMPTS.get(suite_identifier, [])

        warmup_val, subsequent_vals = split_value_for_warmup_and_runs(
            value, count, suite_prompts
        )
        warmup_dict[key] = warmup_val

        for i in range(count):
            runs_list[i][key] = (
                subsequent_vals[i] if i < len(subsequent_vals) else warmup_val
            )

    return warmup_dict, runs_list


async def run_test_case(
    flow_name: str,
    test_case: TestCase,
    test_semaphore: asyncio.Semaphore,
    suite_identifier: str,
):
    # Acquire semaphore to ensure tests run one at a time
    async with test_semaphore:
        global FIRST_TEST_FLAG

        # -------------------------------------------------
        # 1) Use settings override (store old, set new)
        # -------------------------------------------------
        old_settings: dict[str, str] = {}
        if test_case.use_settings:
            print(
                f"Test case '{test_case.name}' has 'use_settings': {test_case.use_settings}"
            )
            for k, new_val in test_case.use_settings.items():
                old_val = await get_global_setting_value(k)
                old_settings[k] = old_val
                await set_global_setting_value(k, new_val)
                print(
                    f"Set global setting: {k} => {new_val} (old value was: {old_val})"
                )

        try:
            # -------------------------------------------------
            # (continue normal test flow)
            # -------------------------------------------------

            if FIRST_TEST_FLAG:
                FIRST_TEST_FLAG = False
            else:
                if PAUSE_INTERVAL and not test_case.sleep_after:
                    print(
                        f"Pausing for {PAUSE_INTERVAL} seconds before starting next test."
                    )
                    await asyncio.sleep(PAUSE_INTERVAL)

            flow_test_case_dir = os.path.join(
                RESULTS_DIR, f"{flow_name}__{test_case.name}"
            )
            metadata_file = os.path.join(flow_test_case_dir, "metadata.json")
            existing_configurations = set()
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    try:
                        metadata = json.load(f)
                        if "results" in metadata:
                            existing_configurations.update(metadata["results"].keys())
                    except json.JSONDecodeError:
                        pass

            worker_engine_details = SELECTED_WORKER["engine_details"]
            configuration_key = (
                f"{worker_engine_details['vram_state']}_disable_smart_memory_"
                f"{worker_engine_details['disable_smart_memory']}"
            )

            if configuration_key in existing_configurations:
                print(
                    f"Results for flow '{flow_name}', test case '{test_case.name}', "
                    f"configuration '{configuration_key}' already exist. Skipping."
                )
                return

            # Build warm-up vs subsequent runs for input_params
            warmup_params, run_params_list = build_warmup_and_runs_dict(
                test_case.input_params,
                suite_identifier,
                test_case.count,
                is_input_files=False,
            )

            # Build warm-up vs subsequent runs for input_files
            warmup_files, run_files_list = build_warmup_and_runs_dict(
                test_case.input_files,
                suite_identifier,
                test_case.count,
                is_input_files=True,
            )

            print(
                f"\n------\nRunning test '{test_case.name}' for flow '{flow_name}', config '{configuration_key}'\n"
            )

            # --- Warm-up ---
            print("Warming up task...")
            warmup_task_ids = await create_task(
                flow_name=flow_name,
                input_params=warmup_params,
                count=1,
                input_files=warmup_files,
                warm_up=True,
            )
            if not warmup_task_ids:
                print(
                    f"Failed to create warmup task for flow '{flow_name}', test case: {test_case.name}"
                )
                return

            wr = await get_task_progress(warmup_task_ids[0])
            if wr.get("error"):
                print(
                    f"Failed warmup task for flow '{flow_name}', test case: {test_case.name} with error: {wr['error']}"
                )
                return
            warmup_result = wr

            if PAUSE_INTERVAL_AFTER_WARMUP and not test_case.sleep_after:
                print(f"Pausing {PAUSE_INTERVAL_AFTER_WARMUP}s after warmup.")
                await asyncio.sleep(PAUSE_INTERVAL_AFTER_WARMUP)

            # --- Main runs ---
            all_test_runs_results = []
            for i in range(test_case.count):
                rp = run_params_list[i]
                rf = run_files_list[i]

                maybe_prompt = rp.get("prompt", "")
                if isinstance(maybe_prompt, str) and maybe_prompt.strip():
                    print(f"Creating main run #{i+1} with prompt='{maybe_prompt}'")
                else:
                    print(f"Creating main run #{i+1}")

                task_ids = await create_task(
                    flow_name=flow_name,
                    input_params=rp,
                    count=1,
                    input_files=rf,
                    warm_up=False,
                )
                if not task_ids:
                    print(
                        f"Failed to create test run task for flow '{flow_name}', test case: {test_case.name}"
                    )
                    continue

                r = await get_task_progress(task_ids[0])
                r["input_params"] = rp
                all_test_runs_results.append(r)

            await save_results(
                flow_name=flow_name,
                test_case_name=test_case.name,
                test_case=test_case,
                warmup_result=warmup_result,
                main_task_results=all_test_runs_results,
                vram_state=worker_engine_details["vram_state"],
                disable_smart_memory=worker_engine_details["disable_smart_memory"],
            )

        finally:
            # -------------------------------------------------
            # 2) Restore old global settings
            # -------------------------------------------------
            if old_settings:
                for k, old_val in old_settings.items():
                    # If old_val == "" then that setting did not exist; remove it
                    await set_global_setting_value(k, old_val)
                    print(f"Restored global setting: {k} => {old_val}")

            # -------------------------------------------------
            # 3) Optional sleep_after
            # -------------------------------------------------
            if test_case.sleep_after > 0:
                print(f"Sleeping for {test_case.sleep_after} seconds after test case.")
                await asyncio.sleep(test_case.sleep_after)


async def install_flows_in_parallel(flow_names: list[str]) -> dict[str, bool]:
    old_hf_token = ""
    old_civitai_token = ""
    if HUGGINGFACE_TOKEN:
        old_hf_token = await get_global_setting_value("huggingface_auth_token")
        await set_global_setting_value(
            "huggingface_auth_token", HUGGINGFACE_TOKEN, sensitive=True
        )
    if CIVITAI_TOKEN:
        old_civitai_token = await get_global_setting_value("civitai_auth_token")
        await set_global_setting_value(
            "civitai_auth_token", CIVITAI_TOKEN, sensitive=True
        )

    try:
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
    finally:
        if HUGGINGFACE_TOKEN:
            await set_global_setting_value(
                "huggingface_auth_token", old_hf_token, sensitive=True
            )
        if CIVITAI_TOKEN:
            await set_global_setting_value(
                "civitai_auth_token", old_civitai_token, sensitive=True
            )
    return results


def is_flow_fully_tested_for_config(
    flow_test: FlowTest, config_key: str, results_folder: Path
) -> bool:
    """
    Returns True if *all* test cases for the given flow_test
    have already been completed for the specified config_key.
    """
    for tc in flow_test.test_cases:
        test_case_dir = results_folder.joinpath(f"{flow_test.flow_name}__{tc.name}")
        metadata_file = test_case_dir.joinpath("metadata.json")

        if not metadata_file.exists():
            return False
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            flow_results = metadata.get("results", {})
            if config_key not in flow_results:
                return False
        except (json.JSONDecodeError, OSError):
            return False
    return True


async def save_results(
    flow_name: str,
    test_case_name: str,
    test_case: TestCase,
    warmup_result: dict | None,
    main_task_results: list[dict],
    vram_state: str,
    disable_smart_memory: typing.Union[bool, str],
):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    flow_test_case_dir = os.path.join(RESULTS_DIR, f"{flow_name}__{test_case_name}")
    os.makedirs(flow_test_case_dir, exist_ok=True)

    valid_main_tasks = [t for t in main_task_results if not t.get("error")]
    if not main_task_results or not valid_main_tasks:
        print(
            f"No valid tasks to summarize for flow '{flow_name}', test case '{test_case_name}'."
        )

    summary = {}
    execution_times = [
        task["execution_time"] for task in valid_main_tasks if "execution_time" in task
    ]
    if execution_times:
        summary = {
            "min_exec_time": min(execution_times),
            "max_exec_time": max(execution_times),
            "avg_exec_time": statistics.mean(execution_times),
        }

    metadata_file = os.path.join(flow_test_case_dir, "metadata.json")
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            metadata = {
                "flow_name": flow_name,
                "test_case": test_case.model_dump(),
                "results": {},
            }
    else:
        metadata = {
            "flow_name": flow_name,
            "test_case": test_case.model_dump(),
            "results": {},
        }

    configuration_key = f"{vram_state}_disable_smart_memory_{disable_smart_memory}"
    metadata["results"].setdefault(configuration_key, {})

    if warmup_result:
        metadata["results"][configuration_key]["warmup_task_results"] = [warmup_result]
        if not warmup_result.get("error"):
            for output in warmup_result.get("outputs", []):
                node_id = output.get("comfy_node_id")
                if node_id:
                    output_data = await get_task_results(
                        warmup_result["task_id"], node_id
                    )
                    if output_data:
                        warmup_file = os.path.join(
                            flow_test_case_dir,
                            f"warmup_task_{warmup_result['task_id']}_node_{node_id}_{configuration_key}{get_extension(output_data)}",
                        )

                        with open(warmup_file, "wb") as fw:
                            fw.write(output_data.content)
                        print(f"Warm-up result saved to: {warmup_file}")
            if REMOVE_RESULTS_FROM_VISIONATRIX:
                await delete_task(warmup_result["task_id"])

    metadata["results"][configuration_key]["summary"] = summary
    metadata["results"][configuration_key]["task_results"] = main_task_results

    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)

    print(
        f"Results saved to {flow_test_case_dir} for configuration '{configuration_key}'"
    )

    for task in main_task_results:
        if task.get("error"):
            continue
        task_id = task.get("task_id")
        if not task_id:
            continue
        for output in task.get("outputs", []):
            node_id = output.get("comfy_node_id")
            if node_id:
                output_data = await get_task_results(task_id, node_id)
                if output_data:
                    await save_output(
                        flow_test_case_dir,
                        task_id,
                        node_id,
                        output_data.content,
                        configuration_key=configuration_key,
                        file_extension=get_extension(output_data),
                    )
        if REMOVE_RESULTS_FROM_VISIONATRIX:
            await delete_task(task_id)


async def get_task_results(task_id: int, node_id: int) -> httpx.Response | None:
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.get(
                f"{SERVER_URL}/vapi/tasks/results",
                params={"task_id": task_id, "node_id": node_id},
                timeout=15,
            )
            if response.status_code == 200:
                return response
            print(
                f"Failed to get results for task {task_id}, node {node_id}. Status: {response.status_code}"
            )
        except httpx.RequestError as exc:
            print(
                f"An error occurred while fetching task results: {exc.request.url!r}: {exc}"
            )
        return None


async def save_output(
    flow_test_case_dir: str,
    task_id: int,
    node_id: int,
    output_data: bytes,
    configuration_key: str,
    file_extension: str = ".png",
):
    output_file = os.path.join(
        flow_test_case_dir,
        f"result__task_{task_id}_node_{node_id}_{configuration_key}{file_extension}",
    )
    with open(output_file, "wb") as f:
        f.write(output_data)
    print(
        f"Output saved for task {task_id}, node {node_id}, config '{configuration_key}' => {output_file}"
    )


async def delete_task(task_id: int) -> None:
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.delete(
                f"{SERVER_URL}/vapi/tasks/task", params={"task_id": task_id}
            )
            if response.status_code != 204:
                print(
                    f"Failed to delete task {task_id}. Status code: {response.status_code}"
                )
        except httpx.RequestError as exc:
            print(
                f"An error occurred while deleting task results: {exc.request.url!r}: {exc}"
            )


async def generate_results_summary_json(suite_identifier: str):
    summary_file = os.path.join(
        RESULTS_DIR,
        f"summary-{TEST_START_TIME.strftime('%Y-%m-%d')}-{HARDWARE}-{suite_identifier}.json",
    )

    old_summary_data = None
    if os.path.exists(summary_file):
        try:
            with open(summary_file, "r", encoding="utf-8") as f:
                old_summary_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            old_summary_data = None

    new_summary_data = {
        "test_time": TEST_START_TIME.strftime("%Y/%m/%d"),
        "flows": [],
    }

    flows_display_names = await get_flow_display_names()
    new_flows_map = {}

    for entry in os.scandir(RESULTS_DIR):
        if not entry.is_dir():
            continue
        if "__" not in entry.name:
            continue
        metadata_file = os.path.join(entry.path, "metadata.json")
        if not os.path.exists(metadata_file):
            continue

        with open(metadata_file, "r") as f:
            try:
                metadata = json.load(f)
            except json.JSONDecodeError:
                continue

        flow_name = metadata.get("flow_name")
        if not flow_name:
            continue

        flow_display = flows_display_names.get(flow_name, flow_name)
        flow_obj = new_flows_map.setdefault(
            flow_name,
            {
                "flow_name": flow_name,
                "flow_display_name": flow_display,
                "test_cases": [],
            },
        )

        results = metadata.get("results", {})
        test_case_name = metadata.get("test_case", {}).get("name", entry.name)
        for configuration_key, config_results in results.items():
            summary = config_results.get("summary", {})
            task_results = config_results.get("task_results", [])
            max_memory_usages = [
                details.get("max_memory_usage")
                for details in (
                    result.get("execution_details") for result in task_results
                )
                if details and details.get("max_memory_usage") is not None
            ]
            parts = configuration_key.split("_disable_smart_memory_")
            if len(parts) == 2:
                vram_state, disable_smart_memory_str = parts
                disable_smart_memory = disable_smart_memory_str == "True"
            else:
                vram_state = configuration_key
                disable_smart_memory = None

            flow_obj["test_cases"].append(
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

    if old_summary_data and "flows" in old_summary_data:
        for old_flow in old_summary_data["flows"]:
            old_flow_name = old_flow.get("flow_name")
            if old_flow_name and old_flow_name not in new_flows_map:
                new_flows_map[old_flow_name] = old_flow

    new_summary_data["flows"] = list(new_flows_map.values())

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(new_summary_data, f, indent=4)

    print(f"Final test results summary saved to {summary_file}")


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


def load_test_suites_from_yaml(path="benchmarks.yaml") -> dict[str, list[FlowTest]]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    global GLOBAL_PROMPTS
    GLOBAL_PROMPTS = data.pop("PROMPTS", {})

    test_suites = {}
    for suite_name, flows_data in data.items():
        flows_test = [FlowTest(**flow_dict) for flow_dict in flows_data]
        validate_flows_test_cases(flows_test)
        test_suites[suite_name] = flows_test

    return test_suites


async def select_test_flow_suite(test_suites: dict[str, list[FlowTest]]):
    global SELECTED_TEST_FLOW_SUITES
    suite_names = list(test_suites.keys())

    print("Please select the test suites you want to run:")
    for idx, name in enumerate(suite_names, start=1):
        print(f"{idx}. {name} Suite")

    user_choice = input(
        "Enter the numbers of the suites to run, separated by commas (e.g., 1,3,5 or ALL): "
    )

    if user_choice.lower() == "all":
        SELECTED_TEST_FLOW_SUITES = [(name, test_suites[name]) for name in suite_names]
        print("Selected all suites.")
        return

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


#
#  Helpers to get/set global settings
#
async def get_global_setting_value(key: str) -> str:
    """Retrieve the global setting's value or empty string if not found."""
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.get(
                f"{SERVER_URL}/vapi/settings/global", params={"key": key}, timeout=30
            )
            if response.status_code == 200:
                # The /settings/global endpoint returns just the string or empty string
                return response.text
            print(
                f"Warning: get_global_setting_value({key}) returned status {response.status_code}"
            )
        except httpx.RequestError as exc:
            print(f"Error retrieving global setting {key}: {exc}")
    return ""


async def set_global_setting_value(key: str, value: str, sensitive=False):
    """Creates or updates a global setting. If value == '', we remove the setting."""
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        payload = {
            "key": key,
            "value": value,
            "sensitive": sensitive,
        }
        try:
            response = await client.post(
                f"{SERVER_URL}/vapi/settings/global", json=payload, timeout=30
            )
            if response.status_code != 204:
                print(
                    f"Failed to set global setting {key} => {value}. "
                    f"status_code={response.status_code}, response={response.text}"
                )
        except httpx.RequestError as exc:
            print(f"Error setting global setting {key} => {value}: {exc}")


async def benchmarker():
    if not await is_server_online():
        print("Cannot proceed as the server is down.")
        return

    await select_worker()
    worker_id = SELECTED_WORKER["worker_id"]

    original_sm_value: bool | None = SELECTED_WORKER.get("smart_memory", None)

    test_suites = load_test_suites_from_yaml("benchmarks.yaml")
    await select_test_flow_suite(test_suites)

    all_flows_to_install = {
        ft.flow_name for _, suite in SELECTED_TEST_FLOW_SUITES for ft in suite
    }

    do_install = (
        True
        if AUTOMATIC_INSTALL
        else (
            input("Install flows for all selected test suites? [y/N]: ").strip().lower()
            == "y"
        )
    )
    if do_install:
        install_results = await install_flows_in_parallel(list(all_flows_to_install))
    else:
        installed = {f["name"] for f in await get_installed_flows()}
        install_results = {f: (f in installed) for f in all_flows_to_install}

    try:
        passes = (1, 2) if not SKIP_SM_DISABLED else (1,)
        for pass_idx in passes:
            if pass_idx == 1:
                if not await _set_worker_smart_memory(worker_id, True):
                    return
                SELECTED_WORKER["engine_details"]["disable_smart_memory"] = False
            else:
                if not await _set_worker_smart_memory(worker_id, False):
                    return
                SELECTED_WORKER["engine_details"]["disable_smart_memory"] = True

            await asyncio.sleep(5)  # brief pause

            globals()["FIRST_TEST_FLAG"] = True

            print(
                f"\n================  PASS {pass_idx}  "
                f"(smart_memory={SELECTED_WORKER.get('engine_details', {}).get('disable_smart_memory') is False})  "
                "================\n"
            )

            for suite_name, suite_test_cases in SELECTED_TEST_FLOW_SUITES:
                global RESULTS_DIR, SELECTED_TEST_FLOW_SUITE
                SELECTED_TEST_FLOW_SUITE = suite_test_cases
                RESULTS_DIR = Path("results").joinpath(
                    f"{TEST_START_TIME.strftime('%Y-%m-%d')}-{HARDWARE}-{suite_name}"
                )

                installed_ok = {
                    ft.flow_name
                    for ft in suite_test_cases
                    if install_results.get(ft.flow_name)
                }

                worker_engine_details = SELECTED_WORKER["engine_details"]
                config_key_for_worker = (
                    f"{worker_engine_details['vram_state']}_disable_smart_memory_"
                    f"{worker_engine_details['disable_smart_memory']}"
                )

                test_semaphore = asyncio.Semaphore(1)

                for flow_test in suite_test_cases:
                    if flow_test.flow_name not in installed_ok:
                        print(f"Skipping '{flow_test.flow_name}' (not installed).")
                        continue

                    if is_flow_fully_tested_for_config(
                        flow_test, config_key_for_worker, RESULTS_DIR
                    ):
                        print(
                            f"All test cases for '{flow_test.flow_name}' already done for this config – skipping."
                        )
                        continue

                    for tc in flow_test.test_cases:
                        if (
                            tc.support_disable_smart_memory == 0
                            and worker_engine_details["disable_smart_memory"]
                        ):
                            print(
                                f"Skipping '{tc.name}' (does not support disable_smart_memory)."
                            )
                            continue

                        await run_test_case(
                            flow_test.flow_name,
                            tc,
                            test_semaphore,
                            suite_name,
                        )

                await generate_results_summary_json(suite_name)

    finally:
        await _set_worker_smart_memory(worker_id, original_sm_value)
        print("\nSmart-memory restored to its original value – benchmark finished.\n")


def get_extension(res: httpx.Response):
    content_disposition = res.headers.get("content-disposition")
    if content_disposition:
        import re

        match = re.search(r'filename="?([^";]+)"?', content_disposition)
        if match:
            filename = match.group(1)
            if "." in filename:
                return f".{filename.rsplit('.', 1)[-1]}"
    return ".png"


async def _fetch_worker_details(worker_id: str) -> dict | None:
    """Return a single WorkerDetails record or None."""
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            r = await client.get(
                f"{SERVER_URL}/vapi/workers/info",
                params={"worker_id": worker_id},
                timeout=30,
            )
            r.raise_for_status()
            data = r.json()
            return data[0] if data else None
        except (httpx.RequestError, httpx.HTTPStatusError):
            return None


async def _set_worker_smart_memory(worker_id: str, enable: bool) -> bool:
    """Toggle Smart-Memory for the worker while keeping every other setting exactly as it was."""
    details = await _fetch_worker_details(worker_id)
    if not details:
        print(f"Cannot change smart_memory: worker '{worker_id}' not found.")
        return False

    payload = {
        "worker_id": worker_id,
        "tasks_to_give": None,
        "smart_memory": enable,
        "cache_type": details.get("cache_type"),
        "cache_size": details.get("cache_size"),
        "vae_cpu": details.get("vae_cpu"),
        "reserve_vram": details.get("reserve_vram"),
    }

    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            r = await client.post(
                f"{SERVER_URL}/vapi/workers/settings", json=payload, timeout=30
            )
            if r.status_code == 204:
                print(f"\nSmart_memory set to {enable} for '{worker_id}'.")
                return True
            print(f"Failed to set smart_memory → {r.status_code}: {r.text}")
        except httpx.RequestError as exc:
            print(f"Error setting smart_memory: {exc}")
    return False


if __name__ == "__main__":
    asyncio.run(benchmarker())
