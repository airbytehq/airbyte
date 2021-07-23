# SSH Tunnel Testing

This directory creates infrastructure for testing ssh tunneling to
databases for airbyte connectors.  It sets up:

* a public subnet (for a bastion host)
* a private subnet (for postgres)
* a security group (for the bastion host)
* a bastion host reachable from the internet, with ssh tunnel support
* a user account on the bastion host
* a postgres database on a private address

All infrastructure for this is kept separate from other airbyte 
infrastructure, as it's meant to simulate a client's corporate
environment and private databases.

## Public Keys

The bastion host requires an ec2-user (always) and preferably also a non-root capable
user named airbyte.  The airbyte user is used for ssh tunnel from the connectors, and should not be a priviledged user.

To create a fresh ssh keypair and set its comment (where the email usually shows), use a command like this:

    ssh-keygen -t rsa -f dbtunnel-bastion-ec2-user_rsa -C ec2-user
    ssh-keygen -t rsa -f ~/dbtunnel-bastion-airbyte_rsa -C airbyte

The public key from that is used for ec2 instance creation, but the private key should be kept secret.

TODO: The airbyte user might also need to usable with a password; check this from the connector side.


