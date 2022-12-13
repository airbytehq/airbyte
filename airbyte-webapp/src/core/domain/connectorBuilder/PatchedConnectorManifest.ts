import { SourceDefinitionSpecificationDraft } from "core/domain/connector";

import { ConnectorManifest } from "../../request/ConnectorManifest";

// Patching this type as required until the upstream schema is updated
export interface PatchedConnectorManifest extends ConnectorManifest {
  spec?: SourceDefinitionSpecificationDraft;
}
