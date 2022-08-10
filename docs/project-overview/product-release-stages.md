# Product Release Stages

The following release stages describe the lifecycle of an Airbyte product, feature, or connector.

| Expectations | Alpha | Beta | General Availability (GA)|
|:-------------|:------|:-----|:-------------------------|
| Customer Availability | Alpha features and products may have limited availability (by invitation only) <br/><br/> Alpha connectors are available to all users | Beta features and products may have limited availability (by invitation only) <br/><br/> Beta connectors are available to all users | Available to all users |
|Support | Cloud: No Support SLAs <br/><br/> Open-source: Community Slack Support | Cloud: Official Beta Support SLA <br/><br/> Open-source: Community Slack Support | Cloud: Official GA Support SLA <br/><br/> Open-source: Community Slack Support |
| Production Readiness | No | Yes (with caveats) | Yes |

## Alpha 
An alpha release signifies a product, feature, or connector under development and helps Airbyte gather early feedback and issues reported by early adopters. We strongly discourage using alpha releases for production use cases and do not offer Cloud Support SLAs around these products, features, or connectors.

### What you should know about an alpha release

- An alpha release might not be feature-complete (features planned for the release are under development) and may include backward-incompatible/breaking API changes. 
- Access for alpha features and products may not be enabled for all Airbyte users by default. Depending on the feature, you may enable the feature either from the Airbyte UI or by contacting Airbyte Support. Alpha connectors are available to all users. 
- Alpha releases may be announced via email, in the Airbyte UI, and/or through certain pages of the Airbyte docs.

## Beta 
A beta release is considered stable and reliable with no backwards incompatible changes but has not been validated by a broader group of users. We expect to find and fix a few issues and bugs in the release before it’s ready for GA.

### What you should know about a beta release

- A beta release is generally feature-complete (features planned for the release have been mostly implemented) and does not include backward-incompatible/breaking API changes. 
- Access may be enabled for all Airbyte users by default. Depending on the feature, you may enable the feature either from the Airbyte UI or by contacting Airbyte Support. Beta connectors are available to all users. 
- Beta releases may be announced via email, in the Airbyte UI, and/or through certain pages of the Airbyte docs.

## General availability (GA) 
A generally available release has been deemed ready for use in a production environment and is officially supported by Airbyte. Its documentation is considered sufficient to support widespread adoption.

### What you should know about a GA release

- A GA release is feature-complete (features planned for the release have been fully implemented) and does not include backward-incompatible/breaking API changes. 
- Access is enabled for all Airbyte users by default. Depending on the feature, you may enable the feature either from the Airbyte UI or by contacting Airbyte Support. 
- GA releases may be announced via email, in the Airbyte UI, and/or through certain pages of the Airbyte docs. 

## Deprecated 
A deprecated feature, product, or connector is no longer officially supported by Airbyte. It might continue to work for a period of time but Airbyte recommends that you migrate away from and avoid relying on deprecated releases.
