---
products: cloud-enterprise
---

# Cloud Enterprise

Airbyte Cloud Enterprise is a hybrid solution that consists of a fully managed Cloud control plane with separate data planes that run in your own infrastructure. It's ideal for organizations with data sovereignty and compliance requirements who need to carefully manage data movement while also minimizing the time and effort needed to self-manage Airbyte.

## Overview

Many organizations collect data in all types of operational systems from users around the world. However, you might face strict requirements around how you can process and store data, as well as who can access it. These requirements comes in many forms.

- **Compliance**: GDPR (European Union), PIPEDA (Canada), HIPAA (USA), APPs (Australia), PIPL (China), and other frameworks govern the management of data, and can punish non-compliance with significant financial penalties.

- **Data sovereignty**: When sensitive data crosses borders, it can be subject to prying eyes and foreign regulations it isn't meant for. Keeping data within a specific country or geographical region helps ensure privacy and control over that data.

- **Security and operational policies**: Some data, like trade secrets or sensitive industry information, is so valuable that external exposure could present a major incident.

While these requirements are critical, organizations also have finite time and expertise. Managing these operational and compliance requirements with more infrastructure often means increased maintenance commitments, higher spend, and greater complexity.

Cloud Enterprise addresses these needs by offering fully managed Cloud workspaces (a control plane) that connect to separate data planes you manage in your own infrastructure. You can also use fully managed data planes for less sensitive data that doesn't need to remain in your own infrastructure. Each Cloud workspace uses one region and data plane, so a single Airbyte instance with multiple workspaces is an ideal way to segregate data and connections.

Cloud Enterprise also offers other enterprise-grade abilities.

| Feature             | Description                                                                                                                                                             |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| User Management     | Enable multiple users to concurrently move data from a single Airbyte deployment.                                                                                       |
| Single Sign-On      | Manage user access to Airbyte from your Okta, Azure Entra ID or OIDC-compatible identity provider.                                                                      |
| Multiple Workspaces | Manage multiple isolated projects or teams on a single Airbyte deployment.                                                                                              |
| Role-Based Access   | Manage user permissions and access across workspaces from a single pane of glass.                                                                                       |
| Column Hashing      | Protect sensitive information by hashing personally identifiable information (PII) as it moves through your pipelines.                                                   |
| Support with SLAs   | [Priority assistance](https://docs.airbyte.com/operator-guides/contact-support/#airbyte-enterprise-self-hosted-support) with deploying, managing and upgrading Airbyte. |

### Cloud Enterprise versus Cloud Teams

Cloud Enterprise includes all features that are standard in Cloud Teams with the additional capability of running self-managed data planes.

## An example hybrid deployment

Every organization's precise needs differ, so you can implement Cloud Enterprise in the way that suits you best. In this example, you have three workspaces. 

- Workspace 1 contains non-sensitive data and uses Airbyte's fully managed European region.

- Workspaces 2 and 3, which contain sensitive data from the United States and Australia, run on your own infrastructure. Only metadata ever reaches the control plane.

![In this example, you have three workspaces. Workspace 1 contains non-sensitive data and uses Airbyte's fully managed European workspace. Workspaces 2 and 3, which contain sensitive data from the United States and Australia, run on your own infrastructure. Only metadata ever reaches the control plane.](img/cloud-enterprise-example.png)

## Get started

- To learn more about Cloud Enterprise, [talk to sales](https://airbyte.com/company/talk-to-sales).
