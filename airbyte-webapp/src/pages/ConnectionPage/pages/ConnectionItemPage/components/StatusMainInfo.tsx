import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { Link as ReactLink } from "react-router-dom";
import styled from "styled-components";

import ConnectorCard from "components/ConnectorCard";

import { getFrequencyConfig } from "config/utils";
import { ConnectionStatus, SourceRead, DestinationRead, WebBackendConnectionRead } from "core/request/AirbyteClient";
import { FeatureItem, useFeatureService } from "hooks/services/Feature";
import { RoutePaths } from "pages/routePaths";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";

import EnabledControl from "./EnabledControl";

const MainContainer = styled.div`
  width: 650px;
  display: flex;
  justify-content: space-between;
  padding: 10px 20px;
  background-color: white;
  border-radius: 10px;
  align-items: center;
`;

const ConnectorsLink = styled(ReactLink)`
  cursor: pointer;
  text-decoration: none;
  border-radius: 10px;

  &:hover {
    background-color: ${({ theme }) => theme.greyColor10};
  }
`;

interface StatusMainInfoProps {
  connection: WebBackendConnectionRead;
  source: SourceRead;
  destination: DestinationRead;
  onStatusUpdating?: (updating: boolean) => void;
}

export const StatusMainInfo: React.FC<StatusMainInfoProps> = ({
  onStatusUpdating,
  connection,
  source,
  destination,
}) => {
  const { hasFeature } = useFeatureService();

  const sourceDefinition = useSourceDefinition(source.sourceDefinitionId);
  const destinationDefinition = useDestinationDefinition(destination.destinationDefinitionId);

  const allowSync = hasFeature(FeatureItem.AllowSync);
  const frequency = getFrequencyConfig(connection.schedule);

  const sourceConnectionPath = `../../${RoutePaths.Source}/${source.sourceId}`;
  const destinationConnectionPath = `../../${RoutePaths.Destination}/${destination.destinationId}`;

  return (
    <MainContainer>
      <ConnectorsLink to={sourceConnectionPath}>
        <ConnectorCard
          connectionName={source.sourceName}
          icon={sourceDefinition?.icon}
          connectorName={source.name}
          releaseStage={sourceDefinition?.releaseStage}
        />
      </ConnectorsLink>
      <FontAwesomeIcon icon={faArrowRight} />
      <ConnectorsLink to={destinationConnectionPath}>
        <ConnectorCard
          connectionName={destination.destinationName}
          icon={destinationDefinition?.icon}
          connectorName={destination.name}
          releaseStage={destinationDefinition?.releaseStage}
        />
      </ConnectorsLink>
      {connection.status !== ConnectionStatus.deprecated && (
        <EnabledControl
          onStatusUpdating={onStatusUpdating}
          disabled={!allowSync}
          connection={connection}
          frequencyType={frequency?.type}
        />
      )}
    </MainContainer>
  );
};
