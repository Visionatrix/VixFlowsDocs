---
title: Manual Installation
---

# Manual Installation

In most cases, we recommend using automatic installation via an
`easy-install` script.

For those who want to install everything manually, here you will find
step-by-step instructions on what the script does.

## Virtual Environment creation

First clone the repository with `git`:

    git clone https://github.com/Visionatrix/Visionatrix.git && cd Visionatrix

Setup the virtual environment with `python`:

    python -m venv venv

Activate Virtual Environment(**Linux/macOS**) with `source`:

    source venv/bin/activate

Activate Virtual Environment(**Windows**) with `powershell`:

    .\venv\Scripts\Activate.ps1

## PyTorch installation

!!! note

    **On macOS currently no action is needed**.

For AMD graphic cards on **Linux** install **ROCM** version of PyTorch using `pip`:

    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.1

------------------------------------------------------------------------

For AMD graphics cards on **Windows** install PyTorch with DirectML support using `pip`:

    pip install torch-directml

> **Python3.10** is the only currently supported version by **torch-directml**.

------------------------------------------------------------------------

For NVIDIA graphics cards on **Linux** install PyTorch with next `pip` command:

    pip install torch torchvision torchaudio

For NVIDIA graphics cards on **Windows** install PyTorch using `pip` specifying PyTorch and CUDA version:

    pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121

## Install Visionatrix

Install Visionatrix from the previously cloned sources using `pip`:

    pip install .

Run **Visionatrix** initialization command using `python`:

    python -m visionatrix install

## Run Visionatrix

Execute from the activated virtual environment **run** command using `python`:

    python -m visionatrix run --ui

## Manual Update

1.  Pull last changes from repository with `git`:

        git pull

2.  Execute **update** command from **activated** virtual environment with `python`:

        python -m visionatrix update