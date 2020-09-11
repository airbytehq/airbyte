# On GCP \(Compute Engine\)

## Pre-requisites

{% hint style="info" %}
The instructions have been tested on `Debian GNU/Linux 10 (buster)`
{% endhint %}

* Create a new instance or use an existing instance 
* The instance **must** have access to the internet
* The instance **must** have these two ports open \(using security groups\):
  * `8000` \(webapp\)
  * `8001` \(API\)
* You **must** have an `ssh` access
* You **must** have `docker` installed

```
$ sudo apt-get update
$ sudo apt-get install apt-transport-https ca-certificates curl gnupg2 software-properties-common
$ curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add --
$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian buster stable"
$ sudo apt-get update
$ sudo apt-get install docker-ce docker-ce-cli containerd.io
$ sudo usermod -a -G docker $USER
$ logout # necessary for the group change to take effect
```

* You **must** have `docker-compose` installed

```bash
$ sudo apt-get install wget
$ sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose
$ sudo chmod +x /usr/local/bin/docker-compose
$ docker-compose --version
```

## Start Dataline

```bash
$ mkdir dataline && cd dataline
$ wget https://raw.githubusercontent.com/datalineio/dataline/master/{.env,docker-compose.yaml}
$ docker-compose up
```

You can now connect to your instance public IP on port `8000`

## Troubleshooting

If you encounter any issues, just connect to our [slack](https://join.slack.com/t/datalinehq/shared_invite/zt-h5m88w3a-twQ_6AF9e8SnAzOIkHu2VQ). Our community will help!

