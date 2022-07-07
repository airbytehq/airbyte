import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button } from "components";

import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";
import { useCreateDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useCreateSourceDefinition } from "services/connector/SourceDefinitionService";

import CreateConnectorModal from "./CreateConnectorModal";

interface IProps {
  type: string;
}

interface ICreateProps {
  name: string;
  documentationUrl: string;
  dockerImageTag: string;
  dockerRepository: string;
}

const CreateConnector: React.FC<IProps> = ({ type }) => {
  const { push } = useRouter();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const onChangeModalState = () => {
    setIsModalOpen(!isModalOpen);
    setErrorMessage("");
  };

  const { formatMessage } = useIntl();

  const { mutateAsync: createSourceDefinition } = useCreateSourceDefinition();

  const { mutateAsync: createDestinationDefinition } = useCreateDestinationDefinition();

  const onSubmitSource = async (sourceDefinition: ICreateProps) => {
    setErrorMessage("");
    try {
      const result = await createSourceDefinition(sourceDefinition);

      push(
        {
          pathname: `${RoutePaths.Source}${RoutePaths.SourceNew}`,
        },
        { state: { sourceDefinitionId: result.sourceDefinitionId } }
      );
    } catch (e) {
      setErrorMessage(e.message || formatMessage({ id: "form.dockerError" }));
    }
  };

  const onSubmitDestination = async (destinationDefinition: ICreateProps) => {
    setErrorMessage("");
    try {
      const result = await createDestinationDefinition(destinationDefinition);

      push(
        {
          pathname: `${RoutePaths.Destination}${RoutePaths.DestinationNew}`,
        },
        { state: { destinationDefinitionId: result.destinationDefinitionId } }
      );
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
        <CreateConnectorModal onClose={onChangeModalState} onSubmit={onSubmit} errorMessage={errorMessage} />
      )}
    </>
  );
};

export default CreateConnector;
