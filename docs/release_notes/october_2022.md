# October 2022
## Airbyte [v0.40.13](https://github.com/airbytehq/airbyte/releases/tag/v0.40.13) to [v0.40.17](https://github.com/airbytehq/airbyte/releases/tag/v0.40.17)

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms. 

### New features
* Added the low-code connector builder UI to Airbyte OSS. It includes an embedded YAML editor and significantly reduces the time and complexity of building and maintaining connectors. [#17482](https://github.com/airbytehq/airbyte/pull/17482)
* Added Datadog Real User Monitoring (RUM) support to the webapp, which helps us monitor frontend performance in Airbyte Cloud. [#17821](https://github.com/airbytehq/airbyte/pull/17821)
* Added Nginx and Basic Auth to ensure security when using Airbyte Open Source. [#17694](https://github.com/airbytehq/airbyte/pull/17694)
    * Now when you start the Airbyte server and go to localhost:8000, you’ll be prompted to log in before accessing your Airbyte workspace.   
    * You should change the default username (airbyte) and password (password) before you deploy Airbyte. If you do not want a username or password, you can remove them by setting `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` to empty values (" ") in your `.env` file. 
    * Our [CLI](https://github.com/airbytehq/airbyte/pull/17982) and [docs](https://docs.airbyte.com/deploying-airbyte/local-deployment) have been updated to reflect this change.

### Improvements
* Since adding Basic Auth to Airbyte Open Source, we improved the `load_test` script to reflect this change. Now when the `load_test` script sources the `.env` file, it includes `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` when calling the API. [#18273](https://github.com/airbytehq/airbyte/pull/18273)
* Improved the Airbyte platform by updating the Apache Commons Text from 1.9 to 1.10.0 because version 1.9 was affected by [CVE 2022-42889](https://nvd.nist.gov/vuln/detail/CVE-2022-42889) (Text4Shell). [#18273](https://github.com/airbytehq/airbyte/pull/18273) 
    * We do not intend to update older versions of Airbyte because we were not affected by the vulnerable behavior:
        * Our direct usages of `commons-text` either do not use the vulnerable class or are pinned to an unaffected version.
        * Almost all of our transitive dependencies on `commons-text` are limited to test code. Runtime code has no vulnerable transitive dependencies on `commons-text`.
