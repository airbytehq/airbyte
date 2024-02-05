# Personio

## Overview

Personio is a software for human resources management.

This connector is built by [TechDivision](https://www.techdivision.com/) and uses the [Personio API](https://developer.personio.de/reference) to fetch data from the following streams:
- employees
- time-offs
- attributes
- projects
- attendances
- time-off-types
- absence-periods

For further information about the specific endpoints, please refer to the [Personio API](https://developer.personio.de/reference).

## Getting started

### Requirements

To create a personio connector, you will need the following:
- Personio Client ID
- Personio Client Secret
- (optional) Start-Date for the `time-offs` stream

## Changelog

| Version | Date       | Pull Request | Subject                                            |  
|---------|------------| ------------ | -------------------------------------------------- |  
| 0.58.0  | 2024-02-02 |              | Start Publishing-Process Personio Source Connector |