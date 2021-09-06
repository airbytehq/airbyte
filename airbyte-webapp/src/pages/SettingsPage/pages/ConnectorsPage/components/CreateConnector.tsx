import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useFetcher } from "rest-hooks";

import { Button } from "components";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import useRouter from "hooks/useRouter";
import { Routes } from "pages/routes";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";

import CreateConnectorModal from "./CreateConnectorModal";
import useWorkspace from "hooks/services/useWorkspace";

type IProps = {
  type: string;
};

type ICreateProps = {
  name: string;
  documentationUrl: string;
  dockerImageTag: string;
  dockerRepository: string;
};

const CreateConnector: React.FC<IProps> = ({ type }) => {
  const { push } = useRouter();
  const { workspace } = useWorkspace();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const onChangeModalState = () => {
    setIsModalOpen(!isModalOpen);
    setErrorMessage("");
  };

  const formatMessage = useIntl().formatMessage;

  const createSourceDefinition = useFetcher(
    SourceDefinitionResource.createShape()
  );

  const onSubmitSource = async (sourceDefinition: ICreateProps) => {
    setErrorMessage("");
    try {
      const result = await createSourceDefinition({}, sourceDefinition, [
        [
          SourceDefinitionResource.listShape(),
          { workspaceId: workspace.workspaceId },
          (
            newSourceDefinitionId: string,
            sourceDefinitionIds: { sourceDefinitions: string[] }
          ) => ({
            sourceDefinitions: [
              ...sourceDefinitionIds.sourceDefinitions,
              newSourceDefinitionId,
            ],
          }),
        ],
      ]);

      push({
        pathname: `${Routes.Source}${Routes.SourceNew}`,
        state: { sourceDefinitionId: result.sourceDefinitionId },
      });
    } catch (e) {
      setErrorMessage(e.message || formatMessage({ id: "form.dockerError" }));
    }
  };

  const createDestinationDefinition = useFetcher(
    DestinationDefinitionResource.createShape()
  );
  const onSubmitDestination = async (destinationDefinition: ICreateProps) => {
    setErrorMessage("");
    try {
      const result = await createDestinationDefinition(
        {},
        destinationDefinition,
        [
          [
            DestinationDefinitionResource.listShape(),
            { workspaceId: workspace.workspaceId },
            (
              newDestinationDefinitionId: string,
              destinationDefinitionIds: { destinationDefinitions: string[] }
            ) => ({
              destinationDefinitions: [
                ...destinationDefinitionIds.destinationDefinitions,
                newDestinationDefinitionId,
              ],
            }),
          ],
        ]
      );

      push({
        pathname: `${Routes.Destination}${Routes.DestinationNew}`,
        state: { destinationDefinitionId: result.destinationDefinitionId },
      });
    } catch (e) {
      setErrorMessage(e.message || formatMessage({ id: "form.dockerError" }));
    }
  };

  const onSubmit = (values: ICreateProps) =>
    type === "sources" ? onSubmitSource(values) : onSubmitDestination(values);

  return (
    <>
      {type === "configuration" ? null : (
        <Button onClick={onChangeModalState}>
          <FormattedMessage id="admin.newConnector" />
        </Button>
      )}

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
