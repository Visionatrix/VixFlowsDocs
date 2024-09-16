---
title: Worker to Database-FS Mode
---

# Setup: Worker to Database-FS Mode

**This is the simplest production setup, when everything is up and running on one server.**

!!! note

    We also use this setup for benchmarks.

*This guide is for Ubuntu, adjust it for you needs for different Linux distros.*

1. Log in to the server: `ssh ...`

    !!! note

        if necessary, add port forwarding: *-L 127.0.0.1:8288:127.0.0.1:8288*

2. If we are under `root` user and the system is fully clear, install **sudo**:

    ```bash
    apt update && apt install -y sudo
    ```

3. Install Python, Git, Compilers, etc:

    ```bash
    sudo apt update && apt install -y wget curl python3-venv python3-pip build-essential git
    ```

4. Install and start PgSQL database and create Visionatrix user:

    ```bash
    apt install -y postgresql postgresql-contrib && pg_ctlcluster 14 main start && \
    \
    sudo -u postgres psql -c "CREATE USER vix_user WITH PASSWORD 'vix_password';" && \
    sudo -u postgres psql -c "CREATE DATABASE vix_db OWNER vix_user;" && \
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vix_db TO vix_user;"
    ```

5. Run Visionatrix installation:

    ```bash
    wget -O easy_install.py https://raw.githubusercontent.com/Visionatrix/Visionatrix/main/scripts/easy_install.py && \
    COMPUTE_DEVICE=NVIDIA DEV_VERSION=1 BUILD_RELEASE=1 python3 easy_install.py && \
    cd Visionatrix && source venv/bin/activate && \
    pip install ".[pgsql]" && \
    \
    USER_PASSWORD=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9' | head -c 16) && \
    DATABASE_URI="postgresql+psycopg://vix_user:vix_password@localhost:5432/vix_db" \
    python3 -m visionatrix create-user --name admin --password "$USER_PASSWORD" && \
    echo "User 'admin' created with password: $USER_PASSWORD"
    ```

6. Run Visionatrix Server:

    ```bash
    DATABASE_URI="postgresql+psycopg://vix_user:vix_password@localhost:5432/vix_db" \
    VIX_SERVER_FULL_MODELS=1 python3 -m visionatrix run --ui --mode=SERVER > server.log 2>&1 & echo "Server PID: $!"
    ```

7. Run Visionatrix Worker:

    ```bash
    DATABASE_URI="postgresql+psycopg://vix_user:vix_password@localhost:5432/vix_db" \
    python3 -m visionatrix run --mode=WORKER > worker.log 2>&1 & echo "Worker PID: $!"
    ```
