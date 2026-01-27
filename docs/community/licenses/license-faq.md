# License FAQ

<!-- vale off -->

This page answers common questions about the ELv2 license and its relationship to you and Airbyte.

## About Elastic License 2.0 (ELv2)

ELv2 is a simple, non-copyleft license, allowing for the right to “use, copy, distribute, make available, and prepare derivative works of the software”. Anyone can use Airbyte, free of charge. You can run the software at scale on your infrastructure. Three high-level limitations exist. You can't:

1. Provide the products to others as a managed service ([read more](#managed-service-case));

2. Circumvent the license key functionality or remove/obscure features protected by license keys; or

3. Remove or obscure any licensing, copyright, or other notices.

In case you want to work with Airbyte without these limitations, we offer alternative licenses. These licenses include maintenance, support, and customary commercial terms. If you need a different license, please get in touch with us at: contact@airbyte.io.

[View License](elv2-license.md)

## FAQ

### What limitations does ELv2 impose on the use of Airbyte?

If you are an Airbyte Cloud customer, nothing changes for you.

For open source users, everyone can continue to use Airbyte as you are doing today: no limitations exist on volume, number of users, number of connections, etc.

A few high-level limitations exist. You cannot:

1. Provide the products to others as a managed service. For example, you cannot sell a cloud service that provides users with direct access to Airbyte. You can sell access to applications built and run using Airbyte ([read more](#what-is-the-managed-service-use-case-that-is-not-allowed-under-elv2)).

2. Circumvent the license key functionality or remove/obscure features protected by license keys. For example, our code may contain watermarks or keys to unlock proprietary functionality. Airbyte marks those elements in its source code. You can’t remove or change them.

### Why did Airbyte adopt ELv2?

Airbyte released Airbyte Cloud, a managed version of Airbyte that offers alternatives to how you operate Airbyte, including additional features and execution models. Airbyte needed to find a great way to execute its mission to commoditize data integration with open source and its ambition to create a sustainable business.

ELv2 gives us the best of both worlds.

On one hand, open source users can continue to use Airbyte freely, and on the other hand, we can safely create a sustainable business and continue to invest in the community, project and product. Airbyte doesn't have to worry about other large companies taking the product to monetize it for themselves, hurting this community in the process.

### Will Airbyte connectors continue to be open source?

Our own connectors remain open-source, and our contributors can also develop your own connectors and continue to choose whichever license you prefer. This is our way to accomplish Airbyte’s vision of commoditizing data integration: access to data shouldn’t be behind a paywall. Also, we want Airbyte’s licensing to work well with applications that integrate using connectors.

We are continuously investing in Airbyte's data protocol and all the tooling around it. The Connector Development Kit (CDK), which helps our community and our team build and maintain connectors at scale, is a cornerstone of this commoditization strategy and also remains open-source.

### How do I contribute to Airbyte under ELv2?

Airbyte’s projects are available here. Anyone can contribute to any of these projects (including those licensed with ELv2). We have a Contributor License Agreement that you have to sign with your first contribution.

### When did ELv2 become effective?

ELv2 applies as of September 27, 2021 and version 0.30.0.

### What's the “managed service” use case that isn't allowed under ELv2? {#managed-service-case}

We chose ELv2 because it's permissive with what you can do with the software.

You can basically build any product on top of Airbyte as long as you don’t:

- Host Airbyte yourself and sell it as an ELT/ETL tool, or a replacement for the Airbyte solution.

- Sell a product that directly exposes Airbyte’s UI or API.

Here is a non-exhaustive list of what you can do (without providing your customers direct access to Airbyte functionality):

- I am creating an analytics platform and I want to use Airbyte to bring data in on behalf of my customers.

- I am building my internal data stack and I want my team to be able to interact with Airbyte to configure the pipelines through the UI or the API.

### My company has a policy against using code that restricts commercial use – can I still use Airbyte under ELv2?

You can use software under ELv2 for your commercial business, you simply can't offer it as a managed service.

### As a data agency, I use Airbyte to fulfill my customer needs. How does ELv2 affect me?

You can continue to use Airbyte, as long as you don’t offer it as a managed service.

### I started to use Airbyte to ingest my customer’s data. What should I do?

You can continue to use Airbyte, as long as you don’t offer it as a managed service.

### Can I customize ELv2 software?

Yes, you can customize ELv2 software. ELv2 is similar in this sense to permissive open-source licenses. You can modify the software, integrate the variant into your app, and operate the modified app, as long as you don’t go against any of the limitations.

### Why didn’t you use a closed-source license for Airbyte Core?

Airbyte wants to provide developers with free access to Airbyte Core's source code — including rights to modify it. Since this wouldn’t be possible with a closed-source license, Airbyte decided to use the more permissive ELv2.

<!-- vale on -->
