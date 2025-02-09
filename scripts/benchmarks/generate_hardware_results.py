import json
import os
import re
from pathlib import Path

os.chdir(Path(__file__).parent)

HARDWARE_RESULTS_DIR = Path("../../hardware_results")

# Pattern now captures everything after "summary-YYYY-MM-DD-" up to the final ".json"
# Group 1: hardware_desc (e.g., "YOUR_CPU-YOUR_GPU")
# Group 2: suite_name (e.g., "SDXL", "CASCADE", etc.)
PATTERN = r"summary-\d{4}-\d{2}-\d{2}-(.*-.*)-(.*?)\.json"

OUTPUT_JSON_DIR = Path("../../docs/hardware_results/plotly_data")

# We want to prioritize these suites in the given order.
# Any suites not found in this list will appear at the end in alphabetical order.
SORTING_ORDER = [
    "SDXL",
    "AURA_FLOW",
    "CASCADE",
    "DIT_8_BIT",
    "DIT",
    "PORTRAITS",
    "UPSCALERS",
    "OTHER",
    "OLLAMA",
]


def generate_hardware_results_table():
    results_by_flow = {}
    flow_to_display_name = {}

    for root, _, files in os.walk(HARDWARE_RESULTS_DIR):
        for file in files:
            if file.endswith(".json"):
                match = re.search(PATTERN, file)
                if not match:
                    print("Found file with invalid naming (skipping):", file)
                    continue
                hardware_desc = match.group(1)
                file_path = os.path.join(root, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    results_data = json.load(f)
                    for flow in results_data["flows"]:
                        flow_name = flow["flow_name"]
                        flow_to_display_name[flow_name] = flow["flow_display_name"]

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

                            avg_exec_time = test_case.get("avg_exec_time")
                            if avg_exec_time is None:
                                avg_exec_time = 0.0

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
                                    "avg_exec_time": round(avg_exec_time, 1),
                                    "avg_max_memory_usage": avg_max_memory_usage,
                                    "avg_max_memory_usage_str": avg_max_memory_usage_str,
                                    "vram_state": test_case.get("vram_state", ""),
                                    "disable_smart_memory": smart_memory_str,
                                    "hardware_desc": hardware_desc,
                                    "test_time": results_data["test_time"],
                                }
                            )

    table_md = "# Hardware Test Results\n\n"

    for flow_name, test_cases in results_by_flow.items():
        sorted_test_cases = sorted(
            test_cases, key=lambda x: (x["test_case"], x["avg_exec_time"])
        )

        display_name = flow_to_display_name.get(flow_name, flow_name)
        table_md += f"## {display_name}\n\n"
        table_md += "|  Type | Execution<br>Time (s) | Hardware | Test Time | VRAM Mode<br>Smart Memory | GPU Memory |\n"
        table_md += "| :---: | :----------------: | -------- | --------- | :-----------------------: | :--------: |\n"

        for tc in sorted_test_cases:
            vram_state = str(tc["vram_state"]).removesuffix("_VRAM")
            table_md += (
                f"| {tc['test_case']} | {tc['avg_exec_time']} | "
                f"{tc['hardware_desc']} | {tc['test_time']} | {vram_state}<br>{tc['disable_smart_memory']} | "
                f"{tc['avg_max_memory_usage_str']} |\n"
            )
        table_md += "\n"

    if table_md.endswith("\n\n"):
        table_md = table_md[:-1]

    output_path = Path("../../docs/hardware_results_raw.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(table_md)

    print(f"Hardware test results table generated at {output_path}")


def generate_plotly_data():
    suite_data = {}
    suite_index = {}

    for root, _, files in os.walk(HARDWARE_RESULTS_DIR):
        for file in files:
            if file.endswith(".json"):
                match = re.search(PATTERN, file)
                if not match:
                    print("Invalid file naming (skipping):", file)
                    continue
                hardware_desc = match.group(1)
                suite_name = match.group(2)
                file_path = os.path.join(root, file)

                with open(file_path, "r") as f:
                    results_data = json.load(f)

                    if suite_name not in suite_data:
                        suite_data[suite_name] = {}
                        suite_index[suite_name] = set()

                    for flow in results_data["flows"]:
                        flow_name = flow["flow_name"]
                        flow_display_name = flow["flow_display_name"]

                        for test_case in flow["test_cases"]:
                            test_case_name = test_case["test_case"]
                            suite_index[suite_name].add(test_case_name)

                            data_for_case = suite_data[suite_name].setdefault(
                                test_case_name, []
                            )

                            data_for_case.append(
                                {
                                    "flow_name": flow_name,
                                    "flow_display_name": flow_display_name,
                                    "test_case": test_case_name,
                                    "avg_exec_time": test_case.get(
                                        "avg_exec_time", 0.0
                                    ),
                                    "hardware_desc": hardware_desc,
                                    "test_time": results_data["test_time"],
                                    "disable_smart_memory": test_case.get(
                                        "disable_smart_memory", ""
                                    ),
                                }
                            )

    OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in OUTPUT_JSON_DIR.glob("*"):
        if old_file.is_file():
            old_file.unlink()

    # Sort suites in the final index using SORTING_ORDER, with any unknown suites appended at the end (alphabetically)
    # Also store the test cases in alphabetical order.
    all_suites = list(suite_data.keys())
    known_suites = [s for s in SORTING_ORDER if s in all_suites]
    unknown_suites = [s for s in all_suites if s not in SORTING_ORDER]
    unknown_suites.sort()
    final_suite_order = known_suites + unknown_suites

    # Write out the data per suite->test_case
    for suite_name in final_suite_order:
        test_cases_dict = suite_data[suite_name]
        for test_case_name, data_array in test_cases_dict.items():
            output_path = OUTPUT_JSON_DIR / f"{suite_name}_{test_case_name}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data_array, f, indent=2)
            print(
                f"Plotly data for {suite_name} - {test_case_name} generated at {output_path}"
            )

    suite_index_output = {}
    for suite_name in final_suite_order:
        test_case_names = list(suite_index[suite_name])
        test_case_names.sort()
        suite_index_output[suite_name] = test_case_names

    index_output_path = OUTPUT_JSON_DIR / "plotly_data_index.json"
    with open(index_output_path, "w", encoding="utf-8") as f:
        json.dump(suite_index_output, f, indent=2)

    print(f"Plotly data index generated at {index_output_path}")


if __name__ == "__main__":
    generate_hardware_results_table()
    generate_plotly_data()
