# On GCP \(Compute Engine\)

{% hint style="info" %}
The instructions have been tested on `Debian GNU/Linux 10 (buster)`
{% endhint %}

## Create a new instance

* Launch a new instance

![](../.gitbook/assets/gcp_ce_launch%20%281%29%20%281%29.png)

* Configure new instance

![](../.gitbook/assets/gcp_ce_configure%20%281%29%20%281%29.png)

* `Create`

## Install environment

{% hint style="info" %}
This part assumes that you have access to a terminal on your workstation
{% endhint %}

* Set variables in your terminal

```bash
# In your workstation terminal
PROJECT_ID=PROJECT_ID_WHERE_YOU_CREATED_YOUR_INSTANCE
INSTANCE_NAME=airbyte # or anyother name that you've used
```

* Install `gcloud`

{% tabs %}
{% tab title="MacOS" %}
```bash
# In your workstation terminal
brew cask install google-cloud-sdk
gcloud init # Follow instructions
```
{% endtab %}

{% tab title="Ubuntu" %}
```bash
# FIXME
```
{% endtab %}
{% endtabs %}

```bash
# Verify you can see your instance
gcloud --project $PROJECT_ID compute instances list
[...] # You should see the airbyte instance you just created
```

* Connect to your instance

```bash
# In your workstation terminal
gcloud --project=$PROJECT_ID beta compute ssh airbyte
```

* Install `docker`

```bash
# In your ssh session on the instance terminal
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg2 software-properties-common
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add --
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian buster stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo usermod -a -G docker $USER
```

* Install `docker-compose`

```bash
# In your ssh session on the instance terminal
sudo apt-get -y install wget
sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

* Close the ssh connection to ensure the group modification is taken into account

```bash
# In your ssh session on the instance terminal
logout
```

## Install & start Airbyte

* Connect to your instance

```bash
# In your workstation terminal
gcloud --project=$PROJECT_ID beta compute ssh airbyte
```

* Install Airbyte

```bash
# In your ssh session on the instance terminal
mkdir airbyte && cd airbyte
wget https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}
docker-compose up -d
```

## Connect to Airbyte

{% hint style="danger" %}
For security reasons, we strongly recommend to not expose Airbyte publicly. Future versions will add support for SSL & Authentication.
{% endhint %}

* Create ssh tunnel.

```bash
# In your workstation terminal
gcloud --project=$PROJECT_ID beta compute ssh airbyte -- -L 8000:localhost:8000 -L 8001:localhost:8001 -N -f
```

* Just visit [http://localhost:8000](http://localhost:8000) in your browser and start moving some data!

## Troubleshooting

If you encounter any issues, just connect to our [Slack](https://slack.airbyte.io). Our community will help!

