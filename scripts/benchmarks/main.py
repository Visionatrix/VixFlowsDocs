from __future__ import annotations

import asyncio
import json
import os
import statistics
import typing
from datetime import datetime
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

SERVER_URL = os.environ.get("SERVER_URL", "http://127.0.0.1:8288")
REMOVE_RESULTS_FROM_VISIONATRIX = int(os.environ.get("REMOVE_RESULTS", "1"))
DEFAULT_NUMBER_OF_TEST_CASE_RUNS = int(os.environ.get("COUNT", "3"))
HARDWARE = os.environ.get("HARDWARE", "REPLACE").strip("\"'")
TEST_START_TIME = datetime.now()
RESULTS_DIR = Path("results").joinpath(
    f"{TEST_START_TIME.strftime('%Y_%m_%d-%H:%M:%S')}"
)
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
    input_files: list[str] = Field(
        [],
        description="List of file paths to pass to the flow during the task creation",
    )
    warm_up: bool = Field(
        True,
        description="If set to True, the warm-up run will be executed before test start.",
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
                name="4_steps",
                input_params={"prompt": "green apple", "steps_number": "4 steps"},
            ),
            TestCase(
                name="8_steps",
                input_params={"prompt": "green apple", "steps_number": "8 steps"},
            ),
        ],
    ),
    FlowTest(
        flow_name="juggernaut_lite",
        test_cases=[
            TestCase(name="default", input_params={"prompt": "green apple"}),
        ],
    ),
    FlowTest(
        flow_name="juggernaut_xl",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "green apple", "fast_run": False},
            ),
            TestCase(
                name="fast_run",
                input_params={"prompt": "green apple", "fast_run": True},
            ),
        ],
    ),
    FlowTest(
        flow_name="colorful_xl",
        test_cases=[
            TestCase(
                name="fast_run_30steps",
                input_params={
                    "prompt": "green apple",
                    "steps_count": 30,
                    "fast_run": True,
                },
            ),
            TestCase(
                name="fast_run_60steps",
                input_params={
                    "prompt": "green apple",
                    "steps_count": 60,
                    "fast_run": True,
                },
            ),
            TestCase(
                name="usual_run_30steps",
                input_params={
                    "prompt": "green apple",
                    "steps_count": 30,
                    "fast_run": False,
                },
            ),
            TestCase(
                name="usual_run_60steps",
                input_params={
                    "prompt": "green apple",
                    "steps_count": 60,
                    "fast_run": False,
                },
            ),
        ],
    ),
    FlowTest(
        flow_name="mobius_xl",
        test_cases=[
            TestCase(
                name="fast_run_30steps",
                input_params={"prompt": "green apple", "fast_run": True},
            ),
            TestCase(
                name="usual_run_30steps",
                input_params={"prompt": "green apple", "fast_run": False},
            ),
        ],
    ),
    FlowTest(
        flow_name="playground_2_5_aesthetic",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "green apple", "fast_run": False},
            ),
            TestCase(
                name="fast_run",
                input_params={"prompt": "green apple", "fast_run": True},
            ),
        ],
    ),
    FlowTest(
        flow_name="playground_2_5_prometheus",
        test_cases=[
            TestCase(
                name="25steps",
                input_params={"prompt": "green apple", "steps_count": 25},
            ),
            TestCase(
                name="50steps",
                input_params={"prompt": "green apple", "steps_count": 50},
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
        flow_name="hunyuan_dit",
        test_cases=[
            TestCase(
                name="20steps",
                input_params={"prompt": "green apple", "steps_count": 20},
            ),
            TestCase(
                name="40steps",
                input_params={"prompt": "green apple", "steps_count": 40},
            ),
        ],
    ),
    FlowTest(
        flow_name="vintage_portrait",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "hero portrait"},
                input_files=["man.png"],
            ),
        ],
    ),
    FlowTest(
        flow_name="sketch_portrait",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "hero portrait"},
                input_files=["man.png"],
            ),
        ],
    ),
    FlowTest(
        flow_name="comicu_portrait",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "hero portrait"},
                input_files=["man.png"],
            ),
        ],
    ),
    FlowTest(
        flow_name="ghibli_portrait",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "hero portrait"},
                input_files=["man.png"],
            ),
        ],
    ),
    FlowTest(
        flow_name="memoji_portrait",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "man, portrait, close up"},
                input_files=["man.png"],
            ),
        ],
    ),
    FlowTest(
        flow_name="photomaker_1",
        test_cases=[
            TestCase(
                name="default",
                input_params={"prompt": "portrait of a man"},
                input_files=["man.png"],
            ),
        ],
    ),
    FlowTest(
        flow_name="remove_background_birefnet",
        test_cases=[
            TestCase(
                name="1024x1024",
                input_files=["man.png"],
            ),
        ],
    ),
    FlowTest(
        flow_name="remove_background_bria",
        test_cases=[
            TestCase(
                name="1024x1024",
                input_files=["man.png"],
            ),
        ],
    ),
    FlowTest(
        flow_name="supir_upscaler",
        test_cases=[
            TestCase(
                name="1MPx1.5",
                input_params={"scale_factor": 1.5},
                input_files=["man.png"],
            ),
        ],
    ),
    FlowTest(
        flow_name="photo_stickers",
        test_cases=[
            TestCase(
                name="default",
                input_files=["man.png"],
            ),
        ],
    ),
]
TEST_CASES_FLUX = [
    FlowTest(
        flow_name="flux1_dev_8bit",
        test_cases=[
            TestCase(
                name="20steps",
                input_params={"prompt": "green apple", "steps_count": 20},
            ),
            TestCase(
                name="40steps",
                input_params={"prompt": "green apple", "steps_count": 40},
            ),
        ],
    ),
    FlowTest(
        flow_name="flux1_schnell_8bit",
        test_cases=[
            TestCase(name="default", input_params={"prompt": "green apple"}),
        ],
    ),
]
TEST_CASES_TOP_TIER = [
    FlowTest(
        flow_name="flux1_dev",
        test_cases=[
            TestCase(
                name="20steps",
                input_params={"prompt": "green apple", "steps_count": 20},
            ),
            TestCase(
                name="40steps",
                input_params={"prompt": "green apple", "steps_count": 40},
            ),
        ],
    ),
]
validate_flows_test_cases(
    TEST_CASES_SDXL + TEST_CASES_OTHER + TEST_CASES_FLUX + TEST_CASES_TOP_TIER
)


async def select_test_flow_suite():
    global SELECTED_TEST_FLOW_SUITE
    print("Please select the test suite you want to run:")
    print("1. SDXL Suite")
    print("2. FLUX Suite")
    print("3. OTHER Suite")
    print("4. TOP TIER(24GB+ VRAM) Suite")

    user_choice = input("Enter the number of the suite (1/2/3/4): ")

    if user_choice == "1":
        SELECTED_TEST_FLOW_SUITE = TEST_CASES_SDXL
        print("Selected SDXL Suite.")
    elif user_choice == "2":
        SELECTED_TEST_FLOW_SUITE = TEST_CASES_FLUX
        print("Selected FLUX Suite.")
    elif user_choice == "3":
        SELECTED_TEST_FLOW_SUITE = TEST_CASES_OTHER
        print("Selected OTHER Suite.")
    elif user_choice == "4":
        SELECTED_TEST_FLOW_SUITE = TEST_CASES_TOP_TIER
        print("Selected TOP TIER Suite.")
    else:
        print("Invalid selection. Please restart and select a valid suite.")
        exit(1)


async def is_server_online() -> bool:
    async with httpx.AsyncClient() as client:
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
    async with httpx.AsyncClient() as client:
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
    async with httpx.AsyncClient() as client:
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


async def check_and_install_flows():
    for flow_test in SELECTED_TEST_FLOW_SUITE:
        flow_name = flow_test.flow_name
        if not await is_flow_installed(flow_name):
            print(f"Flow '{flow_name}' is not installed. Installing now...")
            success = await install_flow(flow_name)
            if not success:
                print(f"Failed to install flow '{flow_name}'.")
                return False
        else:
            print(f"Flow '{flow_name}' is already installed.")
    return True


async def wait_for_installation_to_complete(
    flow_name: str, poll_interval: int = 5, timeout: int = 300
) -> bool:
    elapsed_time = 0
    async with httpx.AsyncClient() as client:
        while elapsed_time < timeout:
            try:
                response = await client.get(f"{SERVER_URL}/api/flows/install-progress")
                response.raise_for_status()
                install_progress = response.json()

                for flow in install_progress:
                    if flow["name"] == flow_name:
                        if flow["progress"] == 100:
                            if flow["error"]:
                                print(
                                    f"Error during installation of flow '{flow_name}': {flow['error']}"
                                )
                                return False
                            return True
                        print(
                            f"Flow '{flow_name}' installation progress: {flow['progress']}%"
                        )

                await asyncio.sleep(poll_interval)
                elapsed_time += poll_interval
            except httpx.RequestError as exc:
                print(
                    f"An error occurred while checking installation progress: {exc.request.url!r}: {exc}"
                )
                return False

    print(f"Installation of flow '{flow_name}' timed out.")
    return False


async def create_task(
    flow_name: str, input_params: dict, count: int, input_files: list[str] = None
) -> list[int]:
    files_to_upload = []
    if input_files:
        # Load files from the "input_files" directory
        for file_name in input_files:
            file_path = os.path.join("input_files", file_name)
            try:
                files_to_upload.append(("files", open(file_path, "rb")))
            except FileNotFoundError:
                print(f"File {file_name} not found in the input_files directory.")
                return []

    async with httpx.AsyncClient() as client:
        try:
            form_data = {
                "name": flow_name,
                "count": count,
                "input_params": json.dumps(input_params),
            }
            response = await client.put(
                f"{SERVER_URL}/api/tasks/create", data=form_data, files=files_to_upload
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
            for _, file in files_to_upload:
                file.close()

    return []


async def get_task_progress(task_id: int, poll_interval: int = 3) -> dict:
    max_read_timeout_count = 20
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(
                    f"{SERVER_URL}/api/tasks/progress/{task_id}"
                )
                if response.status_code == 200:
                    task_data = response.json()
                    if task_data.get("progress") == 100.0 or task_data.get("error"):
                        return task_data
                    print(f"Task {task_id} progress: {task_data.get('progress')}%")
                    max_read_timeout_count = 20
                await asyncio.sleep(poll_interval)
            except httpx.ReadTimeout:
                max_read_timeout_count -= 1
                print(
                    f"ReadTimeout error, continue({max_read_timeout_count} tries left)"
                )
                if not max_read_timeout_count:
                    return {"error": "read timeout error"}
            except httpx.RequestError as exc:
                print(
                    f"An error occurred while fetching task progress: {exc.request.url!r}: {exc}"
                )
                return {"error": "request_error"}


async def benchmarker():
    # Ask the user which suite to run
    await select_test_flow_suite()

    # Check if the server is online
    if not await is_server_online():
        print("Cannot proceed as the server is down.")
        return

    # Check and install flows if necessary
    if not await check_and_install_flows():
        print("Failed to prepare all flows for benchmarking.")
        return

    # Create a results dictionary to store the summary
    results_summary = {}

    # Run benchmarks for each flow and test case
    for flow_test in SELECTED_TEST_FLOW_SUITE:
        flow_name = flow_test.flow_name
        results_summary[flow_name] = []  # Initialize the flow in the results summary
        for test_case in flow_test.test_cases:
            input_params = test_case.input_params
            input_files = test_case.input_files
            warm_up = test_case.warm_up
            count = test_case.count + 1 if warm_up else test_case.count

            # Create tasks, passing input files if present
            task_ids = await create_task(flow_name, input_params, count, input_files)
            if not task_ids:
                print(
                    f"Failed to create tasks for flow '{flow_name}', test case: {test_case.name}"
                )
                continue

            # Wait for tasks to finish and save results
            task_results = []
            flow_comfy_saved = False
            for task_id in task_ids:
                result = await get_task_progress(task_id)
                task_results.append(result)

                if not flow_comfy_saved and "flow_comfy" in result:
                    await save_flow_comfy(
                        flow_name, test_case.name, result["flow_comfy"]
                    )
                    flow_comfy_saved = True

            if warm_up:
                task_results = task_results[1:]

            # Save results and capture summary
            summary = await save_results(
                flow_name, test_case.name, test_case, task_results
            )
            if summary:
                results_summary[flow_name].append(
                    {
                        "test_case": test_case.name,
                        "avg_exec_time": summary["avg_exec_time"],
                    }
                )

    # Generate the JSON results summary file
    await generate_results_summary_json(results_summary)


async def save_results(
    flow_name: str, test_case_name: str, test_case: TestCase, task_results: list
):
    # Ensure results directory exists
    os.makedirs(RESULTS_DIR, exist_ok=True)
    flow_test_case_dir = os.path.join(RESULTS_DIR, f"{flow_name}__{test_case_name}")
    os.makedirs(flow_test_case_dir, exist_ok=True)

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

    # Save metadata (task results) without flow_comfy
    metadata_file = os.path.join(flow_test_case_dir, "metadata.json")

    for task in task_results:
        task.pop("flow_comfy", None)  # We saved it in a separate file

    metadata = {
        "flow_name": flow_name,
        "test_case": test_case.model_dump_json(indent=4),
        "summary": summary,  # Add the summary before task_results
        "task_results": task_results,
    }

    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"Results saved to {flow_test_case_dir}")

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
                            flow_test_case_dir, task_id, node_id, output_data
                        )

            if REMOVE_RESULTS_FROM_VISIONATRIX:
                await delete_task(task_id)

    return summary


async def delete_task(task_id: int) -> None:
    async with httpx.AsyncClient() as client:
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


async def save_flow_comfy(flow_name: str, test_case_name: str, flow_comfy: dict):
    flow_test_case_dir = os.path.join(RESULTS_DIR, f"{flow_name}__{test_case_name}")
    os.makedirs(flow_test_case_dir, exist_ok=True)
    flow_comfy_file = os.path.join(flow_test_case_dir, "flow_comfy.json")
    with open(flow_comfy_file, "w") as f:
        json.dump(flow_comfy, f, indent=4)


async def get_task_results(task_id: int, node_id: int) -> bytes:
    async with httpx.AsyncClient() as client:
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
    file_extension: str = "png",
):
    # Create the output file path, appending file extension
    output_file = os.path.join(
        flow_test_case_dir, f"result__task_{task_id}_node_{node_id}.{file_extension}"
    )
    with open(output_file, "wb") as f:
        f.write(output_data)  # Write binary data to the file
    print(f"Output saved for task {task_id}, node {node_id} to {output_file}")


async def generate_results_summary_json(results_summary: dict):
    suite_identifier = ""
    if SELECTED_TEST_FLOW_SUITE == TEST_CASES_SDXL:
        suite_identifier = "SDXL"
    elif SELECTED_TEST_FLOW_SUITE == TEST_CASES_FLUX:
        suite_identifier = "FLUX"
    elif SELECTED_TEST_FLOW_SUITE == TEST_CASES_OTHER:
        suite_identifier = "OTHER"
    elif SELECTED_TEST_FLOW_SUITE == TEST_CASES_TOP_TIER:
        suite_identifier = "TOP TIER"

    summary_file = os.path.join(
        RESULTS_DIR,
        f"results_summary_{suite_identifier}-{HARDWARE}-{TEST_START_TIME.strftime('%Y-%m-%d')}.json",
    )
    results_data = {
        "test_time": TEST_START_TIME.strftime("%Y/%m/%d"),
        "flows": [],
    }
    flows_display_names = await get_flow_display_names()

    # Populate the flows with test results
    for flow_name, test_cases in results_summary.items():
        flow_data = {
            "flow_name": flow_name,
            "flow_display_name": flows_display_names.get(flow_name, flow_name),
            "test_cases": [],
        }
        for test_case in test_cases:
            flow_data["test_cases"].append(
                {
                    "test_case": test_case["test_case"],
                    "avg_exec_time": test_case["avg_exec_time"],
                    "hardware_desc": HARDWARE,
                }
            )
        results_data["flows"].append(flow_data)

    # Write the results to a JSON file
    with open(summary_file, "w") as f:
        json.dump(results_data, f, indent=4)

    print(f"Test results summary saved to {summary_file}")


if __name__ == "__main__":
    asyncio.run(benchmarker())
