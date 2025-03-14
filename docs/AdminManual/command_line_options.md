---
title: Command Line Options
---

# Command Line Options

Visionatrix supports a range of command-line options to manage installation, updating, execution, and configuration of the application. These options combine Visionatrix-specific functionality with many of the command-line features inherited from ComfyUI. Note that for some settings, values stored in the database or provided via environment variables take precedence over command-line arguments.

## Global Options

- `--verbose [LEVEL]`: Set the logging level.
  **Choices:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
  **Note:** This option should be specified **before** the command.

## Commands Overview

Visionatrix provides the following commands:

- **install**: Performs cleanup and initialization.
- **update**: Updates Visionatrix to the latest version.
- **run**: Starts Visionatrix.
- **install-flow**: Installs a flow by name, tag, or from a file.
- **create-user**: Creates a new user.
- **orphan-models**: Removes orphan models.
- **openapi**: Generates OpenAPI specifications.
- **list-global-settings**: Lists all global settings.
- **get-global-setting**: Retrieves a specific global setting.
- **set-global-setting**: Creates or updates a global setting.

> **Note:** In previous versions, options such as `--comfyui_dir` could be used to specify the ComfyUI directory. In the current version, directory paths (e.g. `COMFYUI_DIR`, `BASE_DATA_DIR`) are determined by the database settings and environment variables. To override these, update the corresponding global settings or environment variables.

---

## The `run` Command

Starts the Visionatrix application, enabling both task processing and (optionally) the web user interface.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] run [options]
```

### Visionatrix-Specific Options

- `--host=HOST`: Host to listen on (DEFAULT or SERVER mode).

    !!! info

        This corresponds to ComfyUI's `--listen` argument.

- `--port=PORT`: Port number to bind to (used in DEFAULT or SERVER mode).
- `--server=SERVER_ADDRESS`: Address of the Vix Server (used in WORKER mode).
- `--mode {DEFAULT,WORKER,SERVER}`: Visionatrix operating mode.

    Choices: [DEFAULT](WorkingModes/working_modes.md#default), [WORKER](WorkingModes/working_modes.md#worker), [SERVER](WorkingModes/working_modes.md#server)

- `--ui [UI_DIR]`: Enables the web user interface.
  - When provided **without** a value, the default UI is enabled.
  - When provided with a directory, it specifies a custom UI.
- `--disable-device-detection`: Disables automatic device detection.

Additionally, ComfyUI-specific options (except those unsupported) can be passed; these will be forwarded to ComfyUI. Unsupported ComfyUI options include:
  - `--tls-keyfile`
  - `--tls-certfile`
  - `--enable-cors-header`
  - `--verbose` (use Visionatrix’s `--verbose` instead)
  - `--dont-print-server`
  - `--quick-test-for-ci`
  - `--windows-standalone-build`
  - `--auto-launch`
  - `--disable-auto-launch`
  - `--multi-user` (Visionatrix always supports multiple users)

---

## The `install` Command

Performs a clean installation by removing existing flows and reinstalling ComfyUI and related components.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] install
```

During installation, if a ComfyUI folder is already present, you will be prompted to confirm its removal.

---

## The `update` Command

Updates components such as ComfyUI, ComfyUI-Manager and custom nodes to the pinned versions that comes with this version of Visionatrix.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] update
```

---

## The `install-flow` Command

Installs a flow by specifying a file, flow name, or flow tag. This command is particularly useful in environments without a user interface.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] install-flow [options]
```

### Options

You must provide one of the following:

- `--file=FILE_PATH`: Path to a `comfyui_flow.json` file or a directory containing flow files.
- `--name=FLOW_NAME`: A flow name mask to identify flows by their ID.
- `--tag=TAG`: A flow tag mask to identify flows by tag.

---

## The `create-user` Command

Creates a new user in the Visionatrix system.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] create-user [options]
```

### Options

- `--name=USERNAME` (required): User ID.
- `--password=PASSWORD` (required): User password.
- `--full_name=FULL_NAME`: Full name of the user.
  *Default:* `John Doe`
- `--email=EMAIL`: User's email address.
  *Default:* `user@example.com`
- `--admin=BOOLEAN`: Whether the user should be an administrator.
  *Default:* `True`
- `--disabled=BOOLEAN`: Whether the account should be disabled.
  *Default:* `False`

---

## The `orphan-models` Command

Removes orphan models that are no longer needed by the system.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] orphan-models [options]
```

### Options

- `--no-confirm`: Do not prompt for confirmation for each model.
- `--dry-run`: Execute a trial run without actually removing models.
- `--include-useful-models`: Include orphaned models that may be useful for future flows.

---

## The `openapi` Command

Generates OpenAPI specifications for the Visionatrix API, covering endpoints for flows and other features.

### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] openapi [options]
```

### Options

- `--file=FILENAME`: Output filename for the OpenAPI specification.
  *Default:* `openapi.json`
- `--indentation=SIZE`: Indentation size for the generated JSON.
  *Default:* `2`
- `--flows=FLOWS`: Comma-separated list of flows to include in the spec.
  - Use `*` to include all flows.
  - An empty string (e.g., `--flows=""`) will exclude flows.
- `--skip-not-installed`: Skip flows that are not installed.
  *Default:* Enabled.
- `--exclude-base`: Exclude base application endpoints from the specification.

---

## Global Settings Commands

Visionatrix allows you to manage global settings directly from the command line.

### The `list-global-settings` Command

Lists all global settings stored in the database.

#### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] list-global-settings
```

This command displays each setting in the following format:

```
 - setting_name = "value"
```

---

### The `get-global-setting` Command

Retrieves the value of a specific global setting.

#### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] get-global-setting --key=SETTING_NAME
```

---

### The `set-global-setting` Command

Creates or updates a global setting.

#### Syntax

```shell
python3 -m visionatrix [--verbose=LEVEL] set-global-setting --key=SETTING_NAME --value=VALUE [--sensitive]
```

- The `--sensitive` flag marks the setting as sensitive (hiding it from non-admin users).

---

## Examples

### Running Visionatrix with Custom Options

Start Visionatrix in SERVER mode on a specific host and port with the default Web UI:

```shell
python3 -m visionatrix --verbose=WARNING run --host=0.0.0.0 --port=8000 --ui
```

### Running Visionatrix in WORKER Mode

Connect a worker instance to a Vix Server:

```shell
python3 -m visionatrix --verbose=INFO run --mode WORKER --server=http://your_vix_server_address
```

### Installing a Flow from a File

Install a flow by providing the path to a flow JSON file:

```shell
python3 -m visionatrix install-flow --file=/path/to/comfyui_flow.json
```

### Creating a New User

Create a new administrator user:

```shell
python3 -m visionatrix create-user --name=admin --password=secret --email=admin@example.com
```

### Removing Orphan Models

Perform a dry-run cleanup of orphan models without confirmation prompts:

```shell
python3 -m visionatrix orphan-models --no-confirm --dry-run
```

### Generating OpenAPI Specifications

Generate an OpenAPI specification that includes all flows:

```shell
python3 -m visionatrix openapi --flows="*" --file=openapi.json
```

### Listing Global Settings

Display all global settings:

```shell
python3 -m visionatrix list-global-settings
```

### Retrieving a Specific Global Setting

Retrieve the value of a global setting:

```shell
python3 -m visionatrix get-global-setting --key=comfyui_folder
```

### Setting a Global Setting

Update or create a global setting (marking it as sensitive if needed):

```shell
python3 -m visionatrix set-global-setting --key=comfyui_folder --value=/new/path/to/ComfyUI --sensitive
```
