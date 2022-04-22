import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { H6, Link } from "components";
import StepsMenu from "components/StepsMenu";

import { Source, Destination } from "core/domain/connector/types";
import useRouter from "hooks/useRouter";

import { RoutePaths } from "../../../../routePaths";
import { ConnectionSettingsRoutes } from "../ConnectionSettingsRoutes";

type IProps = {
  source: Source;
  destination: Destination;
  currentStep: ConnectionSettingsRoutes;
};

const Title = styled.div`
  text-align: center;
  padding: 21px 0 10px;
`;

const Links = styled.div`
  margin-bottom: 18px;
  font-size: 15px;
  font-weight: bold;
`;

const ConnectorsLink = styled(Link)`
  font-style: normal;
  font-weight: bold;
  font-size: 24px;
  line-height: 29px;
  text-align: center;
  display: inline-block;
  margin: 0 16px;
  color: ${({ theme }) => theme.textColor};
`;

const ConnectionPageTitle: React.FC<IProps> = ({ source, destination, currentStep }) => {
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
      name: <FormattedMessage id={"connectionForm.transformation.title"} />,
    },
    {
      id: ConnectionSettingsRoutes.SETTINGS,
      name: <FormattedMessage id="sources.settings" />,
    },
  ];

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
      <Links>
        <ConnectorsLink to={`../../${RoutePaths.Source}/${source.sourceId}`}>{source.name}</ConnectorsLink>
        <FontAwesomeIcon icon={faArrowRight} />
        <ConnectorsLink to={`../../${RoutePaths.Destination}/${destination.destinationId}`}>
          {destination.name}
        </ConnectorsLink>
      </Links>
      <StepsMenu lightMode data={steps} onSelect={onSelectStep} activeStep={currentStep} />
    </Title>
  );
};

export default ConnectionPageTitle;
