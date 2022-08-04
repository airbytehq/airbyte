import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, ContentCard, LoadingButton } from "components";
import EmptyResource from "components/EmptyResourceBlock";
import ToolTip from "components/ToolTip";

import { ConnectionStatus, WebBackendConnectionRead } from "core/request/AirbyteClient";
import Status from "core/statuses";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useResetConnection, useSyncConnection } from "hooks/services/useConnectionHook";
import useLoadingState from "hooks/useLoadingState";
import { useListJobs } from "services/job/JobService";

import JobsList from "./JobsList";

interface StatusViewProps {
  connection: WebBackendConnectionRead;
  isStatusUpdating?: boolean;
}

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

const StatusView: React.FC<StatusViewProps> = ({ connection, isStatusUpdating }) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { isLoading, showFeedback, startAction } = useLoadingState();
  const allowSync = useFeature(FeatureItem.AllowSync);

  const jobs = useListJobs({
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
  });
  const isAtLeastOneJobRunningOrPending = jobs.some((jobWithAttempts) => {
    const status = jobWithAttempts?.job?.status;
    return status === Status.RUNNING || status === Status.PENDING;
  });

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
    <Button disabled={isAtLeastOneJobRunningOrPending || isStatusUpdating} onClick={onResetDataButtonClick}>
      <FormattedMessage id="connection.resetData" />
    </Button>
  );

  const syncNowBtn = (
    <SyncButton
      disabled={!allowSync || isAtLeastOneJobRunningOrPending || isStatusUpdating}
      isLoading={isLoading}
      wasActive={showFeedback}
      onClick={() => startAction({ action: onSync })}
    >
      {showFeedback ? (
        <FormattedMessage id="sources.syncingNow" />
      ) : (
        <>
          <TryArrow icon={faRedoAlt} />
          <FormattedMessage id="sources.syncNow" />
        </>
      )}
    </SyncButton>
  );

  return (
    <StyledContentCard
      title={
        <Title>
          <FormattedMessage id="sources.syncHistory" />
          {connection.status === ConnectionStatus.active && (
            <div>
              <ToolTip control={resetDataBtn} disabled={!isAtLeastOneJobRunningOrPending} cursor="not-allowed">
                <FormattedMessage id="connection.pendingSync" />
              </ToolTip>
              <ToolTip control={syncNowBtn} disabled={!isAtLeastOneJobRunningOrPending} cursor="not-allowed">
                <FormattedMessage id="connection.pendingSync" />
              </ToolTip>
            </div>
          )}
        </Title>
      }
    >
      {jobs.length ? <JobsList jobs={jobs} /> : <EmptyResource text={<FormattedMessage id="sources.noSync" />} />}
    </StyledContentCard>
  );
};

export default StatusView;
