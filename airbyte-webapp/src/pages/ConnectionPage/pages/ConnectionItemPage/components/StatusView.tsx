import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, ContentCard, LoadingButton } from "components";
import EmptyResource from "components/EmptyResourceBlock";
import ToolTip from "components/ToolTip";

import { Connection, ConnectionStatus } from "core/domain/connection";
import Status from "core/statuses";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { FeatureItem, useFeatureService } from "hooks/services/Feature";
import { useResetConnection, useSyncConnection } from "hooks/services/useConnectionHook";
import useLoadingState from "hooks/useLoadingState";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useListJobs } from "services/job/JobService";

import JobsList from "./JobsList";
import { StatusMainInfo } from "./StatusMainInfo";

interface StatusViewProps {
  connection: Connection;
  frequencyText?: string;
}

const Content = styled.div`
  margin: 0 10px;
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

const StatusView: React.FC<StatusViewProps> = ({ connection, frequencyText }) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { isLoading, showFeedback, startAction } = useLoadingState();
  const { hasFeature } = useFeatureService();
  const allowSync = hasFeature(FeatureItem.AllowSync);

  const sourceDefinition = useSourceDefinition(connection?.source.sourceDefinitionId);

  const destinationDefinition = useDestinationDefinition(connection.destination.destinationDefinitionId);

  const jobs = useListJobs({
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
  });
  const isAtLeastOneJobRunningOrPending = jobs.some(
    ({ job: { status } }) => status === Status.RUNNING || status === Status.PENDING
  );

  const { mutateAsync: resetConnection } = useResetConnection();
  const { mutateAsync: syncConnection } = useSyncConnection();

  const onSync = () => syncConnection(connection);
  const onReset = () => resetConnection(connection.connectionId);

  const onResetDataButtonClick = () => {
    openConfirmationModal({
      text: `form.resetDataText`,
      title: `form.resetData`,
      submitButtonText: "form.reset",
      cancelButtonText: "form.noNeed",
      onSubmit: async () => {
        await onReset();
        closeConfirmationModal();
      },
      submitButtonDataId: "reset",
    });
  };

  const resetDataBtn = (
    <Button disabled={isAtLeastOneJobRunningOrPending} onClick={onResetDataButtonClick}>
      <FormattedMessage id={"connection.resetData"} />
    </Button>
  );

  const syncNowBtn = (
    <SyncButton
      disabled={!allowSync || isAtLeastOneJobRunningOrPending}
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
  );

  return (
    <Content>
      <StatusMainInfo
        connection={connection}
        frequencyText={frequencyText}
        sourceDefinition={sourceDefinition}
        destinationDefinition={destinationDefinition}
        allowSync={allowSync}
      />
      <StyledContentCard
        title={
          <Title>
            <FormattedMessage id={"sources.syncHistory"} />
            {connection.status === ConnectionStatus.ACTIVE && (
              <div>
                <ToolTip control={resetDataBtn} disabled={!isAtLeastOneJobRunningOrPending} cursor="not-allowed">
                  <FormattedMessage id={"connection.pendingSync"} />
                </ToolTip>
                <ToolTip control={syncNowBtn} disabled={!isAtLeastOneJobRunningOrPending} cursor="not-allowed">
                  <FormattedMessage id={"connection.pendingSync"} />
                </ToolTip>
              </div>
            )}
          </Title>
        }
      >
        {jobs.length ? <JobsList jobs={jobs} /> : <EmptyResource text={<FormattedMessage id="sources.noSync" />} />}
      </StyledContentCard>
    </Content>
  );
};

export default StatusView;
