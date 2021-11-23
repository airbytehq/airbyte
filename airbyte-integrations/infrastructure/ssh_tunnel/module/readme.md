# SSH Tunnel Testing

This directory creates infrastructure for testing ssh tunneling to
databases for airbyte connectors.  It sets up:

* a public subnet (for a bastion host and one postgres AZ)
* a private subnet (for postgres secondary AZ that aws insists on)
* two security groups (for the bastion host, for the postgres server)
* a bastion host reachable from the internet, with ssh tunnel support
* a user account on the bastion host
* a postgres database on a private address

All infrastructure for this is kept separate from other airbyte 
infrastructure, as it's meant to simulate a client's corporate
environment and private databases.

This configuration uses the 'tfenv' wrapper on terraform for versioning.
Each directory contains a .terraform-version file specifying the compatibility
for that terraform instance.

    brew install tfenv  # install
    terraform plan      # should use the tfenv wrapper's version of terraform


## Public Keys

The bastion host requires an ec2-user (always) and preferably also a non-root capable
user named airbyte.  The airbyte user is used for ssh tunnel from the connectors, and should not be a 
priviledged user.  These are in the integration test secrets store under the 'infra' prefix.

To create a fresh ssh keypair and set its comment (where the email usually shows), use a command like this:

    ssh-keygen -t rsa -f dbtunnel-bastion-ec2-user_rsa -C ec2-user
    ssh-keygen -t rsa -f ~/dbtunnel-bastion-airbyte_rsa -C airbyte

The public key from that is used for ec2 instance creation, but the private key should be kept secret.

TODO: The airbyte user will also need password auth allowed on the ssh connection, once we're ready for that.

## Database Setup

We don't have yet automation for running the database configuration scripts
from infrastructure as code.  The sql scripts included should be run once by hand
when setting up from scratch.  Note that the sql script creating a user has a place to
manually change the password.

