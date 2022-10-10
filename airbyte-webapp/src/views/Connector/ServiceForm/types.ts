import { DestinationDefinitionReadWithLatestTag } from "services/connector/DestinationDefinitionService";

// TODO: This needs to be converted to interface, but has int he current state a problem with index signatures
// eslint-disable-next-line @typescript-eslint/consistent-type-definitions
export type ServiceFormValues<T = unknown> = {
  name: string;
  serviceType: string;
  connectionConfiguration: T;
};

export type DestinationConnectorCard = Pick<
  DestinationDefinitionReadWithLatestTag,
  "destinationDefinitionId" | "name" | "icon" | "releaseStage"
>;
