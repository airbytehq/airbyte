# Developing an SSH Connector

## Goal

Easy development of any connector that needs the ability to connect to a resource via SSH Tunnel.

## Overview

Our SSH connector support is designed to be easy to plug into any existing connector. There are a few major pieces to consider:

1. Add SSH Configuration to the Spec - for SSH, we need to take in additional configuration, so we need to inject extra fields into the connector configuration.
2. Add SSH Logic to the Connector - before the connector code begins to execute we need to start an SSH tunnel. This library provides logic to create that tunnel (and clean it up).
3. Acceptance Testing - it is a good practice to include acceptance testing for the SSH version of a connector for at least one of the SSH types (password or ssh key). While unit testing for the SSH functionality exists in this package (coming soon), high-level acceptance testing to make sure this feature works with the individual connector belongs in the connector.

## How To

### Add SSH Configuration to the Spec

1. The `SshHelpers` class provides 2 helper functions that injects the SSH configuration objects into a spec JsonSchema for an existing connector. Usually the `spec()` method for a connector looks like `Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);`. These helpers are just injecting the ssh spec (`ssh-tunnel-spec.json`) into that spec.
2. You may need to update tests to reflect that new fields have been added to the spec. Usually updating the tests just requires using these helpers in the tests.

### Add SSH Logic to the Connector

1. This package provides a Source decorated class to make it easy to add SSH logic to an existing source. Simply pass the source you want to wrap into the constructor of the `SshWrappedSource`. That class also requires two other fields: `hostKey` and `portKey`. Both of these fields are pointers to fields in the connector specification. The `hostKey` is a pointer to the field that hold the host of the resource you want to connect and `portKey` is the port. In a simple case, where the host name for a connector is just defined in the top-level `host` field, then `hostKey` would simply be: `["host"]`. If that field is nested, however, then it might be: `["database", "configuration", "host"]`.

### Acceptance Testing

1. The only difference between existing acceptance testing and acceptance testing with SSH is that the configuration that is used for testing needs to contain additional fields. You can see the `Postgres Source ssh key creds` in lastpass to see an example of what that might look like. Those credentials leverage an existing bastion host in our test infrastructure. (As future work, we want to get rid of the need to use a static bastion server and instead do it in docker so we can run it all locally.)

## Misc

### How to wrap the protocol in an SSH Tunnel

For `spec()`, `check()`, and `discover()` wrapping the connector in an SSH tunnel is easier to think about because when they return all work is done and the tunnel can be closed. Thus, each of these methods can simply be wrapped in a try-with-resource of the SSH Tunnel.

For `read()` and `write()` they return an iterator and consumer respectively that perform work that must happen within the SSH Tunnel after the method has returned. Therefore, the `close` function on the iterator and consumer have to handle closing the SSH tunnel; the methods themselves cannot just be wrapped in a try-with-resource. This is handled for you by the `SshWrappedSource`, but if you need to implement any of this manually you must take it into account.

### Name Mangling

One of the least intuitive pieces of the SSH setup to follow is the replacement of host names and ports. The reason `SshWrappedSource` needs to know how to get the hostname and port of the database you are trying to connect to is that when it builds the SSH tunnel that forwards to the database, it needs to know the hostname and port so that the tunnel forwards requests to the right place. After the SSH tunnel is established and forwarding to the database, the connector code itself runs.

There's a trick here though! The connector should NOT try to connect to the hostname and port of the database. Instead, it should be trying to connect to `localhost` and whatever port we are forwarding to the database. The `SshTunnel#sshWrap` removes the original host and port from the configuration for the connector and replaces it with `localhost` and the correct port. So from the connector code's point of view it is just operating on localhost.

There is a tradeoff here.

- (Good) The way we have structured this allows users to configure a connector in the UI in a way that it is intuitive to user. They put in the host and port they think about referring to the database as (they don't need to worry about any of the localhost version).
- (Good) The connector code does not need to know anything about SSH, it can just operate on the host and port it gets (and we let SSH Tunnel handle swapping the names for us) which makes writing a connector easier.
- (Bad) The downside is that the `SshTunnel` logic is more complicated because it is absorbing all of this name swapping so that neither user nor connector developer need to worry about it. In our estimation, the good outweighs the extra complexity incurred here.

### Acceptance Testing via ssh tunnel using SshBastion and JdbcDatabaseContainer in Docker

1. The `SshBastion` class provides 3 helper functions:
   `initAndStartBastion()`to initialize and start SSH Bastion server in Docker test container and creates new `Network` for bastion and tested jdbc container
   `getTunnelConfig()`which return JsoneNode with all necessary configuration to establish ssh tunnel. Connection configuration for integration tests is now taken directly from container settings and does not require a real database connection
   `stopAndCloseContainers` to stop and close SshBastion and JdbcDatabaseContainer at the end of the test

## Future Work

- Add unit / integration testing for `ssh` package.
- Restructure spec so that instead of having `SSH Key Authentication` or `Password Authentication` options for `tunnel_method`, just have an `SSH` option and then within that `SSH` option have a `oneOf` for password or key. This is blocked because we cannot use `oneOf`s nested in `oneOf`s.
- Improve the process of acceptance testing by allowing doing acceptance testing using a bastion running in a docker container instead of having to use dedicated infrastructure and a static database.
