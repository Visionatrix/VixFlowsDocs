import builtins
import contextlib
import json
import re
import sys
from pathlib import Path
from time import sleep

import requests
from huggingface_hub import HfApi

ERRORS_LIST = []


def parse_huggingface_url(url: str):
    parts = url.split("/")
    repo_id = "/".join(parts[3:5])
    revision = parts[6:7][0]
    filename = "/".join(parts[7:])
    return repo_id, filename, revision


def __get_huggingface_model_hash(model_url: str) -> str | None:
    with contextlib.suppress(Exception):
        repo_id, filename, revision = parse_huggingface_url(model_url)
        repo_info = HfApi().model_info(repo_id, revision=revision, files_metadata=True)
        for file in repo_info.siblings:
            if file.rfilename == filename:
                return file.lfs.sha256
    return None


def get_huggingface_model_hash(model_url: str) -> str | None:
    for _ in range(5):
        r = __get_huggingface_model_hash(model_url)
        if r is not None:
            return r
        sleep(1)
    return None


def get_civitai_model_hash(model_url: str) -> str | None:
    m = re.search(r"api/download/models/(\d+)", model_url)
    if not m:
        return None
    model_id = m.group(1)
    response = requests.get(f"https://civitai.com/api/v1/model-versions/{model_id}")
    if response.status_code != 200:
        return None
    model_info = json.loads(response.text)
    for i in model_info["files"]:
        if model_url.startswith(i["downloadUrl"]):
            return i["hashes"]["SHA256"]
    return None


def check_model(model_name: str, model: dict) -> bool:
    url = model["url"]
    if "huggingface.co" in url:
        model_hash = get_huggingface_model_hash(url)
    elif "civitai.com" in url:
        model_hash = get_civitai_model_hash(url)
    else:
        ERRORS_LIST.append(f"{model_name}: FAILED. Unknown host for URL: {url}")
        return False

    if not model_hash:
        ERRORS_LIST.append(f"{model_name}: FAILED. {url} --> can't get the hash")
        return False
    if model_hash == model["hash"]:
        print(f"{model_name}: OK.")
        return True
    ERRORS_LIST.append(
        f"{model_name}: FAILED. {url} --> the expected hash({model['hash']}) does not match({model_hash})"
    )
    return False


if __name__ == "__main__":
    with builtins.open(
        Path(__file__).parent.parent.parent.joinpath("models_catalog.json"), "r"
    ) as f:
        models = json.load(f)
        for name, info in models.items():
            check_model(name, info)
    print()
    print(f"ERRORS: {len(ERRORS_LIST)}")
    for i in ERRORS_LIST:
        print(i)
    sys.exit(0 if not ERRORS_LIST else 2)
