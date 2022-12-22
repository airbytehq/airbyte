import { DestinationDefinitionRead } from "core/request/AirbyteClient";
import { ConnectorIds } from "utils/connectors";

export const mockDestinationDefinition: DestinationDefinitionRead = {
  destinationDefinitionId: ConnectorIds.Destinations.Postgres,
  name: "Postgres",
  dockerRepository: "airbyte/destination-postgres",
  dockerImageTag: "0.3.26",
  documentationUrl: "https://docs.airbyte.com/integrations/destinations/postgres",
  protocolVersion: "0.2.0",
  releaseStage: "alpha",
  supportsDbt: true,
  supportsNormalization: true,
};
