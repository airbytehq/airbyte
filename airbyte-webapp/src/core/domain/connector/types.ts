import { DestinationDefinitionReadWithLatestTag } from "services/connector/DestinationDefinitionService";
import { SourceDefinitionReadWithLatestTag } from "services/connector/SourceDefinitionService";

import {
  DestinationDefinitionSpecificationRead,
  DestinationRead,
  SourceDefinitionSpecificationRead,
  SourceRead,
} from "../../request/AirbyteClient";

export type ConnectorDefinition = SourceDefinitionReadWithLatestTag | DestinationDefinitionReadWithLatestTag;

export type SourceDefinitionSpecificationDraft = Pick<
  SourceDefinitionSpecificationRead,
  "documentationUrl" | "connectionSpecification" | "authSpecification" | "advancedAuth"
>;

export type ConnectorDefinitionSpecification =
  | DestinationDefinitionSpecificationRead
  | SourceDefinitionSpecificationRead
  | SourceDefinitionSpecificationDraft;

export type ConnectorT = DestinationRead | SourceRead;
