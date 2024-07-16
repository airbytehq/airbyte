---
products: oss-community, oss-enterprise
---

# Amazon Web Services (AWS)

Airbyte supports Amazon Web Services as a Cloud Provider. There are several ways that you can deploy Airbyte using AWS.

You can use the AWS managed Kubernetes solution EKS, using `abctl` on an EC2 instance, or on a Kubernetes distribution
that has been deployed on EC2 instances.

## Policies

You will need to create an AWS Role and associate that Role with either an AWS User when using Access Credentials, or an
Instance Profile or Kubernetes Service Account when using IAM Roles for Service Accounts. That Role will need the 
following policies depending on in for integrate with S3 and AWS Secret Manager respectively.

### AWS S3 Policy

The [following policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/example-policies-s3.html#iam-policy-ex0), allow the cluster to communicate with S3 storage

```yaml
{
  "Version": "2012-10-17",
  "Statement":
    [
      { "Effect": "Allow", "Action": "s3:ListAllMyBuckets", "Resource": "*" },
      {
        "Effect": "Allow",
        "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
        "Resource": "arn:aws:s3:::YOUR-S3-BUCKET-NAME",
      },
      {
        "Effect": "Allow",
        "Action":
          [
            "s3:PutObject",
            "s3:PutObjectAcl",
            "s3:GetObject",
            "s3:GetObjectAcl",
            "s3:DeleteObject",
          ],
        "Resource": "arn:aws:s3:::YOUR-S3-BUCKET-NAME/*",
      },
    ],
}
```

### AWS Secret Manager Policy

The [following policies](https://docs.aws.amazon.com/mediaconnect/latest/ug/iam-policy-examples-asm-secrets.html), allow the cluster to communicate with AWS Secret Manager

```yaml
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:CreateSecret",
                "secretsmanager:ListSecrets",
                "secretsmanager:DescribeSecret",
                "secretsmanager:TagResource",
                "secretsmanager:UpdateSecret"
            ],
            "Resource": [
                "*"
            ],
            "Condition": {
                "ForAllValues:StringEquals": {
                    "secretsmanager:ResourceTag/AirbyteManaged": "true"
                }
            }
        }
    ]
}
```

## Using an EC2 Instance with abctl

This guide will assume that you are using the Amazon Linux distribution. However. any distribution that supports a docker engine should work with `abctl`. The launching and connecting to your EC2 Instance is outside the scope of this guide. You can find more information on how to launch and connect to EC2 Instances in the [Get started with Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html) documentation from Amazon.

:::tip
`abctl` runs by default on port 8000. You can change the port by passing the `--port` flag to the `local install` command. Make sure that the security group that you have configured for the EC2 Instance allows traffic in on the port that you deploy Airbyte on. See the [Control traffic to your AWS resources using security groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html) documentation for more information.
:::


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

```shell
abctl local install
```

### Editing the Ingress

By default `abctl` will install and Nginx Ingress and set the host name to `localhost`. You will need to edit this to 
match the host name that you have deployed Airbyte to. To do this you will need to have the `kubectl` command installed
on your EC2 Instance and available on your path.

If you do not already have the CLI tool kubectl installed, please [follow these instructions to install](https://kubernetes.io/docs/tasks/tools/).

Then you can run `kubectl edit ingress -n airbyte-abctl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig` and edit the `host` 
key under the spec.rules section of the Ingress definition. The host should match the FQDN name that you are trying to 
host Airbyte at, for example: `airbyte.company.example`.

## Using an ALB for Ingress

The recommended method for Cluster Ingress is an AWS ALB. The [Ingress](../integrations/ingress) section of the documentation
shows how to configure the Kubernetes Ingress using the AWS Load Balancer Controller. This assumes that you have already
correctly configured your Cluster with the AWS Load Balancer Controller. This configuration is outside the scope of this
documentation. You can find more information on how to correctly configure an ALB Ingress Controller by reading the official 
[Route application and HTTP traffic with Application Load Balancers](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html) 
documentation provided by Amazon.

Once the AWS Load Balancer Controller has been correctly installed the Airbyte installation process will be able to 
automatically create an ALB for you. You can combine the ALB with AWS Certificate Manager (ACM) to secure your instance 
with TLS. The ACM documentation can be found here: [Getting Started with AWS Certificate Manager](https://aws.amazon.com/certificate-manager/getting-started/).
To use the ACM certificate, you can specify the certificate-arn when creating the Kubernetes Ingress. For more information
see the [Kubernetes Ingress Annotations documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.1/guide/ingress/annotations/#certificate-arn).