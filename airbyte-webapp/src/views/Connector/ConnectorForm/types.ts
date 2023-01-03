import { DestinationDefinitionReadWithLatestTag } from "services/connector/DestinationDefinitionService";
import { SourceDefinitionReadWithLatestTag } from "services/connector/SourceDefinitionService";

// TODO: This needs to be converted to interface, but has int he current state a problem with index signatures
// eslint-disable-next-line @typescript-eslint/consistent-type-definitions
export type ConnectorFormValues<T = unknown> = {
  name: string;
  connectionConfiguration: T;
};

// The whole ConnectorCard form values
export type ConnectorCardValues = { serviceType: string } & ConnectorFormValues;

export type DestinationConnectorCard = Pick<
  DestinationDefinitionReadWithLatestTag,
  "destinationDefinitionId" | "name" | "icon" | "releaseStage"
>;
export type SourceConnectorCard = Pick<
  SourceDefinitionReadWithLatestTag,
  "sourceDefinitionId" | "name" | "icon" | "releaseStage"
>;

export type SuggestedConnector = (
  | Omit<DestinationConnectorCard, "destinationDefinitionId">
  | Omit<SourceConnectorCard, "sourceDefinitionId">
) & { connectorDefinitionId: string };
