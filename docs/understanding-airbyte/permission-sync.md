# Airbyte Permission Sync

Permission Sync is a capability in Airbyte that allows you to transfer access control information and permission structures between systems. This document explains how Permission Sync works, which connectors support it, and how to use it.

## Overview

When transferring data between systems, it's often important to maintain not just the data itself but also the permission structures that govern access to that data. Permission Sync addresses this need by:

- Preserving user and group access controls.
- Maintaining role-based permissions.
- Transferring ownership information.
- Replicating sharing settings.

This ensures that when data is moved between systems, the appropriate access controls are maintained.

## How Permission Sync Works

When using Permission Sync:

1. The source connector extracts both data and associated permission metadata.
2. Permission structures are mapped between source and destination systems.
3. The destination connector applies compatible permission settings.
4. User and group mappings are maintained where possible.

Permission Sync can work alongside regular data synchronization or File Sync operations.

## Supported Connectors

Permission Sync is currently in early development with limited connector support. The following source connectors are planned to support Permission Sync:

### Sources

- Microsoft SharePoint (in development)
- Google Drive (planned)
- Box (planned)

### Destinations

Permission Sync uses standard record-type processing, making it compatible with all Airbyte destinations.

## Using Permission Sync

To use Permission Sync:

1. Configure a connection using a source and destination that both support Permission Sync.
2. Enable the Permission Sync option in the connection settings.
3. Configure user/group mapping if needed for cross-system synchronization.

### Configuration Example

When configuring a connection between Microsoft SharePoint (source) and S3 (destination):

1. Set up the SharePoint source with your tenant credentials.
2. Configure the S3 destination with your bucket information and IAM settings.
3. Enable Permission Sync in the advanced options.
4. Configure user mapping between SharePoint users and AWS IAM roles/users.

## Limitations

- Permission structures vary significantly between systems, so perfect mapping is not always possible.
- Some permission types may not have equivalents in destination systems.
- User and group identity mapping may require manual configuration.
- Permission Sync is most effective between systems with similar access control models.

## Technical Implementation

Permission Sync is implemented as an extension to the Airbyte protocol, allowing connectors to exchange permission metadata alongside regular data records. Connectors that support this feature have the `supportsPermissionSync: true` flag in their metadata.yaml file.

## Future Enhancements

The Permission Sync capability is being actively developed with plans to support more source and destination connectors. Future enhancements will include:

- More granular permission mapping options.
- Support for complex role-based access control (RBAC) systems.
- Automated user/group identity mapping.
- Audit logging for permission changes during sync.
