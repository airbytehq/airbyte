# On Your Workstation

{% hint style="info" %}
These instructions have been tested on MacOS
{% endhint %}

## Setup & launch Airbyte

* Install Docker on your workstation \(see [instructions](https://www.docker.com/products/docker-desktop)\). Note: There is a known issue with docker-compose 1.27.3. If you are using that version, please upgrade to 1.27.4.
* Clone Airbyte's repository and run `docker compose`

```bash
# In your workstation terminal
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker-compose up
```

* In your browser, just visit [http://localhost:8000](http://localhost:8000)
* Start moving some data!

## Troubleshooting

If you encounter any issues, just connect to our [Slack](https://slack.airbyte.io). Our community will help!

