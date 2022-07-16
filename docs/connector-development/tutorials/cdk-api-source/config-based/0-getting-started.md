# Getting Started

## Summary

Throughout this tutorial, we'll walk you through the creation an Airbyte source to read data from an HTTP API.

We'll build a connector reading data from the Exchange Rates API, but the steps we'll go through will apply to other HTTP APIs you might be interested in integrating with.

## Exchange Rates API Setup

Before we can get started, you'll need to generate an API access key for the Exchange Rates API.
This can be done by signing up for the Free tier plan on [Exchange Rates API](https://exchangeratesapi.io/).

## Requirements

- Python >= 3.9
- Docker
- NodeJS

All the commands below assume that `python` points to a version of python &gt;=3.9.0. On some systems, `python` points to a Python2 installation and `python3` points to Python3. If this is the case on your machine, substitute all `python` commands in this guide with `python3`.

## Next Steps

Next, we'll [create a Source using the connector generator.](./1-create-source.md)