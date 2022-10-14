# bit.io

## Overview

bit.io is a serverless, shareable cloud Postgres database. 

## Endpoints

This destination connector uses the Postgres protocol. 

## Quick Notes

- bit.io doesn't support `CREATE DATABASE`

- This connectors primary change is to hardcode the hostname to `db.bit.io`, the port to `5432`, and the `sslmode` to `require`



