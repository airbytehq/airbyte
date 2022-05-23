# SFTP

## Overview

The Airbyte SFTP source allows you to sync data from server via SFTP type connection

### Sync overview

#### Output schema

Each specified file will be output into a stream.

Currently, this connector only reads data with JSON and CSV format. More formats \(e.g. Apache Avro\) will be supported in the future.

#### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
|:--------------------------|:---------------------| :--- |
| Full Refresh Sync         | Yes                  |  |
| Incremental - Append Sync | No                   |  |
| Namespaces                | No                   |  |
| Username-Password Authentication  | Yes          |  |
| Public Key Authentication | Yes                  |  |

## Getting started

### Requirements

To use the SFTP source, you'll need:

* The Server which supports SFTP type connection

### Setup guide

#### **Setting Up Public Key Authentication for SSH**

The following simple steps are required to set up public key authentication (for SSH):

Key pair is created (typically by the user). This is typically done with ssh-keygen.
Private key stays with the user (and only there), while the public key is sent to the server. Typically with the ssh-copy-id utility.
Server stores the public key (and "marks" it as authorized).
Server will now allow access to anyone who can prove they have the corresponding private key.


## Changelog

| Version | Date       | Pull Request                                           | Subject      |
|:--------|:-----------| :------------------------------------------------------|:-------------|
| 0.1.0   | 2021-23-05 |  | Init version |
