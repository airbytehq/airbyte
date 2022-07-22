import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
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

import JobCancelButton from "./JobCancelButton";
import JobsList from "./JobsList";

interface StatusViewProps {
  connection: WebBackendConnectionRead;
  isStatusUpdating?: boolean;
}

enum CurrentActionType {
  RESET = "reset",
  SYNC = "sync",
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

const StatusView: React.FC<StatusViewProps> = ({ connection, isStatusUpdating }) => {
  const [currentAction, setCurrentAction] = useState<CurrentActionType>();
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { isLoading, showFeedback, startAction } = useLoadingState();
  const allowSync = useFeature(FeatureItem.AllowSync);

  const jobs = useListJobs({
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
  });

  const jobRunningOrPending = jobs.find((jobWithAttempts) => {
    const jobStatus = jobWithAttempts?.job?.status;
    return jobStatus === Status.PENDING || jobStatus === Status.RUNNING || jobStatus === Status.INCOMPLETE;
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
        setCurrentAction(CurrentActionType.RESET);
      },
      submitButtonDataId: "reset",
    });
  };

  const onSyncNowButtonClick = () => {
    setCurrentAction(CurrentActionType.SYNC);
    return startAction({ action: onSync });
  };

  const resetDataBtn = (
    <Button disabled={isStatusUpdating} onClick={onResetDataButtonClick}>
      <FormattedMessage id="connection.resetData" />
    </Button>
  );

  const syncNowBtn = (
    <SyncButton
      disabled={!allowSync || isStatusUpdating}
      isLoading={isLoading}
      wasActive={showFeedback}
      onClick={onSyncNowButtonClick}
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
    <Content>
      <StyledContentCard
        title={
          <Title>
            <FormattedMessage id="sources.syncHistory" />
            {connection.status === ConnectionStatus.active && (
              <div>
                {!jobRunningOrPending && (
                  <>
                    <ToolTip control={resetDataBtn} cursor="not-allowed">
                      <FormattedMessage id="connection.pendingSync" />
                    </ToolTip>
                    <ToolTip control={syncNowBtn} cursor="not-allowed">
                      <FormattedMessage id="connection.pendingSync" />
                    </ToolTip>
                  </>
                )}
                {jobRunningOrPending && (
                  <JobCancelButton jobId={jobRunningOrPending.job?.id}>
                    {currentAction === CurrentActionType.RESET && <FormattedMessage id="connection.cancelReset" />}
                    {currentAction === CurrentActionType.SYNC && <FormattedMessage id="connection.cancelSync" />}
                  </JobCancelButton>
                )}
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
