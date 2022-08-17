import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";

import { Button, ContentCard, ButtonType } from "components";
import EmptyResource from "components/EmptyResourceBlock";
import { RotateIcon } from "components/icons/RotateIcon";
import ToolTip from "components/ToolTip";

import { ConnectionStatus, JobWithAttemptsRead, WebBackendConnectionRead } from "core/request/AirbyteClient";
import Status from "core/statuses";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useResetConnection, useSyncConnection } from "hooks/services/useConnectionHook";
import { useCancelJob, useListJobs } from "services/job/JobService";

import JobsList from "./JobsList";
import styles from "./StatusView.module.scss";

enum ActionType {
  RESET = "reset_connection",
  SYNC = "sync",
}

interface ActiveJob {
  id: number;
  action: ActionType;
  isCanceling: boolean;
}

interface StatusViewProps {
  connection: WebBackendConnectionRead;
  isStatusUpdating?: boolean;
}

const getJobRunningOrPending = (jobs: JobWithAttemptsRead[]) => {
  return jobs.find((jobWithAttempts) => {
    const jobStatus = jobWithAttempts?.job?.status;
    return jobStatus === Status.PENDING || jobStatus === Status.RUNNING || jobStatus === Status.INCOMPLETE;
  });
};

const StatusView: React.FC<StatusViewProps> = ({ connection }) => {
  const [activeJob, setActiveJob] = useState<ActiveJob>();

  const jobs = useListJobs({
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
  });

  useEffect(() => {
    const jobRunningOrPending = getJobRunningOrPending(jobs);

    setActiveJob(
      (state) =>
        ({
          id: jobRunningOrPending?.job?.id,
          action: jobRunningOrPending?.job?.configType,
          isCanceling: state?.isCanceling && !!jobRunningOrPending,
          // We need to disable button when job is canceled but the job list still has a running job
        } as ActiveJob)
    );
  }, [jobs]);

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
        setActiveJob((state) => ({ ...state, action: ActionType.RESET } as ActiveJob));
        closeConfirmationModal();
      },
      submitButtonDataId: "reset",
    });
  };

  const onSyncNowButtonClick = () => {
    setActiveJob((state) => ({ ...state, action: ActionType.SYNC } as ActiveJob));
    return onSync();
  };

  const onCancelJob = () => {
    if (!activeJob?.id) {
      return;
    }
    setActiveJob((state) => ({ ...state, isCanceling: true } as ActiveJob));
    return cancelJob(activeJob.id);
  };
  let label = null;
  if (activeJob?.action === ActionType.RESET) {
    label = <FormattedMessage id="connection.cancelReset" />;
  }
  if (activeJob?.action === ActionType.SYNC) {
    label = <FormattedMessage id="connection.cancelSync" />;
  }
  const cancelJobBtn = (
    <Button
      className={styles.cancelButton}
      disabled={!activeJob?.id || activeJob.isCanceling}
      onClick={onCancelJob}
      icon={<FontAwesomeIcon className={styles.iconXmark} icon={faXmark} />}
      label={label}
    />
  );

  return (
    <div className={styles.statusView}>
      <ContentCard
        className={styles.contentCard}
        title={
          <div className={styles.title}>
            <FormattedMessage id="sources.syncHistory" />
            {connection.status === ConnectionStatus.active && (
              <div className={styles.actions}>
                {!activeJob?.action && (
                  <>
                    <Button
                      className={styles.resetButton}
                      buttonType={ButtonType.Secondary}
                      onClick={onResetDataButtonClick}
                      label={<FormattedMessage id="connection.resetData" />}
                    />
                    <Button
                      className={styles.syncButton}
                      disabled={!allowSync}
                      onClick={onSyncNowButtonClick}
                      icon={
                        <div className={styles.iconRotate}>
                          <RotateIcon />
                        </div>
                      }
                      label={<FormattedMessage id="sources.syncNow" />}
                    />
                  </>
                )}
                {activeJob?.action && !activeJob.isCanceling && cancelJobBtn}
                {activeJob?.action && activeJob.isCanceling && (
                  <ToolTip control={cancelJobBtn} cursor="not-allowed">
                    <FormattedMessage id="connection.canceling" />
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
