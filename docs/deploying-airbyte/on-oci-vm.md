# On Oracle Cloud Infrastructure VM

Install Airbyte on Oracle Cloud Infrastructure VM running Oracle Linux 7

## Create OCI Instance

Go to OCI Console &gt; Compute &gt; Instances &gt; Create Instance

![](../.gitbook/assets/OCIScreen1.png)

![](../.gitbook/assets/OCIScreen2.png)

Deploy it in a VCN which has a Private subnet. Ensure you select shape as 'Intel' 

## Whitelist Port 8000 for a CIDR range in Security List of OCI VM Subnet

Go to OCI Console &gt; Networking &gt; Virtual Cloud Network

Select the Subnet &gt; Security List &gt; Add Ingress Rules

![](../.gitbook/assets/OCIScreen3.png)

### Connection Method 1 : Create SSH Tunnel via a Bastion Host to Login to the Instance 

Keep in mind that it is highly recommended to not have a Public IP for the Instance where you are running Airbyte.

#### SSH Local Port Forward to Airbyte VM

On your local workstation:

```text
ssh opc@bastion-host-public-ip -i <private-key-file.key> -L 2200:oci-private-instance-ip:22
ssh opc@localhost -i <private-key-file.key> -p 2200
```

### Connection Method 2 : Create OCI Bastion Host Service to Login to the Instance 

![OCIScreen13](https://user-images.githubusercontent.com/39692236/142787487-71d464de-38ec-4198-944a-328ccc1a0906.png)


#### Create Bastion Host Service from OCI Console
<img width="1257" alt="OCIScreen5" src="https://user-images.githubusercontent.com/39692236/142786778-99925599-1b68-444a-be76-2a57bd74b5e2.png">


#### Create Port forwarding SSH Session from Bastion Service
<img width="1251" alt="OCIScreen6" src="https://user-images.githubusercontent.com/39692236/142786791-4e6ef40c-bfe5-4b51-88ea-6d72f149c849.png">


#### Create SSH port forwarding session on Local machine 

```text
ssh -i <privateKey> -N -L <localPort>:10.10.1.25:22 -p 22 ocid1.bastionsession.oc1.ap-sydney-1.amaaaaaaqcins5yaf6gzqsp5beaikpg4mczr445uberbrsvj7rmsd73wtiua@host.bastion.ap-sydney-1.oci.oraclecloud.com
```
<img width="945" alt="OCIScreen7" src="https://user-images.githubusercontent.com/39692236/142786799-04f148c3-130e-4ec5-b5ed-799c8bc8e449.png">
<img width="1117" alt="OCIScreen8" src="https://user-images.githubusercontent.com/39692236/142786805-41efb983-70cc-41f0-8799-e0847bea7014.png">



### Login to Airbyte Instance using Port forwarding session from Local machine 

```text
 ssh -i mydemo_vcn.priv opc@localhost -p 2222
```

<img width="861" alt="OCIScreen9" src="https://user-images.githubusercontent.com/39692236/142786815-41c37189-6ab8-4dc0-b4ad-3187ecd0ec5e.png">



## Install Airbyte Prerequisites on OCI VM

### Install Docker

```text
sudo yum update -y

sudo yum install -y docker

sudo service docker start

sudo usermod -a -G docker $USER
```


### Install Docker Compose

```text
sudo wget https://github.com/docker/compose/releases/download/1.26.2/docker-compose-$(uname -s)-$(uname -m) -O /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

sudo /usr/local/bin/docker-compose --version
```


### Install Airbyte

```text
mkdir airbyte && cd airbyte

wget https://raw.githubusercontent.com/airbytehq/airbyte/master/{.env,docker-compose.yaml}

which docker-compose

sudo /usr/local/bin/docker-compose up -d
```

### Airbyte URL Access Method 1 : Local Port Forward to Airbyte VM using Bastion host

```text
ssh opc@bastion-host-public-ip -i <private-key-file.key> -L 8000:oci-private-instance-ip:8000
```

### Access Airbyte

Open URL in Browser : [http://localhost:8000/](http://localhost:8000/)

![](../.gitbook/assets/OCIScreen4.png)

### Airbyte URL Access Method 2 : Local Port Forward to Airbyte VM using OCI Bastion Service

#### Create port-forwarding session to Port 8000
<img width="1251" alt="OCIScreen10" src="https://user-images.githubusercontent.com/39692236/142786987-4c28a846-e3ad-432b-972b-2fd75149d2f6.png">


```text
ssh -i <privateKey> -N -L <localPort>:10.10.1.25:8000 -p 22 ocid1.bastionsession.oc1.ap-sydney-1.amaaaaaaqcins5yadwmzsm7ogtij3kscsqjkuw6d5cjs4csoe2luzlmra62q@host.bastion.ap-sydney-1.oci.oraclecloud.com
```

#### Open port-forwarding tunnel to Port 8000 and connect from browser

```text
ssh -i mydemo_vcn.priv -N -L 8000:10.10.1.25:8000 -p 22 ocid1.bastionsession.oc1.ap-sydney-1.amaaaaaaqcins5yadwmzsm7ogtij3kscsqjkuw6d5cjs4csoe2luzlmra62q@host.bastion.ap-sydney-1.oci.oraclecloud.com
```

<img width="953" alt="OCIScreen11" src="https://user-images.githubusercontent.com/39692236/142787127-1bafdb58-31d0-4930-ae3b-d4092855f35c.png">
<img width="1108" alt="OCIScreen12" src="https://user-images.githubusercontent.com/39692236/142787129-4c60df47-ad01-4db8-a2f8-53cc2a76e07d.png">


### Access Airbyte

Open URL in Browser : [http://localhost:8000/](http://localhost:8000/)

![](../.gitbook/assets/OCIScreen4.png)

/ _Please note Airbyte currently does not support SSL/TLS certificates_ /


