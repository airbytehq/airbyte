import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import Button from "../../../components/Button";
import CreateConnectorModal from "./CreateConnectorModal";
import SourceResource from "../../../core/resources/Source";
import config from "../../../config";
import useRouter from "../../../components/hooks/useRouterHook";
import { Routes } from "../../routes";

const CreateConnector: React.FC = () => {
  const { push } = useRouter();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const onChangeModalState = () => setIsModalOpen(!isModalOpen);

  const createSource = useFetcher(SourceResource.createShape());
  const onSubmit = async (source: {
    name: string;
    documentationUrl: string;
    dockerImageTag: string;
    dockerRepository: string;
  }) => {
    setErrorMessage("");
    try {
      const result = await createSource({}, source, [
        [
          SourceResource.listShape(),
          { workspaceId: config.ui.workspaceId },
          (newSourceId: string, sourcesIds: { sources: string[] }) => ({
            sources: [...sourcesIds.sources, newSourceId]
          })
        ]
      ]);

      push({
        pathname: `${Routes.Source}${Routes.SourceNew}`,
        state: { sourceId: result.sourceId }
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
