---
title: Environment Variables
---

# Environment Variables

In addition to the usual ways of setting environment variables, they can be set via a `.env` file. Visionatrix uses the [python-dotenv](https://pypi.org/project/python-dotenv/) package to load variables from a `.env` file.

Additionally, some variables can also be specified via command-line arguments, which take precedence over environment variables.

This document describes the available environment variables, their default values, and how they affect Visionatrix's operation.

## Using a `.env` File

To simplify configuration, you can create a `.env` file in the root directory of your Visionatrix installation. In this file, you can define environment variables in the format:

```ini
VARIABLE_NAME=value
```

## General Variables

### BACKEND_DIR

- **Description**: Directory for the folder containing ComfyUI. The path can be absolute or relative.
- **Default**: `./vix_backend`

    !!! note

        The command-line argument `--backend_dir=BACKEND_DIR` takes precedence over the environment variable.

### FLOWS_DIR

- **Description**: Directory for storing flows. The path can be absolute or relative.
- **Default**: `./vix_flows`

    !!! note

        The command-line argument `--flows_dir=FLOWS_DIR` takes precedence over the environment variable.

### MODELS_DIR

- **Description**: Directory for the models. The path can be absolute or relative.
- **Default**: `./vix_models`

    !!! note

        The command-line argument `--models_dir=MODELS_DIR` takes precedence over the environment variable.

### TASKS_FILES_DIR

- **Description**: Directory for input/output files. The path can be absolute or relative.
- **Default**: Absolute path to `./vix_tasks_files`

    !!! note

        The command-line argument `--tasks_files_dir=FILES_DIR` takes precedence over the environment variable.

### UI_DIR

- **Description**: Path to the User Interface (JavaScript frontend). This is the directory that will be served as the root of the website.
- **Default**: Empty string.

    !!! note

        - **Command-line Argument**:
          - `--ui` (enables the User Interface using the default frontend), or
          - `--ui=/path/to/frontend` (specifies the path to a custom frontend).

        Command-line arguments take precedence over the environment variable.

### VIX_MODE

- **Description**: Determines the working mode of Visionatrix.
  - `DEFAULT`: Storage and delivery of tasks (Server) + task processing (Worker).

    !!! note

        Authentication is disabled in this mode.

  - `SERVER`: Only storage and management of tasks.

    !!! note

        Authentication is enabled. Requires a PostgreSQL database.

  - `WORKER`: Only processes tasks from the Server (client consuming mode, no backend).
- **Default**: `DEFAULT`

    !!! note

        The command-line argument `--mode=` takes precedence over the environment variable.

Please refer to the [Working Modes](WorkingModes/working_modes.md) documentation for more details.

## Variables for Specific Modes

### SERVER and DEFAULT Mode

#### VIX_HOST

- **Description**: Address to bind to in the `DEFAULT` or `SERVER` mode.
- **Default**: `127.0.0.1` (binds to the local interface)

    !!! note

        The command-line argument `--host=HOST` takes precedence over the environment variable.

#### VIX_PORT

- **Description**: Port to bind to in the `DEFAULT` or `SERVER` mode.
- **Default**: `8288`

    !!! note

        The command-line argument `--port=PORT` takes precedence over the environment variable.

#### VIX_SERVER_WORKERS

- **Description**: Number of server instances to spawn (using Uvicorn). Useful for production environments with a large number of users.
- **Default**: `1`

#### VIX_SERVER_FULL_MODELS

- **Description**: Flag that determines whether full models rather than dummy models should be stored in `SERVER` mode. Useful when both the Server and Workers are on the same machine, or when the `MODELS_DIR` is shared between the Server and Workers.
- **Default**: `0` (disabled)
- **Set to**: `1` to enable.

#### DATABASE_URI

- **Description**: URI for the database used by Visionatrix. Required in `SERVER` mode.

    !!! warning

        SQLite is **not supported** in the `SERVER` mode.

- **Default**: `sqlite:///./tasks_history.db`
  - For SQLite: If the path is relative, it is relative to the current directory.
- **Note**: For PostgreSQL, the format is: `postgresql+psycopg://user:password@host:port/database`

### WORKER Mode

When running in `WORKER` mode, the following variables are relevant:

#### VIX_SERVER

- **Description**: The full URL of the Server to connect to when running in `WORKER` mode in the [Worker to Server](WorkingModes/working_modes.md#worker-to-server) configuration.
- **Default**: Empty string (must be set in `WORKER` mode if not using `DATABASE_URI`)

    !!! warning

        If `VIX_SERVER` is set, the Worker will communicate with the Server via the network; `DATABASE_URI` will be ignored.

        You are **required** to specify either `VIX_SERVER` **or** `DATABASE_URI` for the Worker, so it can fetch tasks to process.

#### DATABASE_URI

- **Description**: In `WORKER` mode, it is used only for the [Worker to Database-FS](WorkingModes/working_modes.md#worker-to-database-fs) configuration.
- **Default**: `sqlite:///./tasks_history.db`
  - **Note**: For Workers connecting directly to a PostgreSQL database, use the appropriate `DATABASE_URI`.

#### WORKER_AUTH

- **Description**: Authentication credentials for the Worker when connecting to the Server. Format: `USER_ID:PASSWORD`
- **Default**: `admin:admin`

    !!! note

        This is only applicable for the **Worker to Server** configuration.

#### WORKER_NET_TIMEOUT

- **Description**: Network timeout in seconds for the Worker when communicating with the Server.
- **Default**: `15.0`

    !!! note

        This is only applicable for the **Worker to Server** configuration.

### Other Variables

#### FLOWS_URL

- **Description**: URLs or file paths (separated by semicolons `;`) that point to locations of archive files containing lists and definitions of Visionatrix workflows. Specifies where Visionatrix fetches the available flows.
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

- **Description**: Maximum number of parallel downloads allowed during workflow installation.
- **Default**: `2`

#### MAX_GIT_CLONE_ATTEMPTS

- **Description**: Maximum number of attempts to perform `git clone` operations during installation or updates.
- **Default**: `3`

#### CORS_ORIGINS

- **Description**: A comma-separated list of origins that are allowed to make Cross-Origin Resource Sharing (CORS) requests to the server. This is necessary when the frontend and backend are hosted on different domains or ports. By specifying allowed origins, you enable frontend applications running on those origins to interact with the Visionatrix backend.
- **Default**: Empty string (CORS is disabled; only same-origin requests are allowed).
- **Example**:

    ```ini
    CORS_ORIGINS="http://localhost:3000,http://192.168.1.132:3000,http://192.168.1.132:8288"
    ```

    In this example, requests are permitted from:

    - `http://localhost:3000`
    - `http://192.168.1.132:3000`
    - `http://192.168.1.132:8288`

    !!! note

        This setting is important when developing or deploying the frontend separately from the backend, especially during development when the frontend might be served by a development server on a different port.

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
