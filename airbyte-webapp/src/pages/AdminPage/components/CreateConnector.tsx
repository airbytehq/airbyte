import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import Button from "../../../components/Button";
import CreateConnectorModal from "./CreateConnectorModal";
import SourceDefinitionResource from "../../../core/resources/SourceDefinition";
import config from "../../../config";
import useRouter from "../../../components/hooks/useRouterHook";
import { Routes } from "../../routes";

const CreateConnector: React.FC = () => {
  const { push } = useRouter();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const onChangeModalState = () => setIsModalOpen(!isModalOpen);

  const createSourceDefinition = useFetcher(
    SourceDefinitionResource.createShape()
  );
  const onSubmit = async (sourceDefinition: {
    name: string;
    documentationUrl: string;
    dockerImageTag: string;
    dockerRepository: string;
  }) => {
    setErrorMessage("");
    try {
      const result = await createSourceDefinition({}, sourceDefinition, [
        [
          SourceDefinitionResource.listShape(),
          { workspaceId: config.ui.workspaceId },
          (
            newSourceDefinitionId: string,
            sourceDefinitionIds: { sourceDefinitions: string[] }
          ) => ({
            sourceDefinitions: [
              ...sourceDefinitionIds.sourceDefinitions,
              newSourceDefinitionId
            ]
          })
        ]
      ]);

      push({
        pathname: `${Routes.Source}${Routes.SourceNew}`,
        state: { sourceDefinitionId: result.sourceDefinitionId }
      });
    } catch (e) {
      setErrorMessage("form.validationError");
    }
  };

  return (
    <>
      <Button onClick={onChangeModalState}>
        <FormattedMessage id="admin.newConnector" />
      </Button>
      {isModalOpen && (
        <CreateConnectorModal
          onClose={onChangeModalState}
          onSubmit={onSubmit}
          errorMessage={errorMessage}
        />
      )}
    </>
  );
};

export default CreateConnector;
