import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import { useFetcher } from "rest-hooks";

import Button from "components/Button";
import CreateConnectorModal from "./CreateConnectorModal";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import config from "config";
import useRouter from "components/hooks/useRouterHook";
import { Routes } from "../../routes";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";

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

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const onChangeModalState = () => {
    setIsModalOpen(!isModalOpen);
    setErrorMessage("");
  };

  const createSourceDefinition = useFetcher(
    SourceDefinitionResource.createShape()
  );

  const onSubmitSource = async (sourceDefinition: ICreateProps) => {
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
      setErrorMessage("form.dockerError");
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
            { workspaceId: config.ui.workspaceId },
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
      setErrorMessage("form.validationError");
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
