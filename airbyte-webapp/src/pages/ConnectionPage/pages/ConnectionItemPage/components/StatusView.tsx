import React, { useCallback, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { useFetcher, useResource, useSubscription } from "rest-hooks";

import ContentCard from "../../../../../components/ContentCard";
import Button from "../../../../../components/Button";
import StatusMainInfo from "./StatusMainInfo";
import ConnectionResource, {
  Connection,
} from "../../../../../core/resources/Connection";
import JobResource from "../../../../../core/resources/Job";
import JobsList from "./JobsList";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import config from "../../../../../config";
import EmptyResource from "../../../../../components/EmptyResourceBlock";
import ResetDataModal from "../../../../../components/ResetDataModal";
import useConnection from "../../../../../components/hooks/services/useConnectionHook";
import useLoadingStateHook from "../../../../../components/hooks/useLoadingStateHook";
import LoadingButton from "../../../../../components/Button/LoadingButton";

type IProps = {
  connection: Connection;
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
  margin: 0 10px -1px 0;
  font-size: 14px;
`;

const SyncButton = styled(LoadingButton)`
  padding: 5px 8px;
  margin: -5px 0 -5px 9px;
  min-width: 101px;
  min-height: 28px;
`;

const StatusView: React.FC<IProps> = ({ connection, frequencyText }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { isLoading, showFeedback, startAction } = useLoadingStateHook();
  const { jobs } = useResource(JobResource.listShape(), {
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
  });
  useSubscription(JobResource.listShape(), {
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
  });

  const SyncConnection = useFetcher(ConnectionResource.syncShape());

  const { resetConnection } = useConnection();

  const onSync = async () => {
    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action: "Full refresh sync",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: frequencyText,
    });
    await SyncConnection({
      connectionId: connection.connectionId,
    });
  };

  const onReset = useCallback(() => resetConnection(connection.connectionId), [
    resetConnection,
    connection.connectionId,
  ]);

  return (
    <Content>
      <StatusMainInfo connection={connection} frequencyText={frequencyText} />
      <StyledContentCard
        title={
          <Title>
            <FormattedMessage id={"sources.syncHistory"} />
            <div>
              <Button onClick={() => setIsModalOpen(true)}>
                <FormattedMessage id={"connection.resetData"} />
              </Button>
              <SyncButton
                isLoading={isLoading}
                wasActive={showFeedback}
                onClick={() => startAction({ action: onSync })}
              >
                {showFeedback ? (
                  <FormattedMessage id={"sources.syncingNow"} />
                ) : (
                  <>
                    <TryArrow icon={faRedoAlt} />
                    <FormattedMessage id={"sources.syncNow"} />
                  </>
                )}
              </SyncButton>
            </div>
          </Title>
        }
      >
        {jobs.length ? (
          <JobsList jobs={jobs} />
        ) : (
          <EmptyResource text={<FormattedMessage id="sources.noSync" />} />
        )}
      </StyledContentCard>
      {isModalOpen ? (
        <ResetDataModal
          onClose={() => setIsModalOpen(false)}
          onSubmit={async () => {
            await onReset();
            setIsModalOpen(false);
          }}
        />
      ) : null}
    </Content>
  );
};

export default StatusView;
