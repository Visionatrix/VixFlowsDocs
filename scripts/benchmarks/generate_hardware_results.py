import json
import os
import re
from pathlib import Path

os.chdir(Path(__file__).parent)
# Directory where the `summary-date-HARDWARE-SUITE.json` files are stored
HARDWARE_RESULTS_DIR = Path("../../hardware_results")
PATTERN = r"summary-\d{4}-\d{2}-\d{2}-(.*?)-(SDXL|PORTRAITS|OTHER|FLUX|HEAVY)\.json"


# Function to generate a Markdown table from multiple results_summary.json files
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
        table_md += "| Test Case  |  Avg Execution Time (s) | Hardware | Test Time | VRAM State | Smart Memory | GPU Memory |\n"
        table_md += "| ---------- | :---------------------: | -------- | --------- | :--------: | :----------: | ---------- |\n"

        for test_case in sorted_test_cases:
            table_md += (
                f"| {test_case['test_case']} | {test_case['avg_exec_time']} | "
                f"{test_case['hardware_desc']} | {test_case['test_time']} | {test_case['vram_state']} | {test_case['disable_smart_memory']} | "
                f"{test_case['avg_max_memory_usage_str']} |\n"
            )
        table_md += "\n"  # Add spacing between flow groups

    table_md = table_md[:-1] if table_md.endswith("\n\n") else table_md
    # Save the table to a Markdown file
    output_path = Path("../../docs/hardware_results.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(table_md)

    print(f"Hardware test results table generated at {output_path}")


if __name__ == "__main__":
    generate_hardware_results_table()
