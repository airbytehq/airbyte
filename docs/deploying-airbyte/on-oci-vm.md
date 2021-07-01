Install Airbyte on Oracle Cloud Infrastructure (OCI) VM
-------------------------------------------------------

Create OCI Instance 
-------------------
Go to OCI Console > Compute > Instances > Create Instance

<img width="1665" alt="Screen Shot 2021-07-02 at 3 15 01 AM" src="https://user-images.githubusercontent.com/39692236/124164422-f6530780-dae3-11eb-802e-cabb29840df1.png">

<img width="1668" alt="Screen Shot 2021-07-02 at 3 18 04 AM" src="https://user-images.githubusercontent.com/39692236/124164566-25697900-dae4-11eb-82f5-2e86f5de2011.png">


Whitelist Port 8000 for a CIDR range in Security List of OCI VM Subnet
----------------------------------------------------------------------
Go to OCI Console > Networking > Virtual Cloud Network

Select the Subnet > Security List > Add Ingress Rules

<img width="1423" alt="Screen Shot 2021-07-02 at 3 22 30 AM" src="https://user-images.githubusercontent.com/39692236/124165247-e5ef5c80-dae4-11eb-9735-dbe748fa0531.png">






Login to the Instance/VM with the SSH key and 'opc' user
--------------------------------------------------------
chmod 600 private-key-file

ssh -i private-key-file opc@oci-private-instance-ip


Install docker
--------------

sudo yum update -y

sudo yum install -y docker

sudo service docker start

sudo usermod -a -G docker $USER


Install docker-compose
----------------------

sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

docker-compose --version


Install Airbyte
----------------

mkdir airbyte && cd airbyte

wget https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}

which docker-compose 

sudo /usr/local/bin/docker-compose up -d


Create SSH Tunnel to Login to the Instance
------------------------------------------

it is highly recommended to not have a Public IP for the Instance where you are running Airbyte)

From your local workstation

$ ssh -i private-key-file -L 8000:oci-private-instance-ip:8000 opc@bastion-host-public-ip

From your browser window https://localhost:8000/

/* Please note Airbyte currently does not support SSL/TLS certificates */
