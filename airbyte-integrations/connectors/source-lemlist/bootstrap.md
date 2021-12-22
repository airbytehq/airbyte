# Lemlist

## API Reference

API Docs: https://developer.lemlist.com/#introduction

## Overview

Lemlist is your sales automation and cold email software. Using its API you can retrieve information about campaigns, activities and unsubscribes. 

- Lemlist API uses Basic Authentication.
- Pagination is offset-based.
- It uses fixed-window rate limiting strategy.

## Endpoints

Lemlist API consists of four endpoints which can be extracted data from:

 1. **Team**: This endpoint retrieves information of your team.
 2. **Campaigns**: This endpoint retrieves the list of all campaigns.
 3. **Activities**: This endpoint retrieves the last 100 activities.
 4. **Unsubscribes**: This endpoint retrieves the list of all people who are unsubscribed.

## Notes

- The API doesn't have any way to filter information so it doesn't support incremental syncs.
