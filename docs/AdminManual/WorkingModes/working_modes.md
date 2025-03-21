---
title: Working modes
---

# Working modes

## DEFAULT

Visionatrix(**Vix**) consists of:

1.  A server component, namely, the backend `(in short - Server)`
2.  A component responsible for processing tasks `(in short - Worker)`
3.  TaskQueue - a database (SQLite *(default)*, PgSQL)
4.  A simple and understandable User Interface

By default, Vix launches with all components integrated (Server +
Worker + UI) for quick and easy use on a single computer.

This is **DEFAULT** mode, in which everything is executed within a
single process.

Easy installation, no need to configure, just launch and use.

!!! note

    There is no support for multiple users or authentication in this case,
    as this mode uses **SQLite** as a database, which is limiting. But for home use in most cases this is not necessary.

## SERVER

In most scenarios, including home use, you likely have more than one
device capable of handling AI tasks. In such cases, it is allowed and
recommended to run the server part and the AI processing part of the
task separately.

!!! warning

    **We recommend using PgSQL database in this mode, as SQLite does not support parallel data writing..**


Steps to run `Vix` in a Server mode:

1.  Install both `psycopg` and `greenlet` python libraries:

    `pip install psycopg greenlet`

2.  Set `VIX_MODE` environment variable to `SERVER`

3.  Setup **PostgreSQL** database and set `DATABASE_URI` environment variable to point on it.

    !!! note

        [PgSQL example](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#module-sqlalchemy.dialects.postgresql.psycopg):
        `DATABASE_URI="postgresql+psycopg://vix_user:vix_password@localhost:5432/vix_db"`

4.  Use `python3 -m visionatrix create-user` command to create a user in the database.

5.  Connect at least one Worker to handle task processing.

*We will provide a docker-compose file soon, with full server setup to deploy it in one click.*

## WORKER

Each worker can have a different set of tasks (Flows) installed, which
is useful to avoid installing a task on a worker instance that cannot
handle it. A worker will only request the tasks installed for it.

There is two worker modes, both will be described, we ourselves most use **Vix* in the `Worker to Server` mode.

### Worker to Database-FS

!!! note

    Requirements:

    1.  The database used by the **Server** should be accessible for the worker.
    2.  There should be the ability to map the **Server**'s `vix_tasks_files` folder to the worker.

Set the environment variable `VIX_MODE` to **WORKER** and leave `VIX_SERVER` with an empty value.

In this scenario, the worker must be configured with the correct
database path using the `DATABASE_URI` environment variable.

The format can be viewed here: [SqlAlchemy Database URLs](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls)

By using the `TASKS_FILES_DIR` environment variable or the
`--tasks_files_dir` argument, you can change the location of the `vix_tasks_files` folder.

The worker must have access to the Server's `vix_tasks_files` folder.

With this scaling method, workers independently retrieve tasks from the
database and directly write the execution results to the servers *TASKS_FILES_DIR*.

In this setup, you can imagine workers as Server threads operating remotely.

See installation guide for this mode: [Worker To Database-FS](worker_to_database.md)

### Worker to Server

This method implies that the workers do not have direct access to the database or the server file system.

All communication occurs through the network, with workers accessing the server backend directly.

Set the environment variable `VIX_MODE` to **WORKER** and set
`VIX_SERVER` with the full address of the Server(including port number).

!!! note

    `VIX_HOST`, `VIX_PORT`, `DATABASE_URI` will be ignored, as the worker in this mode does not need it.

In this use case, the **vix_tasks_files** directory will contain only
temporary files; after uploading results to the Server, the results from
the worker instance will be cleared.

For authentication on the server worker will use `WORKER_AUTH`
environment variable, which must contain "**USER_ID:PASSWORD**".

!!! note

    Workers with an administrator account can process all tasks of all
    users, workers assigned to a user account can only process tasks created by that user.
