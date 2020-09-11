# On AWS \(EC2\)

## Pre-requisites

* Create a new instance or use an existing instance
* The instance **must** have access to the internet
* The instance **must** have these two ports open \(using security groups\):
  * `8000` \(webapp\)
  * `8001` \(API\)
* You **must** have an `ssh` access
* You **must** have `docker` installed

```
$ sudo yum update -y
$ sudo yum install docker
$ sudo service docker start
$ sudo usermod -a -G docker $USER
$ logout # necessary for the group change to take effect
```

* You **must** have `docker-compose` installed

```bash
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

