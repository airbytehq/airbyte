import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRight } from "@fortawesome/free-solid-svg-icons";

import { Source } from "core/resources/Source";
import { Destination } from "core/resources/Destination";
import { FormattedMessage } from "react-intl";
import { H6 } from "components/base";
import Link from "components/Link";
import { Routes } from "pages/routes";
import StepsMenu from "components/StepsMenu";
import useRouter from "hooks/useRouter";

type IProps = {
  source: Source;
  destination: Destination;
  connectionId: string;
  currentStep: "status" | "settings" | "replication" | "transformation";
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

const ConnectionPageTitle: React.FC<IProps> = ({
  source,
  destination,
  currentStep,
  connectionId,
}) => {
  const { push } = useRouter<{ id: string }>();

  const steps = [
    {
      id: "status",
      name: <FormattedMessage id={"sources.status"} />,
    },
    {
      id: "replication",
      name: <FormattedMessage id={"connection.replication"} />,
    },
    {
      id: "transformation",
      name: <FormattedMessage id={"connectionForm.transformation.title"} />,
    },
    {
      id: "settings",
      name: <FormattedMessage id={"sources.settings"} />,
    },
  ];

  const onSelectStep = (id: string) => {
    if (id === "settings") {
      push(`${Routes.Connections}/${connectionId}${Routes.Settings}`);
    } else if (id === "replication") {
      push(`${Routes.Connections}/${connectionId}${Routes.Replication}`);
    } else if (id === "transformation") {
      push(`${Routes.Connections}/${connectionId}${Routes.Transformation}`);
    } else {
      push(`${Routes.Connections}/${connectionId}`);
    }
  };

  return (
    <Title>
      <H6 center bold highlighted>
        <FormattedMessage id="connection.title" />
      </H6>
      <Links>
        <ConnectorsLink to={`${Routes.Source}/${source.sourceId}`}>
          {source.name}
        </ConnectorsLink>
        <FontAwesomeIcon icon={faArrowRight} />
        <ConnectorsLink
          to={`${Routes.Destination}/${destination.destinationId}`}
        >
          {destination.name}
        </ConnectorsLink>
      </Links>
      <StepsMenu
        lightMode
        data={steps}
        onSelect={onSelectStep}
        activeStep={currentStep}
      />
    </Title>
  );
};

export default ConnectionPageTitle;
