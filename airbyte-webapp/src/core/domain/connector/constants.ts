import { isCloudApp } from "utils/app";
import { ConnectorIds } from "utils/connectors";

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
export const getExcludedConnectorIds = (workspaceId?: string): string[] =>
  isCloudApp()
    ? [
        ConnectorIds.Destinations.Cassandra, // hide Cassandra Destination https://github.com/airbytehq/airbyte-cloud/issues/2606
        ConnectorIds.Destinations.Kafka, // hide Kafka Destination https://github.com/airbytehq/airbyte-cloud/issues/2610
        ConnectorIds.Destinations.MariaDbColumnStore, // hide MariaDB Destination https://github.com/airbytehq/airbyte-cloud/issues/2611
        ConnectorIds.Destinations.Mqtt, // hide MQTT Destination https://github.com/airbytehq/airbyte-cloud/issues/2613
        ConnectorIds.Destinations.Pulsar, // hide Pulsar Destination https://github.com/airbytehq/airbyte-cloud/issues/2614
        ConnectorIds.Destinations.Rockset, // hide Rockset Destination https://github.com/airbytehq/airbyte-cloud/issues/2615
        ConnectorIds.Sources.SalesforceSinger, // Salesforce Singer
        ConnectorIds.Destinations.Scylla, // hide Scylla Destination https://github.com/airbytehq/airbyte-cloud/issues/2617
        ConnectorIds.Destinations.MeiliSearch, // hide MeiliSearch Destination https://github.com/airbytehq/airbyte/issues/16313
        ConnectorIds.Destinations.RabbitMq, // hide RabbitMQ Destination https://github.com/airbytehq/airbyte/issues/16315
        ConnectorIds.Destinations.AmazonSqs, // hide Amazon SQS Destination https://github.com/airbytehq/airbyte/issues/16316
        ConnectorIds.Sources.AmazonSellerPartner, // hide Amazon Seller Partner Source https://github.com/airbytehq/airbyte/issues/14734
        // revert me
        ...(workspaceId !== "d705a766-e9e3-4689-85cb-52143422317d" // `oauth-testing` workspace for review
          ? [ConnectorIds.Sources.YouTubeAnalyticsBusiness] // Youtube Analytics Business
          : []),
        //
      ]
    : [];
