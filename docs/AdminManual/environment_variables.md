---
title: Environment Variables
---

# Environment Variables

Visionatrix uses environment variables for configuration and customization. You can set these variables in your system environment or via a .env file, using the [python-dotenv](https://pypi.org/project/python-dotenv/) package.

Additionally, some variables can also be specified via command-line arguments, which take precedence over environment variables.

This document describes the available environment variables, their default values, and how they affect Visionatrix's operation.

## Using a `.env` File

To simplify configuration, you can create a `.env` file in the root directory of your Visionatrix installation. In this file, you can define environment variables in the format:

```ini
VARIABLE_NAME=value
```

## General Variables

### BACKEND_DIR

- **Description**: Directory for the backend (folder containing ComfyUI). (TODO: add info that it can absolute or relative)
- **Default**: `./vix_backend`

    !!! note

        Command-line argument `--backend_dir=BACKEND_DIR` has priority over the environment variable.

### FLOWS_DIR

- **Description**: Directory for storing flows.  (TODO: add info that it can absolute or relative)
- **Default**: `./vix_flows`

    !!! note

        Command-line argument `--flows_dir=FLOWS_DIR` has priority over the environment variable.

### MODELS_DIR

- **Description**: Directory for the models.
- **Default**: `./vix_models`

    !!! note

        Command-line argument `--models_dir=MODELS_DIR` has priority over the environment variable.

### TASKS_FILES_DIR

- **Description**: Directory for input/output files.
- **Default**: Absolute path to `./vix_tasks_files`.  (TODO: add info that it can absolute or relative)

    !!! note

        Command-line Argument**: `--tasks_files_dir=FILES_DIR` has priority over the environment variable.

### UI_DIR

- **Description**: Path to the User Interface (JavaScript frontend). This is the directory that will be served as the root of the website.
- **Default**: Empty string.
- **Command-line Argument**: `--ui` (flag to enable the User Interface; takes precedence over environment variable). TODO: if it is specified just like a flag in cmd, then default frontend will be used. if additional argument specified to it then it should be path to the folder with frontend

### VIX_MODE

- **Description**: Determines the working mode of Visionatrix.
  - `DEFAULT`: Storage and delivery of tasks (Server) + tasks processing (Worker), authentication is disabled.
  - `SERVER`: Only storage and management of tasks, authentication is enabled, requires PostgreSQL database.
  - `WORKER`: Only processing tasks for the Server (client consuming mode, no backend).
- **Default**: `DEFAULT`

Please refer to the [Working Modes](WorkingModes/working_modes.md) documentation for more details.

## Variables for Specific Modes

### SERVER and DEFAULT mode

#### VIX_HOST

- **Description**: Address to bind in the `DEFAULT` or `SERVER` mode.
- **Default**: Empty string (binds to all available addresses). TODO: 127.0.0.1 interface is the default

#### VIX_PORT

- **Description**: Port to bind to in the `DEFAULT` or `SERVER` mode.
- **Default**: Empty string (default port is used). TODO: 8288 port is the default

#### VIX_SERVER_WORKERS

- **Description**: Number of server instances to spawn (using Uvicorn). Useful for a production with a huge number of users.
- **Default**: `1`

#### VIX_SERVER_FULL_MODELS

- **Description**: Flag that determines whether full models rather than dummy models should be stored in SERVER mode. Useful when both the Server and Workers are on the same machine, or when the `MODELS_DIR` is shared between the Server and Workers.
- **Default**: `0` (disabled)
- **Set to**: `1` to enable.

#### DATABASE_URI

- **Description**: URI for the database used by Visionatrix. Required in `SERVER` mode. SQLite is not supported in `SERVER` mode.
- **Default**: `sqlite:///./tasks_history.db`
  - For SQLite: If the path is relative, it is relative to the current directory.
- **Note**: For PostgreSQL, the format is: `postgresql+psycopg://user:password@host:port/database`

### WORKER Mode

When running in `WORKER` mode, the following variables are relevant:

#### VIX_SERVER

- **Description**: The full URL of the Server to connect to when running in `WORKER` mode in the [Worker to Server](WorkingModes/working_modes.md#worker-to-server) configuration.
- **Default**: Empty string.
- **Note**: If `VIX_SERVER` is set, the Worker will communicate with the Server via the network, and `DATABASE_URI` will be ignored.

#### WORKER_AUTH

- **Description**: Authentication credentials for the Worker when connecting to the Server. Format: `USER_ID:PASSWORD`. TODO: add info that it is only for "Worker to Server"
- **Default**: `admin:admin`

#### WORKER_NET_TIMEOUT

- **Description**: Network timeout in seconds for the Worker when communicating with the Server. TODO: add info that it is only for "Worker to Server"
- **Default**: `15.0`

### All Modes

#### DATABASE_URI

- **Description**: URI for the database used by Visionatrix. In `WORKER` mode, this is required when using the [Worker to Database-FS](WorkingModes/working_modes.md#worker-to-database-fs) configuration.
- **Default**: `sqlite:///./tasks_history.db`
- **Note**: For PostgreSQL, the format is: `postgresql+psycopg://user:password@host:port/database`

### Other Variables

#### FLOWS_URL

- **Description**: URL or path that points to the location of archive files containing lists and definitions of Visionatrix workflows. Specifies where Visionatrix fetches the available flows.
- **Default**: `https://visionatrix.github.io/VixFlowsDocs/`
- **More Information**: [Workflows Storage](../FlowsDeveloping/technical_information.md#workflows-storage)

#### MODELS_CATALOG_URL

- **Description**: URL or file path to fetch the models catalog for ComfyUI workflows. This catalog specifies available models.
- **Default**: `https://visionatrix.github.io/VixFlowsDocs/models_catalog.json`

#### MIN_PAUSE_INTERVAL

- **Description**: Minimum interval in seconds (float) that the Worker waits between checking for new tasks when none are available. Helps reduce server load when idle.
- **Default**: `0.1`

#### MAX_PAUSE_INTERVAL

- **Description**: Maximum interval in seconds (float) that the Worker waits between checking for new tasks when none are available. The pause interval increases gradually from `MIN_PAUSE_INTERVAL` to `MAX_PAUSE_INTERVAL` in 10 steps.
- **Default**: `1.0`

#### GC_COLLECT_INTERVAL

- **Description**: Interval in seconds (float) after which the GPU memory release and garbage collection procedure is called after task execution. Not recommended to change unless you know what you're doing.
- **Default**: `10.0`

#### USER_BACKENDS

- **Description**: List of user backends to enable. Each backend supports its own environment variables for configuration.
- **Default**: `vix_db`
- **Format**: Semicolon-separated list of backends (e.g., `vix_db;nextcloud`)
- **Example**:
  ```ini
  USER_BACKENDS=vix_db;nextcloud
  ```
  This will enable the `nextcloud` user backend in addition to the default `vix_db`.

#### MAX_PARALLEL_DOWNLOADS

- **Description**: Maximum number of parallel downloads allowed during flow installation.
- **Default**: `2`

#### MAX_GIT_CLONE_ATTEMPTS

- **Description**: Maximum number of attempts to perform `git clone` during the first installation or updates.
- **Default**: `3`

#### NODES_TIMING

- **Description**: If set to `1`, the execution time of each node will be logged.
- **Default**: `0` (disabled)
- **Set to**: `1` to enable.

## Notes on Configuration Priority

For variables that can be specified both via environment variables and command-line arguments (e.g., `BACKEND_DIR`, `FLOWS_DIR`, ...), the command-line arguments take precedence over environment variables. This allows for temporary overrides without changing the environment configuration.

## Examples

### Using a `.env` File

Create a file named `.env` in the root directory of Visionatrix with the following content:

```ini
# Set the working mode to SERVER
VIX_MODE=SERVER

# Set the database URI to use PostgreSQL
DATABASE_URI=postgresql+psycopg://vix_user:vix_password@localhost:5432/vix_db

# Set the number of server workers
VIX_SERVER_WORKERS=4

# Enable full models on the server
VIX_SERVER_FULL_MODELS=1

# Specify the host and port to bind to
VIX_HOST=0.0.0.0
VIX_PORT=8000
```

### Setting Variables in the Environment

On Linux or macOS:

```bash
export VIX_MODE=WORKER
export VIX_SERVER=http://server_address:8000
export WORKER_AUTH=worker_user:worker_password
```

On Windows Command Prompt:

```cmd
set VIX_MODE=WORKER
set VIX_SERVER=http://server_address:8000
set WORKER_AUTH=worker_user:worker_password
```

### Starting Visionatrix with Command-Line Arguments

```bash
python3 -m visionatrix run --backend_dir=/path/to/backend --flows_dir=/path/to/flows --models_dir=/path/to/models --tasks_files_dir=/path/to/tasks_files --ui
```

In this example, the directories are specified via command-line arguments, which will override any environment variables or settings in the `.env` file.
