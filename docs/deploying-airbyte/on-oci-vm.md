# Install Airbyte on Oracle Cloud Infrastructure (OCI) VM

Install Airbyte on Oracle Cloud Infrastructure VM running Oracle Linux 7

## Create OCI Instance 
Go to OCI Console > Compute > Instances > Create Instance

![](../.gitbook/assets/OCIScreen1.png)

![](../.gitbook/assets/OCIScreen2.png)


## Whitelist Port 8000 for a CIDR range in Security List of OCI VM Subnet
Go to OCI Console > Networking > Virtual Cloud Network

Select the Subnet > Security List > Add Ingress Rules

![](../.gitbook/assets/OCIScreen3.png)


## Login to the Instance/VM with the SSH key and 'opc' user
```
chmod 600 private-key-file

ssh -i private-key-file opc@oci-private-instance-ip -p 2200
```

## Install Airbyte Prerequisites on OCI VM

### Install Docker

sudo yum update -y

sudo yum install -y docker

sudo service docker start

sudo usermod -a -G docker $USER


### Install Docker Compose

sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

docker-compose --version


### Install Airbyte

mkdir airbyte && cd airbyte

wget https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}

which docker-compose 

sudo /usr/local/bin/docker-compose up -d



## Create SSH Tunnel to Login to the Instance

it is highly recommended to not have a Public IP for the Instance where you are running Airbyte). 

### SSH Local Port Forward to Airbyte VM

From your local workstation

```
ssh opc@bastion-host-public-ip -i <private-key-file.key> -L 2200:oci-private-instance-ip:22
ssh opc@localhost -i <private-key-file.key> -p 2200
```

### Airbyte GUI Local Port Forward to Airbyte VM

```
ssh opc@bastion-host-public-ip -i <private-key-file.key> -L 8000:oci-private-instance-ip:8000
```


## Access Airbyte

Open URL in Browser :  http://localhost:8000/

![](../.gitbook/assets/OCIScreen4.png)

/* Please note Airbyte currently does not support SSL/TLS certificates */
