import { isCloudApp } from "utils/app";

export const DEV_IMAGE_TAG = "dev";

/**
 * Returns the list of excluded connections for cloud users.
 * 
 * During the Cloud private beta, we let users pick any connector in our catalog.
 * Later on, we realized we shouldn't have allowed using connectors whose platforms required oauth
 * But by that point, some users were already leveraging them, so removing them would crash the app for users
 * instead we'll filter out those connectors from this drop down menu, and retain them in the backend
 * This way, they will not be available for usage in new connections, but they will be available for users
 * already leveraging them.

 * @param {string} workspaceId The workspace Id
 * @returns {array} List of connectorIds that should be filtered out
 */
export const getExcludedConnectorIds = (workspaceId: string) =>
  isCloudApp()
    ? [
        "707456df-6f4f-4ced-b5c6-03f73bcad1c5", // hide Cassandra Destination https://github.com/airbytehq/airbyte-cloud/issues/2606
        "8ccd8909-4e99-4141-b48d-4984b70b2d89", // hide DynamoDB Destination https://github.com/airbytehq/airbyte-cloud/issues/2608
        "68f351a7-2745-4bef-ad7f-996b8e51bb8c", // hide ElasticSearch Destination https://github.com/airbytehq/airbyte-cloud/issues/2594
        "9f760101-60ae-462f-9ee6-b7a9dafd454d", // hide Kafka Destination https://github.com/airbytehq/airbyte-cloud/issues/2610
        "294a4790-429b-40ae-9516-49826b9702e1", // hide MariaDB Destination https://github.com/airbytehq/airbyte-cloud/issues/2611
        "8b746512-8c2e-6ac1-4adc-b59faafd473c", // hide MongoDB Destination https://github.com/airbytehq/airbyte-cloud/issues/2612
        "f3802bc4-5406-4752-9e8d-01e504ca8194", // hide MQTT Destination https://github.com/airbytehq/airbyte-cloud/issues/2613
        "2340cbba-358e-11ec-8d3d-0242ac130203", // hide Pular Destination https://github.com/airbytehq/airbyte-cloud/issues/2614
        "d4d3fef9-e319-45c2-881a-bd02ce44cc9f", // hide Redis Destination https://github.com/airbytehq/airbyte-cloud/issues/2593
        "2c9d93a7-9a17-4789-9de9-f46f0097eb70", // hide Rockset Destination https://github.com/airbytehq/airbyte-cloud/issues/2615
        "2470e835-feaf-4db6-96f3-70fd645acc77", // Salesforce Singer
        "3dc6f384-cd6b-4be3-ad16-a41450899bf0", // hide Scylla Destination https://github.com/airbytehq/airbyte-cloud/issues/2617
        "af7c921e-5892-4ff2-b6c1-4a5ab258fb7e", // hide MeiliSearch Destination https://github.com/airbytehq/airbyte/issues/16313
        "e06ad785-ad6f-4647-b2e8-3027a5c59454", // hide RabbitMQ Destination https://github.com/airbytehq/airbyte/issues/16315
        "0eeee7fb-518f-4045-bacc-9619e31c43ea", // hide Amazon SQS Destination https://github.com/airbytehq/airbyte/issues/16316
        ...(workspaceId !== "54135667-ce73-4820-a93c-29fe1510d348" // Shopify workspace for review
          ? ["9da77001-af33-4bcd-be46-6252bf9342b9"] // Shopify
          : []),
      ]
    : [];
