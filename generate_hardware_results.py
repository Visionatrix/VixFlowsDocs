import os
import json

# Directory where the `results_summary_XXX.json` files are stored
HARDWARE_RESULTS_DIR = "hardware_results"


# Function to generate a Markdown table from multiple results_summary.json files
def generate_hardware_results_table():
    results_by_flow = {}
    flow_to_display_name = {}

    # Read each results_summary.json file from the hardware_results folder
    for root, _, files in os.walk(HARDWARE_RESULTS_DIR):
        for file in files:
            if file.endswith(".json"):
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
                            results_by_flow[flow_name].append({
                                "test_case": test_case["test_case"],
                                "avg_exec_time": round(test_case["avg_exec_time"], 1),
                                "hardware_desc": test_case["hardware_desc"],
                                "test_time": results_data["test_time"],  # Adding test_time from metadata
                            })

    # Generate a Markdown table
    table_md = "# Hardware Test Results\n\n"

    # Iterate over each flow, first sort by test_case, then by avg_exec_time
    for flow_name, test_cases in results_by_flow.items():
        # Sort test cases first by 'test_case' alphabetically, then by 'avg_exec_time'
        sorted_test_cases = sorted(test_cases, key=lambda x: (x["test_case"], x["avg_exec_time"]))

        table_md += f"## {flow_to_display_name[flow_name]}\n\n"
        table_md += "| Test Case  |  Avg Execution Time (s) | Hardware Description | Test Time |\n"
        table_md += "| ---------- | :---------------------: | -------------------- | --------- |\n"

        for test_case in sorted_test_cases:
            table_md += (
                f"| {test_case['test_case']} | {test_case['avg_exec_time']} | "
                f"{test_case['hardware_desc']} | {test_case['test_time']} |\n"
            )

        table_md += "\n"  # Add spacing between flow groups

    # Save the table to a Markdown file
    with open("docs/hardware_results.md", "w") as f:
        f.write(table_md)

    print("Hardware test results table generated at docs/hardware_results.md")


if __name__ == "__main__":
    generate_hardware_results_table()
