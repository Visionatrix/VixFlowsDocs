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
from pydantic import BaseModel, Field

os.chdir(Path(__file__).parent)

SERVER_URL = os.environ.get("SERVER_URL", "http://127.0.0.1:8288")
REMOVE_RESULTS_FROM_VISIONATRIX = int(os.environ.get("REMOVE_RESULTS", "1"))
DEFAULT_NUMBER_OF_TEST_CASE_RUNS = int(os.environ.get("COUNT", "1"))
HARDWARE = os.environ.get("HARDWARE", "9950X-7900XTX").strip("\"'")
FLOW_INSTALL_TIMEOUT = int(os.environ.get("FLOW_INSTALL_TIMEOUT", "1800"))
TEST_START_TIME = datetime.now()
RESULTS_DIR: Path
VRAM_STATE = os.environ.get("VRAM_STATE", "")  # override autodetect
DISABLE_SMART_MEMORY = os.environ.get("DISABLE_SMART_MEMORY", "")  # override autodetect

USER_NAME, USER_PASSWORD = os.getenv("USER_NAME", "admin"), os.getenv(
    "USER_PASSWORD", "admin"
)
BASIC_AUTH = (
    httpx.BasicAuth(USER_NAME, USER_PASSWORD) if USER_NAME and USER_PASSWORD else None
)
if BASIC_AUTH:
    print("Using authentication for connect")
PAUSE_INTERVAL = int(os.environ.get("PAUSE_INTERVAL", "0"))
PAUSE_INTERVAL_AFTER_WARMUP = int(os.environ.get("PAUSE_INTERVAL_AFTER_WARMUP", "15"))
UNLOAD_MODELS_BEFORE_WARMUP = os.environ.get("UNLOAD_MODELS_BEFORE_WARMUP", "1")
EXECUTION_PROFILER = True

FIRST_TEST_FLAG = True
SELECTED_TEST_FLOW_SUITE = []
INSTALLED_FLOWS_CACHE = []


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


def validate_flows_test_cases(flows_test_cases: list[FlowTest]):
    # Ensure flow_name is unique
    flow_names = set()
    for flow_test in flows_test_cases:
        if flow_test.flow_name in flow_names:
            raise ValueError(f"Duplicate flow_name found: {flow_test.flow_name}")
        flow_names.add(flow_test.flow_name)

        # Ensure test_names is unique within each FlowTest
        test_names = set()
        for test_case in flow_test.test_cases:
            if test_case.name in test_names:
                raise ValueError(
                    f"Duplicate test name '{test_case.name}' found in flow '{flow_test.flow_name}'"
                )
            test_names.add(test_case.name)


TEST_CASES_SDXL = [
    FlowTest(
        flow_name="sdxl_lighting",
        test_cases=[
            TestCase(
                name="lighting",
                input_params={"prompt": "green apple", "steps_number": "8 steps"},
            ),
        ],
    ),
    FlowTest(
        flow_name="juggernaut_lite",
        test_cases=[
            TestCase(name="lighting", input_params={"prompt": "green apple"}),
        ],
    ),
    FlowTest(
        flow_name="juggernaut_xl",
        test_cases=[
            TestCase(
                name="default",
                input_params={
                    "prompt": "green apple",
                    "fast_run": False,
                    "steps_count": 45,
                },
            ),
            TestCase(
                name="fast_run",
                input_params={
                    "prompt": "green apple",
                    "fast_run": True,
                    "steps_count": 45,
                },
            ),
        ],
    ),
    FlowTest(
        flow_name="colorful_xl",
        test_cases=[
            TestCase(
                name="fast_run",
                input_params={
                    "prompt": "green apple",
                    "fast_run": True,
                    "steps_count": 45,
                },
            ),
            TestCase(
                name="default",
                input_params={
                    "prompt": "green apple",
                    "fast_run": False,
                    "steps_count": 45,
                },
            ),
        ],
    ),
    FlowTest(
        flow_name="mobius_xl",
        test_cases=[
            TestCase(
                name="fast_run",
                input_params={
                    "prompt": "green apple",
                    "fast_run": True,
                    "steps_count": 45,
                },
            ),
            TestCase(
                name="default",
                input_params={
                    "prompt": "green apple",
                    "fast_run": False,
                    "steps_count": 45,
                },
            ),
        ],
    ),
    FlowTest(
        flow_name="playground_2_5_aesthetic",
        test_cases=[
            TestCase(
                name="default",
                input_params={
                    "prompt": "green apple",
                    "fast_run": False,
                    "steps_count": 45,
                },
            ),
            TestCase(
                name="fast_run",
                input_params={
                    "prompt": "green apple",
                    "fast_run": True,
                    "steps_count": 45,
                },
            ),
        ],
    ),
    FlowTest(
        flow_name="playground_2_5_prometheus",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "green apple", "steps_count": 45},
            ),
        ],
    ),
]
TEST_CASES_PORTRAITS = [
    FlowTest(
        flow_name="vintage_portrait",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "hero portrait"},
                input_files={"person_face": "man.png"},
            ),
        ],
    ),
    FlowTest(
        flow_name="sketch_portrait",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "hero portrait"},
                input_files={"person_face": "man.png"},
            ),
        ],
    ),
    FlowTest(
        flow_name="comicu_portrait",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "hero portrait"},
                input_files={"person_face": "man.png"},
            ),
        ],
    ),
    FlowTest(
        flow_name="ghibli_portrait",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "hero portrait"},
                input_files={"person_face": "man.png"},
            ),
        ],
    ),
    FlowTest(
        flow_name="memoji_portrait",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "man, portrait, close up"},
                input_files={"person_face": "man.png"},
            ),
        ],
    ),
    FlowTest(
        flow_name="photomaker_1",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "portrait of a man"},
                input_files={"person_face": "man.png"},
            ),
        ],
    ),
    FlowTest(
        flow_name="photo_stickers",
        test_cases=[
            TestCase(
                name="default",
                input_files={"person_face": "man.png"},
            ),
        ],
    ),
]
TEST_CASES_OTHER = [
    FlowTest(
        flow_name="stable_cascade",
        test_cases=[
            TestCase(
                name="one_pass",
                input_params={"prompt": "green apple", "pass_count": "One pass"},
            ),
            TestCase(
                name="two_pass",
                input_params={"prompt": "green apple", "pass_count": "Two pass"},
            ),
            TestCase(
                name="three_pass",
                input_params={"prompt": "green apple", "pass_count": "Three pass"},
            ),
        ],
    ),
    FlowTest(
        flow_name="remove_background_birefnet",
        test_cases=[
            TestCase(
                name="Remove Background",
                input_files={"input_image": "man.png"},
            ),
        ],
    ),
    FlowTest(
        flow_name="remove_background_bria",
        test_cases=[
            TestCase(
                name="Remove Background",
                input_files={"input_image": "man.png"},
            ),
        ],
    ),
    FlowTest(
        flow_name="supir_upscaler",
        test_cases=[
            TestCase(
                name="1.5x Scale",
                input_params={"scale_factor": 1.5},
                input_files={"image_to_upscale": "man.png"},
            ),
        ],
    ),
]
TEST_CASES_DIT = [
    FlowTest(
        flow_name="hunyuan_dit",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "green apple", "steps_count": 45},
            ),
        ],
    ),
    FlowTest(
        flow_name="flux1_dev_8bit",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "green apple", "steps_count": 45},
            ),
        ],
    ),
    FlowTest(
        flow_name="flux1_schnell_8bit",
        test_cases=[
            TestCase(name="lighting", input_params={"prompt": "green apple"}),
        ],
    ),
]
TEST_CASES_HEAVY = [
    FlowTest(
        flow_name="flux1_dev",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "green apple", "steps_count": 45},
            ),
        ],
    ),
]
validate_flows_test_cases(
    TEST_CASES_SDXL
    + TEST_CASES_PORTRAITS
    + TEST_CASES_OTHER
    + TEST_CASES_DIT
    + TEST_CASES_HEAVY
)


async def select_test_flow_suite():
    global SELECTED_TEST_FLOW_SUITE
    global RESULTS_DIR

    print("Please select the test suite you want to run:")
    print("1. SDXL Suite")
    print("2. PORTRAITS Suite")
    print("3. OTHER Suite")
    print("4. DiT(FLUX, ..) Suite")
    print("5. HEAVY(24GB+ VRAM) Suite")

    user_choice = input("Enter the number of the suite (1/2/3/4/5): ")

    if user_choice == "1":
        SELECTED_TEST_FLOW_SUITE = TEST_CASES_SDXL
        print("Selected SDXL Suite.")
    elif user_choice == "2":
        SELECTED_TEST_FLOW_SUITE = TEST_CASES_PORTRAITS
        print("Selected PORTRAITS Suite.")
    elif user_choice == "3":
        SELECTED_TEST_FLOW_SUITE = TEST_CASES_OTHER
        print("Selected OTHER Suite.")
    elif user_choice == "4":
        SELECTED_TEST_FLOW_SUITE = TEST_CASES_DIT
        print("Selected DIT Suite.")
    elif user_choice == "5":
        SELECTED_TEST_FLOW_SUITE = TEST_CASES_HEAVY
        print("Selected HEAVY Suite.")
    else:
        print("Invalid selection. Please restart and select a valid suite.")
        exit(1)

    # Set RESULTS_DIR based on the selected suite
    suite_identifier = get_suite_identifier()
    RESULTS_DIR = Path("results").joinpath(
        f"{TEST_START_TIME.strftime('%Y-%m-%d')}-{HARDWARE}-{suite_identifier}"
    )


async def is_server_online() -> bool:
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.get(f"{SERVER_URL}/api/flows/installed")
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
        response = await client.get(f"{SERVER_URL}/api/flows/installed")
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
                f"{SERVER_URL}/api/flows/flow", params={"name": flow_name}
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
                response = await client.get(f"{SERVER_URL}/api/flows/install-progress")
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


async def create_task(
    flow_name: str,
    input_params: dict,
    count: int,
    input_files: dict | None = None,
    warm_up=False,
) -> list[int]:
    files_to_upload = {}
    if input_files:
        # Load from the "input_files" directory
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
                f"{SERVER_URL}/api/tasks/create/{flow_name}",
                data=form_data,
                files=files_to_upload,
                headers={
                    "X-WORKER-EXECUTION-PROFILER": (
                        "0" if warm_up else str(int(EXECUTION_PROFILER))
                    ),
                    "X-WORKER-UNLOAD-MODELS": (
                        UNLOAD_MODELS_BEFORE_WARMUP if warm_up else "0"
                    ),
                },
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
            # Close file handlers
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
                    f"{SERVER_URL}/api/tasks/progress/{task_id}"
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
                    if progress > 0.0:
                        # Only print progress if it has increased
                        if progress != previous_progress:
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
):
    # Use the test_semaphore to limit concurrent tests
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

        # Check if results already exist for this test case
        flow_results = results_summary.setdefault(flow_name, {})
        test_case_results = flow_results.setdefault(test_case.name, set())

        # Load existing results for this test case
        flow_test_case_dir = os.path.join(RESULTS_DIR, f"{flow_name}__{test_case.name}")
        metadata_file = os.path.join(flow_test_case_dir, "metadata.json")
        existing_configurations = set()
        if os.path.exists(metadata_file):
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                existing_configurations.update(metadata["results"].keys())

        test_case_results.update(existing_configurations)

        if VRAM_STATE and DISABLE_SMART_MEMORY:
            configuration_key = (
                f"{VRAM_STATE}_disable_smart_memory_{bool(int(DISABLE_SMART_MEMORY))}"
            )
            # Check if results for this configuration already exist
            if configuration_key in test_case_results:
                print(
                    f"Results for flow '{flow_name}', test case '{test_case.name}', configuration '{configuration_key}' already exist. Skipping."
                )
                return

        print("Warming up...")
        warmup_task_id = await create_task(
            flow_name, input_params, 1, input_files, warm_up=True
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

        # Extract 'vram_state' and 'disable_smart_memory' from execution_details
        execution_details = r.get("execution_details")
        if execution_details:
            vram_state = (
                VRAM_STATE
                if VRAM_STATE
                else execution_details.get("vram_state", "unknown_vram_state")
            )
            disable_smart_memory = execution_details.get(
                "disable_smart_memory", "unknown"
            )
            disable_smart_memory = (
                DISABLE_SMART_MEMORY if DISABLE_SMART_MEMORY else disable_smart_memory
            )
        else:
            print(
                f"Execution details not found for flow '{flow_name}', test case '{test_case.name}'"
            )
            vram_state = "unknown_vram_state"
            disable_smart_memory = "unknown"

        configuration_key = f"{vram_state}_disable_smart_memory_{disable_smart_memory}"

        # Check if results for this configuration already exist
        if configuration_key in test_case_results:
            print(
                f"Results for flow '{flow_name}', test case '{test_case.name}', configuration '{configuration_key}' already exist. Skipping."
            )
            return
        else:
            test_case_results.add(configuration_key)

        # Proceed to run the actual test
        # Create tasks, passing input files if present
        task_ids = await create_task(
            flow_name, input_params, test_case.count, input_files, warm_up=False
        )
        if not task_ids:
            print(
                f"Failed to create tasks for flow '{flow_name}', test case: {test_case.name}"
            )
            return

        # Create a list of coroutines for task progress
        task_progress_coroutines = [get_task_progress(task_id) for task_id in task_ids]
        task_results = await asyncio.gather(*task_progress_coroutines)

        # Save results and capture summary
        summary = await save_results(
            flow_name,
            test_case.name,
            test_case,
            task_results,
            vram_state,
            disable_smart_memory,
        )
        if summary:
            # Save the updated results summary after each test case
            await generate_results_summary_json(results_summary)


async def process_flow(
    flow_test: FlowTest,
    results_summary: dict,
    installation_semaphore: asyncio.Semaphore,
    test_semaphore: asyncio.Semaphore,
):
    flow_name = flow_test.flow_name

    # Initialize the flow in the results summary if not already present
    if flow_name not in results_summary:
        results_summary[flow_name] = {}

    # Check if the flow is installed
    if not await is_flow_installed(flow_name):
        print(f"Flow '{flow_name}' is not installed. Installing now...")

        # Use semaphore to ensure only one installation at a time
        async with installation_semaphore:
            success = await install_flow(flow_name)
            if not success:
                print(f"Failed to install flow '{flow_name}'.")
                return
    else:
        print(f"Flow '{flow_name}' is already installed.")

    for test_case in flow_test.test_cases:
        await run_test_case(flow_name, test_case, results_summary, test_semaphore)


async def load_results_summary() -> dict:
    # Initialize empty results summary
    results_summary = {}

    # Load existing results for the selected test suite
    for flow_test in SELECTED_TEST_FLOW_SUITE:
        flow_name = flow_test.flow_name
        flow_results = results_summary.setdefault(flow_name, {})
        for test_case in flow_test.test_cases:
            test_case_name = test_case.name
            test_case_results = flow_results.setdefault(test_case_name, set())

            flow_test_case_dir = os.path.join(
                RESULTS_DIR, f"{flow_name}__{test_case_name}"
            )
            metadata_file = os.path.join(flow_test_case_dir, "metadata.json")

            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    existing_configurations = set(metadata["results"].keys())
                    test_case_results.update(existing_configurations)

    return results_summary


async def benchmarker():
    # Ask the user which suite to run
    await select_test_flow_suite()

    # Check if the server is online
    if not await is_server_online():
        print("Cannot proceed as the server is down.")
        return

    # Semaphores to control concurrency
    installation_semaphore = asyncio.Semaphore(1)  # Only 1 flow installation at a time
    test_semaphore = asyncio.Semaphore(1)  # Only 1 test runs at a time

    # Load existing results if available
    results_summary = await load_results_summary()

    flow_tasks = []

    for flow_test in SELECTED_TEST_FLOW_SUITE:
        flow_task = asyncio.create_task(
            process_flow(
                flow_test, results_summary, installation_semaphore, test_semaphore
            )
        )
        flow_tasks.append(flow_task)

    await asyncio.gather(*flow_tasks)

    # Generate results summary after all tests are done
    await generate_results_summary_json(results_summary)


async def save_results(
    flow_name: str,
    test_case_name: str,
    test_case: TestCase,
    task_results: list,
    vram_state: str,
    disable_smart_memory: typing.Union[bool, str],
):
    # Ensure results directory exists
    os.makedirs(RESULTS_DIR, exist_ok=True)
    flow_test_case_dir = os.path.join(RESULTS_DIR, f"{flow_name}__{test_case_name}")
    os.makedirs(flow_test_case_dir, exist_ok=True)

    failed_tasks = [task for task in task_results if task.get("error")]
    if failed_tasks:
        print(
            f"Some tasks failed for flow '{flow_name}', test case '{test_case_name}' with errors:"
        )
        for i in failed_tasks:
            print(i["error"])

    # Calculate summary statistics
    execution_times = [
        task["execution_time"] for task in task_results if "execution_time" in task
    ]
    if not execution_times:
        return None  # No valid execution times, skip saving

    summary = {
        "min_exec_time": min(execution_times),
        "max_exec_time": max(execution_times),
        "avg_exec_time": statistics.mean(execution_times),
    }

    # Load existing metadata if available
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

    # Remove 'flow_comfy' from task results
    for task in task_results:
        task.pop("flow_comfy", None)  # We saved it in a separate file

    # Update the results for the current configuration
    configuration_key = f"{vram_state}_disable_smart_memory_{disable_smart_memory}"
    metadata["results"][configuration_key] = {
        "summary": summary,
        "task_results": task_results,
    }

    # Save updated metadata
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

    # Save the flow_comfy from the first task that has it
    for result in task_results:
        if "flow_comfy" in result:
            await save_flow_comfy(
                flow_name, test_case_name, result["flow_comfy"], configuration_key
            )
            break  # No need to check further once saved

    return summary


async def delete_task(task_id: int) -> None:
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.delete(
                f"{SERVER_URL}/api/tasks/task", params={"task_id": task_id}
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


async def get_task_results(task_id: int, node_id: int) -> bytes:
    async with httpx.AsyncClient(auth=BASIC_AUTH) as client:
        try:
            response = await client.get(
                f"{SERVER_URL}/api/tasks/results",
                params={"task_id": task_id, "node_id": node_id},
            )
            if response.status_code == 200:
                return response.content  # File content as bytes
            print(
                f"Failed to get results for task {task_id}, node {node_id}. Status code: {response.status_code}"
            )
        except httpx.RequestError as exc:
            print(
                f"An error occurred while fetching task results: {exc.request.url!r}: {exc}"
            )
        return b""  # Return empty bytes if there is an error


async def save_output(
    flow_test_case_dir: str,
    task_id: int,
    node_id: int,
    output_data: bytes,
    configuration_key: str,
    file_extension: str = "png",
):
    # Create the output file path, appending file extension
    output_file = os.path.join(
        flow_test_case_dir,
        f"result__task_{task_id}_node_{node_id}_{configuration_key}.{file_extension}",
    )
    with open(output_file, "wb") as f:
        f.write(output_data)  # Write binary data to the file
    print(
        f"Output saved for task {task_id}, node {node_id}, configuration '{configuration_key}' to {output_file}"
    )


def get_suite_identifier() -> str:
    if SELECTED_TEST_FLOW_SUITE == TEST_CASES_SDXL:
        return "SDXL"
    elif SELECTED_TEST_FLOW_SUITE == TEST_CASES_PORTRAITS:
        return "PORTRAITS"
    elif SELECTED_TEST_FLOW_SUITE == TEST_CASES_OTHER:
        return "OTHER"
    elif SELECTED_TEST_FLOW_SUITE == TEST_CASES_DIT:
        return "DIT"
    elif SELECTED_TEST_FLOW_SUITE == TEST_CASES_HEAVY:
        return "HEAVY"
    else:
        raise RuntimeError("Unknown TEST SUITE")


async def generate_results_summary_json(results_summary: dict):
    suite_identifier = get_suite_identifier()

    summary_file = os.path.join(
        RESULTS_DIR,
        f"summary-{TEST_START_TIME.strftime('%Y-%m-%d')}-{HARDWARE}-{suite_identifier}.json",
    )

    results_data = {
        "test_time": TEST_START_TIME.strftime("%Y/%m/%d"),
        "flows": [],
    }

    flows_display_names = await get_flow_display_names()

    # Use results from the current run (results_summary)
    for flow_name in results_summary.keys():
        flow_data = {
            "flow_name": flow_name,
            "flow_display_name": flows_display_names.get(flow_name, flow_name),
            "test_cases": [],
        }

        # Read test case results from the corresponding directories
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
                        # Parse configuration_key
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

    # Write the results to a JSON file
    with open(summary_file, "w") as f:
        json.dump(results_data, f, indent=4)

    print(f"Test results summary saved to {summary_file}")


if __name__ == "__main__":
    asyncio.run(benchmarker())
