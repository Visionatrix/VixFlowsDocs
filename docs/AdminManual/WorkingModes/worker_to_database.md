---
title: Worker to Database-FS Mode
---

# Setup: Worker to Database-FS Mode

**This is the simplest production setup, when everything is up and running on one server.**

!!! note

    We also use this setup for benchmarks.

*This guide is for Ubuntu. Adjust it to your needs for different Linux distributions.*

1. Log in to the server: `ssh ...`

    !!! note

        if necessary, add port forwarding: *-L 127.0.0.1:8288:127.0.0.1:8288*

2. If you are logged in as the `root` user on a clean system, install `sudo`:

    ```bash
    apt update && apt install -y sudo
    ```

3. Install Python, Git, and essential build tools:

    ```bash
    sudo apt update && sudo apt install -y wget curl python3-venv python3-pip build-essential git
    ```

    !!! note

        On some systems you need additionally to install `cv2` dependencies:

        ```bash
        sudo apt install -y ffmpeg libsm6 libxext6
        ```

4. Install and start PostgreSQL:

    ```bash
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    sudo systemctl status postgresql
    ```

    <details>
       <summary>For benchmark automation script</summary>

       ```bash
       sudo DEBIAN_FRONTEND=noninteractive apt install -y postgresql postgresql-contrib && pg_ctlcluster 14 main start && \
       \
       sudo -u postgres psql -c "CREATE USER vix_user WITH PASSWORD 'vix_password';" && \
       sudo -u postgres psql -c "CREATE DATABASE vix_db OWNER vix_user;" && \
       sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vix_db TO vix_user;"
       ```
     </details>

5. Create a Visionatrix DB user:

    ```bash
    sudo -u postgres psql -c "CREATE USER vix_user WITH PASSWORD 'vix_password';"
    sudo -u postgres psql -c "CREATE DATABASE vix_db OWNER vix_user;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vix_db TO vix_user;"
    ```

    !!! warning

        If you encounter the following error during Visionatrix startup:

        ```password authentication failed for user "vix_user"```

        <details>
          This means you need to enable password authentication for the `vix_user`.


          Edit `pg_hba.conf` file (typically located at `/etc/postgresql/XX/main/pg_hba.conf`) by adding following:

          ```
          host    all             vix_user        127.0.0.1/32            md5
          ```

          Then, restart PostgreSQL:

          ```bash
          sudo systemctl restart postgresql
          ```

          or

          ```bash
          sudo service postgresql restart
          ```

        </details>

6. Install Visionatrix:

    ```bash
    wget -O easy_install.py https://raw.githubusercontent.com/Visionatrix/Visionatrix/main/scripts/easy_install.py && \
    python3 easy_install.py && \
    cd Visionatrix && source venv/bin/activate && \
    pip install ".[pgsql]" && \
    \
    USER_PASSWORD=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9' | head -c 16) && \
    DATABASE_URI="postgresql+psycopg://vix_user:vix_password@localhost:5432/vix_db" \
    python3 -m visionatrix create-user --name admin --password "$USER_PASSWORD" && \
    echo "User 'admin' created with password: $USER_PASSWORD"
    ```

    <details>
      <summary>For benchmark automation script (CUDA, Dev version)</summary>

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
    </details>

7. Start the Visionatrix Server(*from activated venv*):

    ```bash
    DATABASE_URI="postgresql+psycopg://vix_user:vix_password@localhost:5432/vix_db" \
    VIX_SERVER_FULL_MODELS=1 python3 -m visionatrix run --ui --mode=SERVER > server.log 2>&1 & echo "Server PID: $!"
    ```

8. Start the Visionatrix Worker(*from activated venv*):

    ```bash
    DATABASE_URI="postgresql+psycopg://vix_user:vix_password@localhost:5432/vix_db" \
    python3 -m visionatrix run --mode=WORKER > worker.log 2>&1 & echo "Worker PID: $!"
    ```
