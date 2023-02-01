# Getting Started

## Summary

This is a step-by-step guide for how to create an Airbyte source in Python to read data from an HTTP API. We'll be using the Exchange Rates API as an example since it is simple and demonstrates a lot of the capabilities of the CDK.

## Requirements

* Python &gt;= 3.9
* Docker
* NodeJS \(only used to generate the connector\). We'll remove the NodeJS dependency soon.

All the commands below assume that `python` points to a version of python &gt;=3.9.0. On some systems, `python` points to a Python2 installation and `python3` points to Python3. If this is the case on your machine, substitute all `python` commands in this guide with `python3`.

## Exchange Rates API Setup

For this guide we will be making API calls to the Exchange Rates API. In order to generate the API access key that will be used by the new connector, you will have to follow steps on the [Exchange Rates API](https://exchangeratesapi.io/) by signing up for the Free tier plan. Once you have an API access key, you can continue with the guide.

## Checklist

* Step 1: Create the source using the template
* Step 2: Install dependencies for the new source
* Step 3: Define the inputs needed by your connector
* Step 4: Implement connection checking
* Step 5: Declare the schema of your streams
* Step 6: Implement functionality for reading your streams
* Step 7: Use the connector in Airbyte
* Step 8: Write unit tests or integration tests

Each step of the Creating a Source checklist is explained in more detail in the following steps. We also mention how you can submit the connector to be included with the general Airbyte release at the end of the tutorial.

