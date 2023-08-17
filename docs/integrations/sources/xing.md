# Xing

## Overview

The Xing source provides the output of the streams mentioned below. 
The streams have DV client's DV measurement data and verification data for the tag based and social campaigns. 
It supports Full Refresh. 

### Output schema

DoubleVerify connector outputs the following streams:

* Customers
* Ads
* Daily_insights
* Lifetime_insights


### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | No |


## Getting started

### Requirements
In order to access the AdManger API the following information is required byt the Xing team to generate an API consumer that can be accessed under [dev.xing.com](dev.xing.com]):
#### App Data
This data is regarding the app or software you are planning to use the API with. The data will be shown in the OAuth process, see example screenshot below.
* App logo (just attach to the email) This must be a graphic file (JPEG, PNG, BMP or GIF), ideally with a minimum of 100 x 100 pixels to produce the best results. The maximum size is 1 Mbyte.
* App name (If you are using a third party software, just put a descriptive name there like “Youragency API Access”) -> mandatory
* Link to App website -> mandatory
* Link to Privacy Policy
* App Description (English) -> mandatory
* App Description (German)
* Callback domain: -> mandatory 
During the OAuth handshake we will verify your callback URL against the given OAuth callback domain. Check out the documentation on the XING Developer Portal for a more in-depth explanation https://dev.xing.com/docs/authentication.

#### Developer details
The responsible developer to work on the integration and to access the credentials
* Name -> mandatory
* Street and no. -> mandatory
* ZIP code, City -> mandatory
* Country -> mandatory
* XING Profile URL -> mandatory
* URL of the XING User profile of the responsible developer

#### Company details
The company that will provide the software that connects to the API
* Name -> mandatory
* Street and no. -> mandatory
* ZIP code, City -> mandatory
* Country -> mandatory
* Contact person -> mandatory
* Email address -> mandatory
* Phone number -> mandatory

### Token generation guide
See [https://dev.xing.com/docs/authentication](https://dev.xing.com/docs/authentication) once you got your API consumer.

## Changelog

| Version | Date | Pull Request | Subject |
| 0.0.1   | 2023-08-16 | #29527 | New Connector Xing |
