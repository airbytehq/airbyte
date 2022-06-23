import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { H6 } from "components";
import StepsMenu from "components/StepsMenu";

import { ConnectionStatus, DestinationRead, SourceRead, WebBackendConnectionRead } from "core/request/AirbyteClient";
import useRouter from "hooks/useRouter";

import { ConnectionSettingsRoutes } from "../ConnectionSettingsRoutes";
import ConnectionName from "./ConnectionName";
import { StatusMainInfo } from "./StatusMainInfo";

interface ConnectionPageTitleProps {
  source: SourceRead;
  destination: DestinationRead;
  connection: WebBackendConnectionRead;
  currentStep: ConnectionSettingsRoutes;
  onStatusUpdating?: (updating: boolean) => void;
}

const Title = styled.div`
  text-align: center;
  padding: 21px 0 10px;
`;

const Links = styled.div`
  margin: 18px 0;
  font-size: 15px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const ConnectionPageTitle: React.FC<ConnectionPageTitleProps> = ({
  source,
  destination,
  connection,
  currentStep,
  onStatusUpdating,
}) => {
  const { push } = useRouter<{ id: string }>();

  const steps = [
    {
      id: ConnectionSettingsRoutes.STATUS,
      name: <FormattedMessage id="sources.status" />,
    },
    {
      id: ConnectionSettingsRoutes.REPLICATION,
      name: <FormattedMessage id="connection.replication" />,
    },
    {
      id: ConnectionSettingsRoutes.TRANSFORMATION,
      name: <FormattedMessage id="connectionForm.transformation.title" />,
    },
  ];

  connection.status !== ConnectionStatus.deprecated &&
    steps.push({
      id: ConnectionSettingsRoutes.SETTINGS,
      name: <FormattedMessage id="sources.settings" />,
    });

  const onSelectStep = (id: string) => {
    if (id === ConnectionSettingsRoutes.STATUS) {
      push("");
    } else {
      push(id);
    }
  };

  return (
    <Title>
      <H6 center bold highlighted>
        <FormattedMessage id="connection.title" />
      </H6>
      <ConnectionName connection={connection} />
      <Links>
        <StatusMainInfo
          connection={connection}
          source={source}
          destination={destination}
          onStatusUpdating={onStatusUpdating}
        />
      </Links>
      <StepsMenu lightMode data={steps} onSelect={onSelectStep} activeStep={currentStep} />
    </Title>
  );
};

export default ConnectionPageTitle;
