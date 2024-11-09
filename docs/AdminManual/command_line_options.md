---
title: Command Line Options
---

# Command Line Options

Visionatrix supports various command-line options, including most of the options provided by `ComfyUI`. You can specify these options when starting Visionatrix manually.

For example:

```shell
python3 -m visionatrix --verbose=WARNING run --ui --disable-smart-memory
```

Below are the command-line options related to Visionatrix and ComfyUI.

## Common Options for Multiple Commands

The following options can be specified for the `install`, `update`, `install-flow`, `orphan-models`, and `openapi` commands:

- `--backend_dir=BACKEND_DIR`: Directory for the folder with ComfyUI. Default: `vix_backend`
- `--flows_dir=FLOWS_DIR`: Directory for the flows. Default: `vix_flows`
- `--models_dir=MODELS_DIR`: Directory for the models. Default: `vix_models`

## The `run` Command

Starts the ComfyUI and Visionatrix backends.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] run [options]
```

### Options

#### Visionatrix-Specific Options

- `--host=HOST`: Host to listen on (DEFAULT or SERVER mode).

    !!! info

        This corresponds to ComfyUI's `--listen` argument.

- `--port=PORT`: Port to listen on (DEFAULT or SERVER mode).
- `--server=SERVER_ADDRESS`: Address of Vix Server (WORKER mode).
- `--mode {DEFAULT,WORKER,SERVER}`: Visionatrix operating mode.

    Choices: [DEFAULT](WorkingModes/working_modes.md#default), [WORKER](WorkingModes/working_modes.md#worker), [SERVER](WorkingModes/working_modes.md#server)

- `--ui [UI_DIR]`: Enable WebUI (DEFAULT or SERVER mode).
    - If `--ui` is provided **without** a value, the default UI is enabled.
    - If `--ui` is provided **with** a directory, it specifies the UI directory.
- `--tasks_files_dir=FILES_DIR`: Directory for input/output files. Default: `vix_task_files`
- `--disable-device-detection`: Disable automatic device detection.
- `--verbose [LEVEL]`: Set the logging level.

    Choices: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.

    Default: `INFO` or the value of the `LOG_LEVEL` environment variable.

    !!! note

        **Note:** The `--verbose` option should be specified **before** any command (e.g., `run`, `install`, `update`).

- `--backend_dir=BACKEND_DIR`: Directory for the folder with ComfyUI. Default: `vix_backend`
- `--flows_dir=FLOWS_DIR`: Directory for the flows. Default: `vix_flows`
- `--models_dir=MODELS_DIR`: Directory for the models. Default: `vix_models`

#### ComfyUI Options

Visionatrix supports most of ComfyUI's command-line options for the `run` command. You can pass ComfyUI options when starting Visionatrix, and they will be forwarded to ComfyUI.

**Note:** The following ComfyUI options are **not supported** in Visionatrix:

- `--tls-keyfile`
- `--tls-certfile`
- `--enable-cors-header`
- `--verbose` (Visionatrix uses its own `--verbose` option)
- `--dont-print-server`
- `--quick-test-for-ci`
- `--windows-standalone-build`
- `--auto-launch`
- `--disable-auto-launch`
- `--multi-user` (Visionatrix always supports multiple users)

All other ComfyUI options can be used. Below is a list of supported ComfyUI options:

##### Device and Performance Options

- `--cuda-device DEVICE_ID`: Set the ID of the CUDA device this instance will use.
- `--cuda-malloc`: Enable cudaMallocAsync (enabled by default for PyTorch 2.0 and up).
- `--disable-cuda-malloc`: Disable cudaMallocAsync.
- `--force-fp32`: Force fp32 precision (If this makes your GPU work better, please report it).
- `--force-fp16`: Force fp16 precision.

##### UNET Precision Options

- `--bf16-unet`: Run the UNET in bf16 precision. This should only be used for testing purposes.
- `--fp16-unet`: Store UNET weights in fp16 precision.
- `--fp8_e4m3fn-unet`: Store UNET weights in fp8_e4m3fn format.
- `--fp8_e5m2-unet`: Store UNET weights in fp8_e5m2 format.

##### VAE Precision Options

- `--fp16-vae`: Run the VAE in fp16 precision (might cause black images).
- `--fp32-vae`: Run the VAE in full precision fp32.
- `--bf16-vae`: Run the VAE in bf16 precision.
- `--cpu-vae`: Run the VAE on the CPU.

##### Text Encoder Precision Options

- `--fp8_e4m3fn-text-enc`: Store text encoder weights in fp8 (e4m3fn variant).
- `--fp8_e5m2-text-enc`: Store text encoder weights in fp8 (e5m2 variant).
- `--fp16-text-enc`: Store text encoder weights in fp16.
- `--fp32-text-enc`: Store text encoder weights in fp32.

##### Other Performance Options

- `--force-channels-last`: Force channels-last format when inferring the models.
- `--disable-ipex-optimize`: Disable `ipex.optimize` when loading models with Intel GPUs.

##### Caching Options

- `--cache-classic`: Use the old style (aggressive) caching.
- `--cache-lru N`: Use LRU caching with a maximum of N node results cached. May use more RAM/VRAM.

##### Attention Optimization Options

- `--use-split-cross-attention`: Use the split cross-attention optimization. Ignored when xformers is used.
- `--use-quad-cross-attention`: Use the sub-quadratic cross-attention optimization. Ignored when xformers is used.
- `--use-pytorch-cross-attention`: Use the new PyTorch 2.0 cross-attention function.
- `--disable-xformers`: Disable xformers.
- `--force-upcast-attention`: Force enable attention upcasting (please report if it fixes black images).
- `--dont-upcast-attention`: Disable all upcasting of attention. Should be unnecessary except for debugging.

##### Memory and Device Options

- `--gpu-only`: Store and run everything (text encoders/CLIP models, etc.) on the GPU.
- `--highvram`: Keep models in GPU memory instead of unloading to CPU memory after use.
- `--normalvram`: Force normal VRAM usage if low VRAM gets automatically enabled.
- `--lowvram`: Split the UNET into parts to use less VRAM.
- `--novram`: Use when `--lowvram` isn't enough.
- `--cpu`: Use the CPU for everything (slow).
- `--reserve-vram VRAM_GB`: Set the amount of VRAM in GB you want to reserve for use by your OS/other software.
- `--disable-smart-memory`: Force ComfyUI to aggressively offload to regular RAM instead of keeping models in VRAM when it can.

##### Other Options

- `--fast`: Enable some untested and potentially quality-deteriorating optimizations.

### Examples

#### Running Visionatrix with Specific GPU Settings

To run Visionatrix using the first CUDA device and enable split cross-attention optimization:

```shell
python3 -m visionatrix run --cuda-device 0 --use-split-cross-attention
```

#### Running in WORKER Mode

To run Visionatrix in WORKER mode, connecting to a Vix Server:

```shell
python3 -m visionatrix run --mode WORKER --server http://your_vix_server_address
```

#### Enabling the Web UI

To start Visionatrix with the default Web UI:

```shell
python3 -m visionatrix run --ui
```

To specify a custom UI directory:

```shell
python3 -m visionatrix run --ui /path/to/your/ui_directory
```

## The `install` Command

Performs cleanup and initialization.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] install [options]
```

### Options

- `--backend_dir=BACKEND_DIR`: Directory for the folder with ComfyUI. Default: `vix_backend`
- `--flows_dir=FLOWS_DIR`: Directory for the flows. Default: `vix_flows`
- `--models_dir=MODELS_DIR`: Directory for the models. Default: `vix_models`

### Example

```shell
python3 -m visionatrix install
```

During installation, you will be prompted to confirm whether to clear models, flows, and backend folders.

## The `update` Command

Performs an update to the latest version.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] update [options]
```

### Options

- `--backend_dir=BACKEND_DIR`: Directory for the folder with ComfyUI. Default: `vix_backend`
- `--flows_dir=FLOWS_DIR`: Directory for the flows. Default: `vix_flows`
- `--models_dir=MODELS_DIR`: Directory for the models. Default: `vix_models`

### Example

```shell
python3 -m visionatrix update
```

## The `install-flow` Command

Installs a flow by name, tag, or from a file. Useful for workers that do not have a user interface.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] install-flow [options]
```

### Options

You must specify one of the following options:

- `--file=FILE_PATH`: Path to `comfyui_flow.json` file or a directory containing flow files.
  - The file should contain a ComfyUI workflow with the [metadata](../FlowsDeveloping/vix_workflows.md#vix-workflow-overview) needed for Visionatrix.
- `--name=FLOW_NAME`: Flow name mask of the flow(s).
  - This will install the flow by its `ID`, which is equal to its folder name [here](https://github.com/Visionatrix/VixFlows/tree/main/flows).
- `--tag=TAG`: Flow tags mask of the flow(s).

Additional options:

- `--backend_dir=BACKEND_DIR`: Directory for the folder with ComfyUI. Default: `vix_backend`
- `--flows_dir=FLOWS_DIR`: Directory for the flows. Default: `vix_flows`
- `--models_dir=MODELS_DIR`: Directory for the models. Default: `vix_models`

### Examples

#### Installing from a File

```shell
python3 -m visionatrix install-flow --file=path_to_comfyui_flow.json
```

The file should contain a ComfyUI workflow with the [metadata](../FlowsDeveloping/vix_workflows.md#vix-workflow-overview) needed for Visionatrix.

#### Installing by Name

```shell
python3 -m visionatrix install-flow --name=photo_stickers
```

This will install the flow by its `ID`, which is equal to its folder name [here](https://github.com/Visionatrix/VixFlows/tree/main/flows).

#### Installing by Tag

```shell
python3 -m visionatrix install-flow --tag=your_tag
```

## The `create-user` Command

Creates a new user.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] create-user [options]
```

### Options

- `--name=USERNAME` (required): User name (ID).
- `--password=PASSWORD` (required): User password.
- `--full_name=FULL_NAME`: Full user name. Default: `John Doe`.
- `--email=EMAIL`: User's email address. Default: `user@example.com`.
- `--admin=BOOLEAN`: Should the user be an admin. Default: `True`.
- `--disabled=BOOLEAN`: Should the account be disabled. Default: `False`.

### Example

```shell
python3 -m visionatrix create-user --name=username --password=userpassword --email=user@example.com
```

## The `orphan-models` Command

Removes orphan models.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] orphan-models [options]
```

### Options

- `--no-confirm`: Do not ask for confirmation for each model.
- `--dry-run`: Perform cleaning without actually removing models.
- `--include-useful-models`: Include orphaned models that can be used in future flows for removal.
- `--backend_dir=BACKEND_DIR`: Directory for the folder with ComfyUI. Default: `vix_backend`
- `--flows_dir=FLOWS_DIR`: Directory for the flows. Default: `vix_flows`
- `--models_dir=MODELS_DIR`: Directory for the models. Default: `vix_models`

### Example

```shell
python3 -m visionatrix orphan-models --no-confirm --dry-run
```

## The `openapi` Command

Generates OpenAPI specifications.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] openapi [options]
```

### Options

- `--file=FILENAME`: Filename to save. Default: `openapi.json`.
- `--available`: Include specs for 'available' flows.
- `--installed`: Include specs for 'installed' flows.
- `--indentation=SIZE`: Indentation size. Default: `2`.
- `--only-flows`: Only include specs for flows.
- `--backend_dir=BACKEND_DIR`: Directory for the folder with ComfyUI. Default: `vix_backend`
- `--flows_dir=FLOWS_DIR`: Directory for the flows. Default: `vix_flows`
- `--models_dir=MODELS_DIR`: Directory for the models. Default: `vix_models`

### Example

```shell
python3 -m visionatrix openapi --available --file=my_openapi.json
```
