# On GCP \(Compute Engine\)



{% hint style="info" %}
The instructions have been tested on `Debian GNU/Linux 10 (buster)`
{% endhint %}

## Create a new instance

* Launch a new instance

![](../../.gitbook/assets/gcp_ce_launch.png)

* Configure new instance

![](../../.gitbook/assets/gcp_ce_configure.png)

* `Create`

## Install environment

{% hint style="info" %}
This part assumes that you have access to a terminal on your workstation
{% endhint %}

* Set variables in your terminal

```bash
w$ PROJECT_ID=PROJECT_ID_WHERE_YOU_CREATED_YOUR_INSTANCE
w$ INSTANCE_NAME=dataline # or anyother name that you've used
```

* Install `gcloud`

```bash
w$ # For MacOS with brew
w$ brew cask install google-cloud-sdk
w$ gcloud init # Follow instructions
w$ # Verify you can see your instance
w$ gcloud --project $PROJECT_ID compute instances list
[...] # You should see the dataline instance you just created
```

* Connect to your instance

```bash
w$ gcloud --project=$PROJECT_ID beta compute ssh dataline
```

* Install `docker`

```
:~$ sudo apt-get update
:~$ sudo apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common
:~$ curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add --
:~$ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian buster stable"
:~$ sudo apt-get update
:~$ sudo apt-get install -y docker-ce docker-ce-cli containerd.io
:~$ sudo usermod -a -G docker $USER
```

* Install `docker-compose`

```bash
:~$ sudo apt-get -y install wget
:~$ sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose
:~$ sudo chmod +x /usr/local/bin/docker-compose
:~$ docker-compose --version
```

* Close the ssh connection to ensure the group modification is taken into account

```bash
:~$ logout
```

## Install & Start Dataline

* Connect to your instance

```bash
w$ gcloud --project=$PROJECT_ID beta compute ssh dataline
```

* Install Dataline

```bash
:~$ mkdir dataline && cd dataline
:~$ wget https://raw.githubusercontent.com/datalineio/dataline/master/{.env,docker-compose.yaml}
:~$ docker-compose up -d
```

## Connect to Dataline

{% hint style="danger" %}
For security reason we strongly recommend to not expose Dataline on Internet available ports. Future versions will add support for SSL & Authentication
{% endhint %}

* Create ssh tunnel

```bash
w$ gcloud --project=$PROJECT_ID beta compute ssh dataline -- -L 8000:localhost:8000 -L 8001:localhost:8001 -N -f
```

* In your browser, just visit [http://localhost:8000](http://localhost:8000)
* Start moving some data!

## Troubleshooting

If you encounter any issues, just connect to our [slack](https://join.slack.com/t/datalinehq/shared_invite/zt-h5m88w3a-twQ_6AF9e8SnAzOIkHu2VQ). Our community will help!

