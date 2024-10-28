# Kisi
This directory contains the manifest-only connector for `source-kisi`.

This is the setup for the Kisi source connector that ingests data from the Kisi API.

Kisi&#39;s sturdy hardware and user-friendly software work in perfect harmony to enhance the security of your spaces. Remotely manage your locations, streamline operations, and stay compliant while enjoying mobile unlocks. https://www.getkisi.com/

In order to use this source, you must first create an account with Kisi.
On the top right corner, click on your name and click on My Account.
Next, select the API tab and click on Add API key. Enter your name, your Kisi password, and your verification code and click Add. Copy the API key shown on the screen.

You can learn more about the API key here https://api.kisi.io/docs#/


Kisi&#39;s sturdy hardware and user-friendly software work in perfect harmony to enhance the security of your spaces. Remotely manage your locations, streamline operations, and stay compliant while enjoying mobile unlocks. https://www.getkisi.com/

In order to use this source, you must first create an account with Kisi.
On the top right corner, click on your name and click on My Account.
Next, select the API tab and click on Add API key. Enter your name, your Kisi password, and your verification code and click Add. Copy the API key shown on the screen.

You can learn more about the API key here https://api.kisi.io/docs#/

## Usage
There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Local Development
We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-kisi:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-kisi build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-kisi test
```

