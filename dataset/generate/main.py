import os
import json
import csv
from collections import defaultdict

# get script path
base_path = os.path.dirname(os.path.abspath(__file__))

# check if the directory "PropertyEval" exists. If not, create clone the repository.
if not os.path.exists(os.path.join(base_path, "PropertyEval")):
    os.system("git clone https://github.com/mrigankpawagi/PropertyEval", cwd=base_path)

# read the problems data
with open(os.path.join(base_path, "PropertyEval", "problems.json")) as f:
    problems = json.load(f)

# the final dataset
dataset = defaultdict(dict)

# load the function code for each item
for problem_id in problems:
    problem_key = problem_id.split("/")[1]
    function_code = problems[problem_id]["prompt"] + problems[problem_id]["canonical_solution"]
    dataset[problem_key]["function"] = function_code

# load limits
limits = dict()
with open(os.path.join(base_path, "PropertyEval", "limits", "limits.py")) as f:
    for line in f.readlines():
        line = line.strip()
        if not line: continue
        key, value = line.split(" = ")
        limits[key] = eval(value)

# load the hypothesis strategies from the tests directory
for problem_key in os.listdir(os.path.join(base_path, "PropertyEval", "tests")):
    if problem_key not in dataset: continue
    with open(os.path.join(base_path, "PropertyEval", "tests", problem_key, "strategy.py")) as f:
        strategy_code = f.read()

    # remove the line that imports limits
    strategy_code = strategy_code.replace("from limits.limits import *\n", "")

    # remove all comment lines before the first non-comment line
    lines = strategy_code.split("\n")
    for i, line in enumerate(lines):
        if not line.strip().startswith("#"):
            break
    strategy_code = "\n".join(lines[i:])

    # replace all the limits with the actual values
    for key in limits:
        strategy_code = strategy_code.replace(key, str(limits[key]))

    dataset[problem_key]["strategy"] = strategy_code

# dump the dataset into jsonl and csv files
with open(os.path.join(base_path, "..", "ghaistwriter.jsonl"), "w") as f:
    for item in dataset.values():
        f.write(json.dumps({
            "function": item["function"],
            "strategy": item["strategy"]
        }))
        f.write("\n")

with open(os.path.join(base_path, "..", "ghaistwriter.csv"), "w") as f:
    writer = csv.DictWriter(f, fieldnames=["function", "strategy"])
    writer.writeheader()
    for item in dataset.values():
        writer.writerow(item)
