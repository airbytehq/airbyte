# Local Deployment
This page guides you through setting up your Airbyte on your local machine. 

## Prerequisites
* [Install Docker](https://docs.docker.com/get-docker/) and make sure you have the latest version of `docker-compose` installed.
* Additionally, for Windows, install [WSL 2 backend](https://docs.docker.com/desktop/windows/wsl/)  and enable Hyper-V Windows Features".

> **_Note:_** These instructions have been tested on MacOS, Windows 10, and Ubuntu 20.04.

## Deploy on Mac and Linux
To set up Airbyte on your local machine:

1. Clone the Airbyte repository.
2. Move into the cloned folder (`airbyte`) and start the server with `docker compose`;

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker compose up
```
3. In your browser, visit http://localhost:8000
> **_Note:_** You will be asked for a username and password. The default username is `airbyte` and the password is `password`.

## Deploy on Windows
To set up Airbyte on your Windows machine:

1. Clone the Airbyte repository.
2. Move into the cloned folder (`airbyte`) and start the server with `docker compose`

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker compose up
```
3. In your browser, visit http://localhost:8000
4. You will be asked for a username and password. The default username is `airbyte` and the password is `password`.

### Troubleshooting
If you encounter any issues, reach out to our community on [Slack](https://slack.airbyte.com/).
