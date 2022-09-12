import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useEffect, useState } from "react";
import { FormattedMessage } from "react-intl";

import { Button, ContentCard, LoadingButton } from "components";
import { Tooltip } from "components/base/Tooltip";
import EmptyResource from "components/EmptyResourceBlock";
import { RotateIcon } from "components/icons/RotateIcon";

import { getFrequencyType } from "config/utils";
import { Action, Namespace } from "core/analytics";
import { ConnectionStatus, JobWithAttemptsRead, WebBackendConnectionRead } from "core/request/AirbyteClient";
import Status from "core/statuses";
import { useTrackPage, PageTrackingCodes, useAnalyticsService } from "hooks/services/Analytics";
import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useResetConnection, useSyncConnection } from "hooks/services/useConnectionHook";
import { useCancelJob, useListJobs } from "services/job/JobService";

import JobsList from "./JobsList";
import styles from "./StatusView.module.scss";

const JOB_PAGE_SIZE_INCREMENT = 25;

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
  useTrackPage(PageTrackingCodes.CONNECTIONS_ITEM_STATUS);
  const [activeJob, setActiveJob] = useState<ActiveJob>();
  const [jobPageSize, setJobPageSize] = useState(JOB_PAGE_SIZE_INCREMENT);
  const analyticsService = useAnalyticsService();
  const { jobs, isPreviousData: isJobPageLoading } = useListJobs({
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
    pagination: {
      pageSize: jobPageSize,
    },
  });

  const moreJobPagesAvailable = jobs.length === jobPageSize;

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

  const onLoadMoreJobs = () => {
    setJobPageSize((prevJobPageSize) => prevJobPageSize + JOB_PAGE_SIZE_INCREMENT);

    analyticsService.track(Namespace.CONNECTION, Action.LOAD_MORE_JOBS, {
      actionDescription: "Load more jobs button was clicked",
      connection_id: connection.connectionId,
      connector_source: connection.source?.sourceName,
      connector_source_definition_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.destinationName,
      connector_destination_definition_id: connection.destination?.destinationDefinitionId,
      frequency: getFrequencyType(connection.schedule),
      job_page_size: jobPageSize,
    });
  };

  const cancelJobBtn = (
    <Button className={styles.cancelButton} disabled={!activeJob?.id || activeJob.isCanceling} onClick={onCancelJob}>
      <FontAwesomeIcon className={styles.iconXmark} icon={faXmark} />
      {activeJob?.action === ActionType.RESET && <FormattedMessage id="connection.cancelReset" />}
      {activeJob?.action === ActionType.SYNC && <FormattedMessage id="connection.cancelSync" />}
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
              <div className={styles.actions}>
                {!activeJob?.action && (
                  <>
                    <Button className={styles.resetButton} secondary onClick={onResetDataButtonClick}>
                      <FormattedMessage id="connection.resetData" />
                    </Button>
                    <Button className={styles.syncButton} disabled={!allowSync} onClick={onSyncNowButtonClick}>
                      <div className={styles.iconRotate}>
                        <RotateIcon />
                      </div>
                      <FormattedMessage id="sources.syncNow" />
                    </Button>
                  </>
                )}
                {activeJob?.action && !activeJob.isCanceling && cancelJobBtn}
                {activeJob?.action && activeJob.isCanceling && (
                  <Tooltip control={cancelJobBtn} cursor="not-allowed">
                    <FormattedMessage id="connection.canceling" />
                  </Tooltip>
                )}
              </div>
            )}
          </div>
        }
      >
        {jobs.length ? <JobsList jobs={jobs} /> : <EmptyResource text={<FormattedMessage id="sources.noSync" />} />}
      </ContentCard>

      {(moreJobPagesAvailable || isJobPageLoading) && (
        <footer className={styles.footer}>
          <LoadingButton isLoading={isJobPageLoading} onClick={onLoadMoreJobs}>
            <FormattedMessage id="connection.loadMoreJobs" />
          </LoadingButton>
        </footer>
      )}
    </div>
  );
};

export default StatusView;
