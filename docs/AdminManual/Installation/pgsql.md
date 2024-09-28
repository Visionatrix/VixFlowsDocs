---
title: Installing PostgreSQL
---

# How to Install PostgreSQL

This guide provides step-by-step instructions on how to install PostgreSQL on Linux, macOS, and Windows systems.

This is recommended only for Visionatrix running in [SERVER](../WorkingModes/working_modes.md#server) mode.

---

## Installation on Linux

### Installing on Ubuntu/Debian

#### Step 1: Update Package Lists

Open a terminal and update your package lists:

```bash
sudo apt update
```

#### Step 2: Install PostgreSQL

Install PostgreSQL along with the `postgresql-contrib` package, which provides additional utilities and features:

```bash
sudo DEBIAN_FRONTEND=noninteractive apt install -y postgresql postgresql-contrib
```

**Note:** This command will install the default version of PostgreSQL available in your distribution's repositories.

#### Step 3: Start PostgreSQL

Start the PostgreSQL service:

```bash
sudo systemctl start postgresql
```

### Installing on CentOS/RHEL

#### Step 1: Add Repository

Enable the PostgreSQL repository for the desired version.

Replace `13` with your preferred version (`12`, `13`, `14`, etc.):

```bash
sudo yum install -y https://download.postgresql.org/pub/repos/yum/13/redhat/rhel-$(rpm -E %{rhel})-x86_64/pgdg-redhat-repo-latest.noarch.rpm
```

**Note:** Where you see `postgresql13`, it can be `postgresql12` or `postgresql14` based on the version you want.

#### Step 2: Disable the Default PostgreSQL Module

For CentOS/RHEL 8 and newer:

```bash
sudo dnf -qy module disable postgresql
```

#### Step 3: Install PostgreSQL

Install PostgreSQL server:

```bash
sudo yum install -y postgresql13-server
```

#### Step 4: Initialize and Enable

Initialize the database and enable automatic start:

```bash
sudo /usr/pgsql-13/bin/postgresql-13-setup initdb
sudo systemctl enable postgresql-13
sudo systemctl start postgresql-13
```

### Installing on Fedora

#### Step 1: Install PostgreSQL

Install PostgreSQL server and contrib packages:

```bash
sudo dnf install postgresql-server postgresql-contrib
```

#### Step 2: Initialize Database

Initialize the PostgreSQL database:

```bash
sudo postgresql-setup --initdb
```

### Step 3: Start PostgreSQL

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

## Installation on macOS

### Using Homebrew

#### Step 1: Install Homebrew

If you don't have Homebrew installed, run:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Update Homebrew

```bash
brew update
```

#### Step 3: Install PostgreSQL

```bash
brew install postgresql
```

### Step 4: Start PostgreSQL

To start PostgreSQL now and restart at login:

```bash
brew services start postgresql
```

Or, to run it manually:

```bash
pg_ctl -D /usr/local/var/postgres start
```

### Using PostgreSQL Installer

#### Step 1: Download the Installer

Download the PostgreSQL installer for macOS from the [official PostgreSQL website](https://www.postgresql.org/download/macosx/).

### Step 2: Run the Installer

- Open the downloaded `.dmg` file.
- Run the installer and follow the on-screen instructions.
- Set a password for the `postgres` user when prompted.

---

## Installation on Windows

### PostgreSQL Installer

#### Step 1: Download the Installer

Download the PostgreSQL installer for Windows from the [official PostgreSQL website](https://www.postgresql.org/download/windows/).

#### Step 2: Run the Installer

- Double-click the downloaded `.exe` file.
- Follow the installation wizard steps:
    - Set a password for the PostgreSQL superuser (`postgres`).
    - Choose the port number (default is 5432).
    - Wait for the installation to complete.

---

## Post-Installation Setup

### Initializing the Database

In most cases, the database is initialized during installation. If not, follow the steps below.

#### On Linux

For versions installed via package managers:

```bash
sudo su - postgres
```

Then initialize the database(*not always required*):

```bash
initdb -D /var/lib/pgsql/data
```

### Starting the PostgreSQL

Ensure PostgreSQL is running and set to start on boot.

#### On Ubuntu/Debian

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### On CentOS/RHEL

```bash
sudo systemctl start postgresql-13
sudo systemctl enable postgresql-13
```

**Note:** Replace `13` with your PostgreSQL version number.

#### On Fedora

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### On macOS (Manual Start)

```bash
pg_ctl -D /usr/local/var/postgres start
```

### Creating a User and Database

We will create a database named `vix_db` and a user `vix_user` with password `vix_password`, as required by Visionatrix.

#### Option 1: Via PgSQL Shell

##### Step 1: Switch to `postgres`

```bash
sudo -u postgres psql
```

##### Step 2: Create User

```sql
CREATE USER vix_user WITH PASSWORD 'vix_password';
```

##### Step 3: Create Database

```sql
CREATE DATABASE vix_db OWNER vix_user;
```

##### Step 4: Grant Privileges

```sql
GRANT ALL PRIVILEGES ON DATABASE vix_db TO vix_user;
```

##### Step 5: Exit Shell

```sql
\q
```

#### Option 2: Direct Commands

You can execute all commands directly from the terminal:

```bash
sudo -u postgres psql -c "CREATE USER vix_user WITH PASSWORD 'vix_password';"
sudo -u postgres psql -c "CREATE DATABASE vix_db OWNER vix_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE vix_db TO vix_user;"
```

---

## Configuring Visionatrix

After installing and configuring PostgreSQL, you need to set the `DATABASE_URI` environment variable for Visionatrix to connect to the PostgreSQL database.

Set the `DATABASE_URI` as follows:

```bash
DATABASE_URI="postgresql+psycopg://vix_user:vix_password@localhost:5432/vix_db"
```

This tells Visionatrix to connect to the PostgreSQL database `vix_db` on `localhost` using the user `vix_user` and password `vix_password` on port `5432`.

Make sure to export this variable or set it in your Visionatrix configuration file as per the installation instructions.

Good luck!
