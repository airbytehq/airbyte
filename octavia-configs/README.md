# Octavia: Configuration As Code.

We manage all the Airbyte configuration from this folder.

## Prerequisetes to run Octavia Commands:
- Docker
- the `airbyte.pem` ssh key to be able connect to the EC2 instance where Airbyte is running. If you dont have it, you can get the key from LastPass and then copy it to a file called `~/.ssh/airbyte.pem`

## How to run Octavia commands:

- Install Octavia by running:
```
make install_octavia
```

- To be able to reach the Airbyte UI, you need to Forward the 8000 port of the EC2 instance where it is running. To do so, run:
```
make forward_ec2_port
```

Now you are ready to start running Octavia Commands. Refer to the [official documentation](https://github.com/airbytehq/airbyte/blob/master/octavia-cli/README.md) in case of questions: 