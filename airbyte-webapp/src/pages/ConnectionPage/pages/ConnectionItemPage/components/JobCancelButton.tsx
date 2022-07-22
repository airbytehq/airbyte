import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { LoadingButton } from "components";

import useLoadingState from "hooks/useLoadingState";
import { useCancelJob } from "services/job/JobService";

import styles from "./JobCancelButton.module.css";

const CancelButton = styled(LoadingButton)`
  margin-right: 10px;
  padding: 3px 7px;
  z-index: 1;
`;

interface JobCancelButtonProps {
  jobId?: number;
}

const JobCancelButton: React.FC<JobCancelButtonProps> = ({ children, jobId }) => {
  const { isLoading, showFeedback, startAction } = useLoadingState();
  const cancelJob = useCancelJob();

  const onCancelJob = (event: React.SyntheticEvent) => {
    event.stopPropagation();
    return jobId ? startAction({ action: () => cancelJob(jobId) }) : null;
  };

  return (
    <CancelButton
      danger={!showFeedback}
      disabled={isLoading}
      isLoading={isLoading}
      wasActive={showFeedback}
      onClick={onCancelJob}
    >
      {showFeedback ? (
        <FormattedMessage id="form.canceling" />
      ) : (
        <>
          <FontAwesomeIcon className={styles.icon} icon={faXmark} />
          {children}
        </>
      )}
    </CancelButton>
  );
};

export default JobCancelButton;
