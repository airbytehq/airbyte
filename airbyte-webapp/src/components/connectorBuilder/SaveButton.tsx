import { Button } from "components/ui/Button";

import { useCreateBuilderDefinition } from "services/connector/SourceDefinitionService";
import { useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";

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
            spec: JSON.stringify(lastValidJsonManifest?.spec),
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
