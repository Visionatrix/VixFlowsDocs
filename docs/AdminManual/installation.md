---
title: Installation
---

# Installation

In most cases, we recommend using automatic installation via an
`easy-install` script.

Download and execute `easy_install.py` script:

!!! note

    It will clone this repository into the current folder and perform the installation.

    After installation you can always run `easy_install` from the "scripts" folder.

With **wget**:
```console
wget -O easy_install.py https://raw.githubusercontent.com/Visionatrix/Visionatrix/main/scripts/easy_install.py && python3 easy_install.py
```

or with **curl**:
```console
curl -o easy_install.py https://raw.githubusercontent.com/Visionatrix/Visionatrix/main/scripts/easy_install.py && python3 easy_install.py
```

## Manual Installation

For those who want to install everything manually, here you will find
step-by-step instructions on what the script does.

### Virtual Environment creation

First clone the repository with `git`:

    git clone https://github.com/Visionatrix/Visionatrix.git && cd Visionatrix

Setup the virtual environment with `python`:

    python -m venv venv

Activate Virtual Environment(**Linux/macOS**) with `source`:

    source venv/bin/activate

Activate Virtual Environment(**Windows**) with `powershell`:

    .\venv\Scripts\Activate.ps1

### PyTorch installation

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

### Install Visionatrix

Install Visionatrix from the previously cloned sources using `pip`:

    pip install .

Run **Visionatrix** initialization command using `python`:

    python -m visionatrix install

### Run Visionatrix

Execute from the activated virtual environment **run** command using `python`:

    python -m visionatrix run --ui

## Update process

### Recommended way

!!! note

    On Windows this method currently does not supported.

With the `easy_install.py` script:

    python3 scripts/easy_install.py

and select option **Update (2)**

### Manual Update

!!! note

    On Windows this method requires installed **git** and **Visual Studio Compilers**

1.  Pull last changes from repository with `git`:

        git pull

2.  Execute **update** command from **activated** virtual environment with `python`:

        python -m visionatrix update


### Update algorithm

Development versions are updated only to development versions, release
versions only to release ones.

!!! note

    If you are not a developer, you are better off using the release version, as they should be more stable.

The update scheme in
[easy_install.py](https://github.com/Visionatrix/Visionatrix/blob/main/scripts/easy_install.py)
is quite simple; everything is done with ordinary Git commands.

-   If the current version is a dev release or the current branch is
    `main` then:

    > 1.  Check out the `main` branch.
    > 2.  Pull the latest changes from the remote repository.

-   If the current version is a tagged release version:

    > 1.  Determine the latest tag for the current major version, and if
    >     a newer version tag is found, check out the latest version tag
    >     within the current major version.
    > 2.  If no newer version is found within the current major version,
    >     check for the next major version.
    > 3.  If a newer major version tag is found, prompt the user to
    >     update to this newer major version.

-   After checking out the appropriate version, executes a `pip install`
    command to update the Python packages.

-   Finally, executes the `python3 -m visionatrix update` command to ensure
    that any additional necessary updates are applied (ComfyUI, custom nodes, flows).
