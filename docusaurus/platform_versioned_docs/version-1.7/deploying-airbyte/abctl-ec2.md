---
products: oss-community
---

# Using an EC2 Instance with abctl

<!-- This topic has been preserved from the original Quickstart guide, unchanged. It may be used later in rewritten deployment docs. -->

This guide will assume that you are using the Amazon Linux distribution. However. any distribution that supports a docker engine should work with `abctl`. The launching and connecting to your EC2 Instance is outside the scope of this guide. You can find more information on how to launch and connect to EC2 Instances in the [Get started with Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html) documentation from Amazon.

1. Install the docker engine:

```shell
sudo yum install -y docker
```

2. Add the ec2-user (or whatever your distros default user) to the docker group:

```shell
sudo usermod -a -G docker ec2-user
```

3. Start and optionally enable (start on boot) the docker engine:

```shell
sudo systemctl start docker
sudo systemctl enable docker
```

4. Exit the shell and reconnect to the ec2 instance, an example would look like:

```shell
exit
ssh -i ec2-user-key.pem ec2-user@1.2.3.4
```

5. Download the latest version of abctl and install it in your path:

```shell
curl -LsfS https://get.airbyte.com | bash -
```

6. Run the `abctl` command and install Airbyte:
   :::tip
   By default, `abctl` only configures an ingress rule for the host `localhost`. In order to ensure that Airbyte can be accessed outside of the EC2 instance, you will need to specify the `--host` flag to the `local install` command, providing the FQDN of the host which is hosting Airbyte. For example, `abctl local install --host airbyte.company.example`.
   :::

By default, `abctl` will listen on port 8000. If port 8000 is already in used or you require a different port, you can specify this by passing the `--port` flag to the `local install` command. For example, `abctl local install --port 6598`

Ensure the security group configured for the EC2 Instance allows traffic in on the port (8000 by default, or whatever port was passed to `--port`) that you deploy Airbyte on. See the [Control traffic to your AWS resources using security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html) documentation for more information.

```shell
abctl local install --host [HOSTNAME]
```

## Running over HTTP

Airbyte suggest that you secure your instance of Airbyte using TLS. Running over plain HTTP allows attackers to see your
password over clear text. If you understand the risk and would still like to run Airbyte over HTTP, you must set
Secure Cookies to false. You can do this with `abctl` by passing the `--insecure-cookies` flag to `abctl`:

```shell
abctl local install --host [HOSTNAME] --insecure-cookies
```
