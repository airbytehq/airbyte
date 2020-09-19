# On your workstation

{% hint style="info" %}
These instructions have been tested on MacOS
{% endhint %}

## Setup & Launch Airbyte

* Install docker on your workstation \(see [instructions](https://www.docker.com/products/docker-desktop)\)
* Clone airbyte's repository and run `docker compose`

```bash
# In your workstation terminal
git clone git@github.com:airbyteio/airbyte.git
cd airbyte
VERSION=dev docker-compose up -d
```

* In your browser, just visit [http://localhost:8000](http://localhost:8000)
* Start moving some data!

## Troubleshooting

If you encounter any issues, just connect to our [slack](https://join.slack.com/t/airbytehq/shared_invite/zt-h5m88w3a-twQ_6AF9e8SnAzOIkHu2VQ). Our community will help!

