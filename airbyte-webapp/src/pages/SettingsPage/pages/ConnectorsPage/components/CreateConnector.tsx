import { faDocker } from "@fortawesome/free-brands-svg-icons";
import { faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useNavigate } from "react-router-dom";

import { Button } from "components/ui/Button";
import { DropdownMenu, DropdownMenuOptionType } from "components/ui/DropdownMenu";

import { useExperiment } from "hooks/services/Experiment";
import { RoutePaths, DestinationPaths } from "pages/routePaths";
import { useCreateDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useCreateSourceDefinition } from "services/connector/SourceDefinitionService";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import { ReactComponent as BuilderIcon } from "./builder-icon.svg";
import CreateConnectorModal from "./CreateConnectorModal";

interface IProps {
  type: "sources" | "destinations";
}

interface ICreateProps {
  name: string;
  documentationUrl: string;
  dockerImageTag: string;
  dockerRepository: string;
}

const CreateConnector: React.FC<IProps> = ({ type }) => {
  const navigate = useNavigate();
  const workspaceId = useCurrentWorkspaceId();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const onChangeModalState = () => {
    setIsModalOpen(!isModalOpen);
    setErrorMessage("");
  };
  const showBuilderNavigationLinks = useExperiment("connectorBuilder.showNavigationLinks", false);

  const { formatMessage } = useIntl();

  const { mutateAsync: createSourceDefinition } = useCreateSourceDefinition();

  const { mutateAsync: createDestinationDefinition } = useCreateDestinationDefinition();

  const onSubmitSource = async (sourceDefinition: ICreateProps) => {
    setErrorMessage("");
    try {
      const result = await createSourceDefinition(sourceDefinition);

      navigate(
        {
          pathname: `/${RoutePaths.Workspaces}/${workspaceId}/${RoutePaths.Source}/${RoutePaths.SourceNew}`,
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

      navigate(
        {
          pathname: `/${RoutePaths.Workspaces}/${workspaceId}/${RoutePaths.Destination}/${DestinationPaths.NewDestination}`,
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
      {type === "sources" && showBuilderNavigationLinks ? (
        <DropdownMenu
          placement="bottom"
          options={[
            {
              as: "a",
              href: `../../${RoutePaths.ConnectorBuilder}`,
              icon: <BuilderIcon />,
              displayName: formatMessage({ id: "admin.newConnector.build" }),
              internal: true,
            },
            {
              as: "button",
              icon: <FontAwesomeIcon icon={faDocker} color="#0091E2" size="xs" />,
              value: "docker",
              displayName: formatMessage({ id: "admin.newConnector.docker" }),
            },
          ]}
          onChange={(data: DropdownMenuOptionType) => data.value === "docker" && onChangeModalState()}
        >
          {() => <NewConnectorButton />}
        </DropdownMenu>
      ) : (
        <NewConnectorButton onClick={onChangeModalState} />
      )}

      {isModalOpen && (
        <CreateConnectorModal onClose={onChangeModalState} onSubmit={onSubmit} errorMessage={errorMessage} />
      )}
    </>
  );
};

interface NewConnectorButtonProps {
  onClick?: () => void;
}

const NewConnectorButton: React.FC<NewConnectorButtonProps> = ({ onClick }) => {
  return (
    <Button size="xs" icon={<FontAwesomeIcon icon={faPlus} />} onClick={onClick}>
      <FormattedMessage id="admin.newConnector" />
    </Button>
  );
};

export default CreateConnector;
