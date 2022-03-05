# On Windows

## Overview

Windows requires the installation of WSL 2 backend and Docker and can be immediately run from your web browser.

## Setup Guide

**1. Check out system requirements from [Docker documentation](https://docs.docker.com/desktop/windows/install/).**

Follow the steps on the system requirements, and necessarily, download and install the Linux kernel update package.

**2. Install Docker Desktop on Windows.**

Install Docker Desktop following the guidelines, and reboot your computer.

**3. You're done!

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```
* In your browser, just visit [http://localhost:8000](http://localhost:8000)
* Start moving some data!
