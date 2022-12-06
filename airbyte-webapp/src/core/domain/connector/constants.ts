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
  [];
