# Jenkins Blue Ocean
This page contains the setup guide and reference information for the Jenkins Blue Ocean source connector.

## Overview

The Jenkins Blue Ocean plugin uses the [Jenkins Blue Ocean](https://plugins.jenkins.io/blueocean-rest/)
to pull data from Jenkins. This has a different structure than the alternative Jenkins connector source.

If you use mostly Jenkins Pipeline style projects, this connector may be better suited.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The Jenkins Blue Ocean source should not run into Jenkins API limitations under normal usage.

## Getting started

### Requirements

* Jenkins Server
* Jenkins User
* Jenkins API Token

## Setup guide

### Create your Jenkins API Token

1. Log into your Jenkins system.
2. Click on your username in the top right.
3. On the left, click "Configure".
4. In the "API Token" section, click "Add new Token", give the token a name, and click "Generate".
5. Copy the generated token for later.


## Supported sync modes

The Jenkins Blue source connector supports incremental sync modes for Runs, Nodes, and Steps. These three sources are
processed hierarchically, and should all have the same sync mode. In general, you probably want incremental sync mode
for Runs, Nodes, and Steps.

NOTE: The Nodes and Steps streams rely on the incremental sync mode of the Runs stream.

## Changelog

| Version | Date       | Pull Request | Subject                                                                                                      |
|:--------|:-----------| :--- |:-------------------------------------------------------------------------------------------------------------|
## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |

