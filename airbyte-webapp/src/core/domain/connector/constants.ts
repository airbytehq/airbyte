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
        "2470e835-feaf-4db6-96f3-70fd645acc77", // Salesforce Singer
        ...(workspaceId !== "54135667-ce73-4820-a93c-29fe1510d348" // Shopify workspace for review
          ? ["9da77001-af33-4bcd-be46-6252bf9342b9"] // Shopify
          : []),
      ]
    : [];
