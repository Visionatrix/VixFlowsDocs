import json
import os
import re
from pathlib import Path

os.chdir(Path(__file__).parent)
# Directory where the `summary-date-HARDWARE-SUITE.json` files are stored
HARDWARE_RESULTS_DIR = Path("../../hardware_results")
PATTERN = r"summary-\d{4}-\d{2}-\d{2}-(.*?)-(SDXL|PORTRAITS|OTHER|DIT|HEAVY)\.json"
OUTPUT_JSON_DIR = Path("../../docs/plotly_data")


def generate_hardware_results_table():
    results_by_flow = {}
    flow_to_display_name = {}

    # Read each results_summary.json file from the hardware_results folder
    for root, _, files in os.walk(HARDWARE_RESULTS_DIR):
        for file in files:
            if file.endswith(".json"):
                match = re.search(PATTERN, file)
                if not match:
                    print("found file with invalid naming:", file)
                    continue
                hardware_desc = match.group(1)
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    results_data = json.load(f)
                    for flow in results_data["flows"]:
                        flow_name = flow["flow_name"]
                        flow_to_display_name[flow_name] = flow["flow_display_name"]

                        # Initialize the flow in the results dictionary if not present
                        if flow_name not in results_by_flow:
                            results_by_flow[flow_name] = []

                        for test_case in flow["test_cases"]:
                            disable_smart_memory = test_case.get("disable_smart_memory")
                            if disable_smart_memory is True:
                                smart_memory_str = "No"
                            elif disable_smart_memory is False:
                                smart_memory_str = "Yes"
                            else:
                                smart_memory_str = ""

                            avg_max_memory_usage = test_case.get(
                                "avg_max_memory_usage", -1
                            )
                            if avg_max_memory_usage >= 0:
                                avg_max_memory_usage_str = (
                                    f"{int(avg_max_memory_usage)} MB"
                                )
                            else:
                                avg_max_memory_usage_str = ""

                            results_by_flow[flow_name].append(
                                {
                                    "test_case": test_case["test_case"],
                                    "avg_exec_time": round(
                                        test_case["avg_exec_time"], 1
                                    ),
                                    "avg_max_memory_usage": avg_max_memory_usage,
                                    "avg_max_memory_usage_str": avg_max_memory_usage_str,
                                    "vram_state": test_case.get("vram_state", ""),
                                    "disable_smart_memory": smart_memory_str,
                                    "hardware_desc": hardware_desc,
                                    "test_time": results_data["test_time"],
                                }
                            )

    # Generate a Markdown table
    table_md = "# Hardware Test Results\n\n"

    # Iterate over each flow, first sort by test_case, then by avg_exec_time
    for flow_name, test_cases in results_by_flow.items():
        # Sort test cases first by 'test_case' alphabetically, then by 'avg_exec_time'
        sorted_test_cases = sorted(
            test_cases, key=lambda x: (x["test_case"], x["avg_exec_time"])
        )

        table_md += f"## {flow_to_display_name[flow_name]}\n\n"
        table_md += "|  Type | Execution<br>Time (s) | Hardware | Test Time | VRAM Mode<br>Smart Memory | GPU Memory |\n"
        table_md += "| :---: | :----------------: | -------- | --------- | :-----------------------: | :--------: |\n"

        for test_case in sorted_test_cases:
            table_md += (
                f"| {test_case['test_case']} | {test_case['avg_exec_time']} | "
                f"{test_case['hardware_desc']} | {test_case['test_time']} | {str(test_case['vram_state']).removesuffix("_VRAM")}<br>{test_case['disable_smart_memory']} | "
                f"{test_case['avg_max_memory_usage_str']} |\n"
            )
        table_md += "\n"  # Add spacing between flow groups

    table_md = table_md[:-1] if table_md.endswith("\n\n") else table_md
    # Save the table to a Markdown file
    output_path = Path("../../docs/hardware_results_raw.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(table_md)

    print(f"Hardware test results table generated at {output_path}")


def generate_plotly_data():
    suite_data = {"SDXL": {}, "PORTRAITS": {}, "OTHER": {}, "HEAVY": {}, "DIT": {}}
    suite_index = {
        "SDXL": set(),
        "PORTRAITS": set(),
        "OTHER": set(),
        "DIT": set(),
        "HEAVY": set(),
    }

    for root, _, files in os.walk(HARDWARE_RESULTS_DIR):
        for file in files:
            if file.endswith(".json"):
                match = re.search(PATTERN, file)
                if not match:
                    print("Invalid file naming:", file)
                    continue
                hardware_desc = match.group(1)
                suite_name = match.group(2)
                file_path = os.path.join(root, file)

                with open(file_path, "r") as f:
                    results_data = json.load(f)
                    for flow in results_data["flows"]:
                        flow_name = flow["flow_name"]
                        flow_display_name = flow["flow_display_name"]

                        for test_case in flow["test_cases"]:
                            test_case_name = test_case["test_case"]

                            # Track the test cases for each suite
                            suite_index[suite_name].add(test_case_name)

                            # Initialize the test case dictionary
                            if test_case_name not in suite_data[suite_name]:
                                suite_data[suite_name][test_case_name] = []

                            suite_data[suite_name][test_case_name].append(
                                {
                                    "flow_name": flow_name,
                                    "flow_display_name": flow_display_name,
                                    "test_case": test_case_name,
                                    "avg_exec_time": test_case["avg_exec_time"],
                                    "hardware_desc": hardware_desc,
                                    "test_time": results_data["test_time"],
                                    "disable_smart_memory": test_case.get(
                                        "disable_smart_memory", False
                                    ),
                                }
                            )

    OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)
    for file in OUTPUT_JSON_DIR.glob("*"):
        if file.is_file():
            file.unlink()

    # Save each test suite's data to a separate JSON file for each test case
    for suite_name, test_cases in suite_data.items():
        for test_case_name, data in test_cases.items():
            output_path = OUTPUT_JSON_DIR / f"{suite_name}_{test_case_name}.json"
            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            print(
                f"Plotly data for {suite_name} - {test_case_name} generated at {output_path}"
            )

    # Save the index of available test cases for each suite
    index_output_path = OUTPUT_JSON_DIR / "plotly_data_index.json"
    suite_index = {key: list(value) for key, value in suite_index.items()}
    if "OTHER" in suite_index and suite_index["OTHER"]:
        suite_index["OTHER"] = sorted(suite_index["OTHER"], key=custom_sort_other)
    with open(index_output_path, "w") as f:
        json.dump(suite_index, f, indent=2)
    print(f"Plotly data index generated at {index_output_path}")


def custom_sort_other(test_case_name):
    predefined_order = ["one_pass", "two_pass", "three_pass"]
    if test_case_name in predefined_order:
        # Return index of predefined order with a negative priority to place them first
        return 0, predefined_order.index(test_case_name)
    # For other test cases, return them with a positive priority to sort alphabetically after predefined ones
    return 1, test_case_name.lower()


if __name__ == "__main__":
    generate_hardware_results_table()
    generate_plotly_data()
