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

