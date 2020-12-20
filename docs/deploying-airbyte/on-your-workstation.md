# On Your Workstation

{% hint style="info" %}
These instructions have been tested on MacOS
{% endhint %}

## System requirements
The following software should be installed on your machine. 
* Docker \(see [Docker](https://www.docker.com/products/docker-desktop). Note: There is a known issue with docker-compose 1.27.3. If you are using that version, please upgrade to 1.27.4.
* Java 14
* Python 3.7.9
* Node 14 

#### A note on versions
These versions do not need to be your system defaults; they only need to be available. While Airbyte may function correctly with other versions of the requirements it is regularly tested with the versions listed above. 

## Setup & launch Airbyte
Clone Airbyte's repository and run `docker compose
```bash
# In your workstation terminal
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

After starting up, Airbyte will print a message to the terminal indicating it's ready: 
```

    ___    _      __          __
   /   |  (_)____/ /_  __  __/ /____
  / /| | / / ___/ __ \/ / / / __/ _ \
 / ___ |/ / /  / /_/ / /_/ / /_/  __/
/_/  |_/_/_/  /_.___/\__, /\__/\___/
                    /____/
--------------------------------------
 Now ready at http://localhost:8000/
--------------------------------------
```

In your browser, visit [http://localhost:8000](http://localhost:8000) and start moving some data!

## Troubleshooting

If you encounter any issues, just connect to our [Slack](https://slack.airbyte.io) or open an issue on our [Github repo](https://github.com/airbytehq/airbyte). Our community will help!

