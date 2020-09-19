# On your workstation

{% hint style="info" %}
These instructions have been tested on MacOS
{% endhint %}

## Setup & Launch Airbyte

* Install docker on your workstation \(see [instructions](https://www.docker.com/products/docker-desktop)\)
* Clone airbyte's repository and run `docker compose`

```bash
# In your workstation terminal
git clone git@github.com:airbytehq/airbyte.git
cd airbyte
VERSION=dev docker-compose up -d
```

* In your browser, just visit [http://localhost:8000](http://localhost:8000)
* Start moving some data!

## Troubleshooting

If you encounter any issues, just connect to our [slack](https://slack.airbyte.io). Our community will help!

