import React, { Suspense, useState } from "react";
import styled from "styled-components";

import { Spinner } from "components";

import { JobInfo, JobListItem, Logs, Attempt } from "core/domain/job/Job";
import Status from "core/statuses";

import JobLogs from "./components/JobLogs";
import ContentWrapper from "./components/ContentWrapper";
import MainInfo from "./components/MainInfo";
import { LogsDetails } from "./components/LogsDetails";

const Item = styled.div<{ isFailed: boolean }>`
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  font-size: 15px;
  line-height: 18px;

  &:hover {
    background: ${({ theme, isFailed }) =>
      isFailed ? theme.dangerTransparentColor : theme.greyColor0};
  }
`;

const LoadLogs = styled.div`
  background: ${({ theme }) => theme.whiteColor};
  text-align: center;
  padding: 6px 0;
  min-height: 58px;
`;

const isJobEntity = (
  props: { job: JobListItem } | { jobInfo: JobInfo }
): props is { job: JobListItem } => {
  return props.hasOwnProperty("job");
};

const JobCurrentLogs: React.FC<{
  id: number | string;
  jobIsFailed?: boolean;
  logs?: Logs;
}> = (props) => {
  const path = ["/tmp/workspace", props.id, "logs.log"].join("/");

  return <LogsDetails {...props} path={path} />;
};

const isPartialSuccessCheck = (attempts: Attempt[]) => {
  if (
    attempts.length > 0 &&
    attempts[attempts.length - 1].status === Status.FAILED
  ) {
    return attempts.some(
      (attempt) =>
        attempt.failureSummary && attempt.failureSummary.partialSuccess
    );
  } else {
    return false;
  }
};

type IProps = {
  shortInfo?: boolean;
} & ({ job: JobListItem } | { jobInfo: JobInfo });

const JobItem: React.FC<IProps> = ({ shortInfo, ...props }) => {
  const [isOpen, setIsOpen] = useState(false);
  const onExpand = () => setIsOpen(!isOpen);

  const jobMeta = isJobEntity(props) ? props.job.job : props.jobInfo;
  const isFailed = jobMeta.status === Status.FAILED;
  const isPartialSuccess = isJobEntity(props)
    ? isPartialSuccessCheck(props.job.attempts)
    : undefined;

  return (
    <Item isFailed={isFailed}>
      <MainInfo
        shortInfo={shortInfo}
        isOpen={isOpen}
        isFailed={isFailed}
        isPartialSuccess={isPartialSuccess}
        onExpand={onExpand}
        job={jobMeta}
        attempts={isJobEntity(props) ? props.job.attempts : undefined}
      />
      <ContentWrapper isOpen={isOpen}>
        <div>
          <Suspense
            fallback={
              <LoadLogs>
                <Spinner />
              </LoadLogs>
            }
          >
            {isOpen ? (
              isJobEntity(props) ? (
                <JobLogs
                  id={jobMeta.id}
                  jobIsFailed={isFailed}
                  isPartialSuccess={isPartialSuccess}
                />
              ) : (
                <JobCurrentLogs
                  id={jobMeta.id}
                  jobIsFailed={isFailed}
                  logs={props.jobInfo.logs}
                />
              )
            ) : null}
          </Suspense>
        </div>
      </ContentWrapper>
    </Item>
  );
};

export default JobItem;
