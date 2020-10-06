import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { useFetcher, useSubscription, useResource } from "rest-hooks";

import ContentCard from "../../../../../components/ContentCard";
import Button from "../../../../../components/Button";
import StatusMainInfo from "./StatusMainInfo";
import ConnectionResource, {
  Connection
} from "../../../../../core/resources/Connection";
import JobResource from "../../../../../core/resources/Job";
import JobsList from "./JobsList";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import config from "../../../../../config";
import { Destination } from "../../../../../core/resources/Destination";
import EmptyResource from "../../../components/EmptyResource";

type IProps = {
  sourceData: Connection;
  onEnabledChange: () => void;
  destination: Destination;
  frequencyText?: string;
};

const Content = styled.div`
  max-width: 816px;
  margin: 18px auto;
`;

const StyledContentCard = styled(ContentCard)`
  margin-bottom: 20px;
`;

const Title = styled.div`
  display: flex;
  justify-content: space-between;
  flex-direction: row;
  align-items: center;
`;

const TryArrow = styled(FontAwesomeIcon)`
  margin-right: 10px;
  font-size: 14px;
`;

const SyncButton = styled(Button)`
  padding: 5px 8px;
  margin: -5px 0;
`;

const StatusView: React.FC<IProps> = ({
  sourceData,
  onEnabledChange,
  destination,
  frequencyText
}) => {
  const { jobs } = useResource(JobResource.listShape(), {
    configId: sourceData.connectionId,
    configType: "sync"
  });
  useSubscription(JobResource.listShape(), {
    configId: sourceData.connectionId,
    configType: "sync"
  });

  const SyncConnection = useFetcher(ConnectionResource.syncShape());

  const onSync = () => {
    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Full refresh sync",
      connector_source: sourceData.source?.sourceName,
      connector_source_id: sourceData.source?.sourceId,
      connector_destination: destination.name,
      connector_destination_id: destination.destinationId,
      frequency: frequencyText
    });
    SyncConnection({
      connectionId: sourceData.connectionId
    });
  };

  return (
    <Content>
      <StatusMainInfo
        sourceData={sourceData}
        onEnabledChange={onEnabledChange}
        destination={destination}
        frequencyText={frequencyText}
      />
      <StyledContentCard
        title={
          <Title>
            <FormattedMessage id={"sources.syncHistory"} />
            <SyncButton onClick={onSync}>
              <TryArrow icon={faRedoAlt} />
              <FormattedMessage id={"sources.syncNow"} />
            </SyncButton>
          </Title>
        }
      >
        {jobs.length ? (
          <JobsList jobs={jobs} />
        ) : (
          <EmptyResource text={<FormattedMessage id="sources.noSync" />} />
        )}
      </StyledContentCard>
    </Content>
  );
};

export default StatusView;
