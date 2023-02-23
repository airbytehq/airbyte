import destinationConnectorIds from "./destinations.json";
import sourceConnectorIds from "./sources.json";

export const ConnectorIds = {
  Sources: sourceConnectorIds,
  Destinations: destinationConnectorIds,
} as const;
