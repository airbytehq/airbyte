import { faRedoAlt, faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { Button, ContentCard } from "components";
import EmptyResource from "components/EmptyResourceBlock";
import ToolTip from "components/ToolTip";

import { ConnectionStatus, WebBackendConnectionRead } from "core/request/AirbyteClient";
import Status from "core/statuses";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useResetConnection, useSyncConnection } from "hooks/services/useConnectionHook";
import { useCancelJob, useListJobs } from "services/job/JobService";

import JobsList from "./JobsList";
import styles from "./StatusView.module.scss";

interface StatusViewProps {
  connection: WebBackendConnectionRead;
  isStatusUpdating?: boolean;
}

enum CurrentActionType {
  RESET = "reset_connection",
  SYNC = "sync",
}

const StatusView: React.FC<StatusViewProps> = ({ connection }) => {
  const jobs = useListJobs({
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
  });

  const jobRunningOrPending = jobs.find((jobWithAttempts) => {
    const jobStatus = jobWithAttempts?.job?.status;
    return jobStatus === Status.PENDING || jobStatus === Status.RUNNING || jobStatus === Status.INCOMPLETE;
  });

  const [jobCancelling, setJobCancelling] = useState<boolean>();
  const [currentAction, setCurrentAction] = useState<CurrentActionType | null>(
    (jobRunningOrPending?.job?.configType || null) as CurrentActionType
  );

  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();

  const allowSync = useFeature(FeatureItem.AllowSync);
  const cancelJob = useCancelJob();

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
    return onSync();
  };

  const onCancelJob = async () => {
    if (!jobRunningOrPending?.job?.id) {
      return;
    }
    setJobCancelling(true);
    await cancelJob(jobRunningOrPending?.job?.id);
    setJobCancelling(false);
  };

  const cancelJobBtn = (
    <Button className={styles.cancelButton} disabled={jobCancelling} onClick={onCancelJob}>
      <FontAwesomeIcon className={styles.iconXmark} icon={faXmark} />
      {currentAction === CurrentActionType.RESET && <FormattedMessage id="connection.cancelReset" />}
      {currentAction === CurrentActionType.SYNC && <FormattedMessage id="connection.cancelSync" />}
    </Button>
  );

  const resetDataBtn = (
    <Button className={styles.resetButton} secondary onClick={onResetDataButtonClick}>
      <FormattedMessage id="connection.resetData" />
    </Button>
  );

  const syncNowBtn = (
    <Button className={styles.syncButton} disabled={!allowSync} onClick={onSyncNowButtonClick}>
      <FontAwesomeIcon className={styles.iconRedoAlt} icon={faRedoAlt} />
      <FormattedMessage id="sources.syncNow" />
    </Button>
  );

  return (
    <div className={styles.statusView}>
      <ContentCard
        className={styles.contentCard}
        title={
          <div className={styles.title}>
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
                {jobRunningOrPending && !jobCancelling && cancelJobBtn}
                {jobRunningOrPending && jobCancelling && (
                  <ToolTip control={cancelJobBtn} cursor="not-allowed">
                    <FormattedMessage id="form.canceling" />
                  </ToolTip>
                )}
              </div>
            )}
          </div>
        }
      >
        {jobs.length ? <JobsList jobs={jobs} /> : <EmptyResource text={<FormattedMessage id="sources.noSync" />} />}
      </ContentCard>
    </div>
  );
};

export default StatusView;
