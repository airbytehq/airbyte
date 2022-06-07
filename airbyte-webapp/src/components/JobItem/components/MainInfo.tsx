import { faAngleDown } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedDateParts, FormattedMessage, FormattedTimeParts } from "react-intl";
import styled from "styled-components";

import { LoadingButton, StatusIcon } from "components";
import { Cell, Row } from "components/SimpleTableComponents";

import { AttemptRead, JobStatus } from "core/request/AirbyteClient";
import { SynchronousJobReadWithStatus } from "core/request/LogsRequestError";
import useLoadingState from "hooks/useLoadingState";
import { JobsWithJobs } from "pages/ConnectionPage/pages/ConnectionItemPage/components/JobsList";
import { useCancelJob } from "services/job/JobService";

import { getJobId, getJobStatus } from "../JobItem";
import AttemptDetails from "./AttemptDetails";

const MainView = styled(Row)<{
  isOpen?: boolean;
  isFailed?: boolean;
}>`
  cursor: pointer;
  height: 75px;
  padding: 15px 44px 10px 40px;
  justify-content: space-between;
  border-bottom: 1px solid
    ${({ theme, isOpen, isFailed }) => (!isOpen ? "none" : isFailed ? theme.dangerTransparentColor : theme.greyColor20)};
`;

const Title = styled.div<{ isFailed?: boolean }>`
  position: relative;
  color: ${({ theme, isFailed }) => (isFailed ? theme.dangerColor : theme.darkPrimaryColor)};
`;

const ErrorSign = styled(StatusIcon)`
  position: absolute;
  left: -30px;
`;

const AttemptCount = styled.div`
  font-size: 12px;
  line-height: 15px;
  color: ${({ theme }) => theme.dangerColor};
`;

const CancelButton = styled(LoadingButton)`
  margin-right: 10px;
  padding: 3px 7px;
  z-index: 1;
`;

const InfoCell = styled(Cell)`
  flex: none;
`;

const Arrow = styled.div<{
  isOpen?: boolean;
  isFailed?: boolean;
}>`
  transform: ${({ isOpen }) => !isOpen && "rotate(-90deg)"};
  transition: 0.3s;
  font-size: 22px;
  line-height: 22px;
  height: 22px;
  color: ${({ theme, isFailed }) => (isFailed ? theme.dangerColor : theme.darkPrimaryColor)};
  position: absolute;
  right: 18px;
  top: calc(50% - 11px);
  opacity: 0;

  div:hover > div > &,
  div:hover > div > div > &,
  div:hover > & {
    opacity: 1;
  }
`;
const Text = styled.div`
  font-size: 12px;
  font-weight: bold;
  color: ${({ theme }) => theme.greyColor40};
`;

const getJobConfig = (job: SynchronousJobReadWithStatus | JobsWithJobs) =>
  (job as SynchronousJobReadWithStatus).configType ?? (job as JobsWithJobs).job.configType;

const getJobCreatedAt = (job: SynchronousJobReadWithStatus | JobsWithJobs) =>
  (job as SynchronousJobReadWithStatus).createdAt ?? (job as JobsWithJobs).job.createdAt;

interface MainInfoProps {
  job: SynchronousJobReadWithStatus | JobsWithJobs;
  attempts?: AttemptRead[];
  isOpen?: boolean;
  onExpand: () => void;
  isFailed?: boolean;
  isPartialSuccess?: boolean;
  shortInfo?: boolean;
}

const MainInfo: React.FC<MainInfoProps> = ({
  job,
  attempts = [],
  isOpen,
  onExpand,
  isFailed,
  shortInfo,
  isPartialSuccess,
}) => {
  const { isLoading, showFeedback, startAction } = useLoadingState();
  const cancelJob = useCancelJob();

  const onCancelJob = (event: React.SyntheticEvent) => {
    event.stopPropagation();
    const jobId = Number(getJobId(job));
    return startAction({ action: () => cancelJob(jobId) });
  };

  const jobStatus = getJobStatus(job);
  const isNotCompleted =
    jobStatus === JobStatus.pending || jobStatus === JobStatus.running || jobStatus === JobStatus.incomplete;

  const jobStatusLabel = isPartialSuccess ? (
    <FormattedMessage id="sources.partialSuccess" />
  ) : (
    <FormattedMessage id={`sources.${getJobStatus(job)}`} />
  );

  const getIcon = () => {
    if (isPartialSuccess) {
      return <ErrorSign status="warning" />;
    } else if (isFailed && !shortInfo) {
      return <ErrorSign />;
    }
    return null;
  };

  return (
    <MainView isOpen={isOpen} isFailed={isFailed} onClick={onExpand}>
      <InfoCell>
        <Title isFailed={isFailed}>
          {getIcon()}
          {jobStatusLabel}
          {shortInfo ? <FormattedMessage id="sources.additionLogs" /> : null}
          {attempts.length && !shortInfo ? (
            <div>
              {attempts.length > 1 && (
                <Text>
                  <FormattedMessage id="sources.lastAttempt" />
                </Text>
              )}
              <AttemptDetails attempt={attempts[attempts.length - 1]} configType={getJobConfig(job)} />
            </div>
          ) : null}
        </Title>
      </InfoCell>
      <InfoCell>
        {!shortInfo && isNotCompleted && (
          <CancelButton
            secondary
            disabled={isLoading}
            isLoading={isLoading}
            wasActive={showFeedback}
            onClick={onCancelJob}
          >
            <FormattedMessage id={showFeedback ? "form.canceling" : "form.cancel"} />
          </CancelButton>
        )}
        <FormattedTimeParts value={getJobCreatedAt(job) * 1000} hour="numeric" minute="2-digit">
          {(parts) => <span>{`${parts[0].value}:${parts[2].value}${parts[4].value} `}</span>}
        </FormattedTimeParts>
        <FormattedDateParts value={getJobCreatedAt(job) * 1000} month="2-digit" day="2-digit">
          {(parts) => <span>{`${parts[0].value}/${parts[2].value}`}</span>}
        </FormattedDateParts>
        {attempts.length > 1 && (
          <AttemptCount>
            <FormattedMessage id="sources.countAttempts" values={{ count: attempts.length }} />
          </AttemptCount>
        )}
        <Arrow isOpen={isOpen} isFailed={isFailed}>
          <FontAwesomeIcon icon={faAngleDown} />
        </Arrow>
      </InfoCell>
    </MainView>
  );
};

export default MainInfo;
