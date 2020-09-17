# Source Name

## Overview 

### Sync Overview
#### Resulting schema
Is the schema changed or altered in any way? If so, mention how. 

Does this source have a fixed schema? (e.g: SaaS API like ExchangeRateIO) if so, point to the schema or include it here directly

#### Data Type Mapping
This section should contain a table mapping each of the source's data types to Dataline types. At the moment, 
Dataline uses the same types used by Singer.

| Source Type | Dataline Type | Notes
|-----|-----|-----|

Currently, Dataline uses the same types as Singer: `string`, `int`, `number`, `boolean`, `object`. 
#### Features
This section should contain a table with the following format:

| Feature| Supported?(Yes/No) | Notes | 
|------|-----| ---- |
| Full Refresh Sync |  | 
| Incremental Sync |  | 
| Replicate deletes |  | 
| For databases, WAL/Logical replication |  |  
| SSL connection |  | 
| SSH Tunnel Support |  | 
| (Any other source-specific features) |  |  

#### Performance considerations
Could this source hurt the user's data source or put too much strain on it in certain circumstances? For example, 
if there are a lot of tables or rows in a table? What is the breaking point (e.g: 100mm> records)? What can the user 
do to prevent this? (e.g: use a read-only replica, or schedule frequent syncs, etc..)  


## Getting Started

### Requirements: 
* What versions of this source does this implementation support? (e.g: `postgres v3.14 and above`) 
* What configurations, if any, are required on the source? (e.g: `buffer_size > 1024`)
* Network accessibility requirements
* Credentials/authentication requirements? (e.g: A  DB user with read permissions on certain tables) 

### Setup Guide
For each of the above high-level requirements as appropriate, add or point to a follow-along guide. See the Postgres source guide for an example. 

For each major cloud provider we support, also add a follow-along guide for setting up Dataline to connect to that destination. 
See the Postgres destination guide for an example of what this should look like.  
