import { Button } from "components/ui/Button";

import { Spec } from "core/request/ConnectorManifest";
import { useCreateBuilderDefinition } from "services/connector/SourceDefinitionService";
import { useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";

function toSaveButtonSpec(spec: Spec | undefined) {
  if (!spec) {
    return {
      documentationUrl: "http://example.org",
      connectionSpecification: {},
    };
  }
  return {
    documentationUrl: spec.documentation_url,
    connectionSpecification: spec.connection_specification,
  };
}

export const SaveButton: React.FC = () => {
  const { mutateAsync: createBuilderDefinition } = useCreateBuilderDefinition();
  const { builderFormValues, lastValidJsonManifest } = useConnectorBuilderFormState();
  return (
    <Button
      full
      onClick={() => {
        createBuilderDefinition({
          sourceDefinition: {
            name: builderFormValues.global.connectorName,
          },
          initialVersion: {
            description: "Initial version",
            manifest: JSON.stringify(lastValidJsonManifest),
            spec: JSON.stringify(toSaveButtonSpec(lastValidJsonManifest?.spec)),
            version: 1,
          },
        }).then(
          (val) => {
            alert("Worked!");
            console.log(val);
          },
          (err) => {
            alert("Failed!");
            console.log(err);
          }
        );
      }}
    >
      Save
    </Button>
  );
};
