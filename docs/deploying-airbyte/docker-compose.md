# Docker Compose

:::info
These instructions have been tested on MacOS, Windows 10 and Ubuntu 22.04.

:::

## Setup & launch Airbyte

- Install `Docker Engine` and the `Docker Compose plugin` on your workstation \(see [instructions](https://docs.docker.com/engine/install/)\).
- After Docker is installed, you can immediately get started locally by running:

```bash
# clone Airbyte from GitHub
git clone --depth=1 https://github.com/airbytehq/airbyte.git

# switch into Airbyte directory
cd airbyte

# start Airbyte
./run-ab-platform.sh
```

- In your browser, visit [http://localhost:8000](http://localhost:8000)
- You will be asked for a username and password. By default, that's username `airbyte` and password `password`. Once you deploy Airbyte to your servers, be sure to change these in your `.env` file:

```yaml
# Proxy Configuration
# Set to empty values, e.g. "" to disable basic auth
BASIC_AUTH_USERNAME=your_new_username_here
BASIC_AUTH_PASSWORD=your_new_password_here
```

- Start moving some data!

## Deploy on Windows

After installing the WSL 2 backend and Docker you should be able to run containers using Windows PowerShell. Additionally, as we note frequently, you will need `docker-compose` to build Airbyte from source. The suggested guide already installs `docker-compose` on Windows.

### Setup Guide

**1. Check out system requirements from [Docker documentation](https://docs.docker.com/desktop/windows/install/).**

Follow the steps on the system requirements, and necessarily, download and install the Linux kernel update package.

**2. Install Docker Desktop on Windows.**

Install [Docker Desktop](https://docs.docker.com/desktop/windows/install/) from here.

Make sure to select the options:

1. _Enable Hyper-V Windows Features_
2. _Install required Windows components for WSL 2_
   when prompted. After installation, it will require to reboot your computer.

**3. You're done!**

```bash
git clone --depth=1 https://github.com/airbytehq/airbyte.git
cd airbyte
bash run-ab-platform.sh
```

- In your browser, just visit [http://localhost:8000](http://localhost:8000)
- You will be asked for a username and password. By default, that's username `airbyte` and password `password`. Once you deploy airbyte to your servers, be sure to change these.
- Start moving some data!

## Troubleshooting

If you have any questions about the local setup and deployment process, head over to our [Getting Started FAQ](https://github.com/airbytehq/airbyte/discussions/categories/questions) on our Airbyte Forum that answers the following questions and more:

- How long does it take to set up Airbyte?
- Where can I see my data once I've run a sync?
- Can I set a start time for my sync?

If you encounter any issues, check out [Getting Support](/community/getting-support) documentation
for options how to get in touch with the community or us.
