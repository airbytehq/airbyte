import React, { Suspense, useRef, useState } from "react";
import { useEffectOnce } from "react-use";
import styled from "styled-components";

import { Spinner } from "components";

import { JobInfo, JobListItem, Logs, Attempt } from "core/domain/job/Job";
import Status from "core/statuses";

import { useAttemptLink } from "./attemptLinkUtils";
import ContentWrapper from "./components/ContentWrapper";
import JobLogs from "./components/JobLogs";
import { LogsDetails } from "./components/LogsDetails";
import MainInfo from "./components/MainInfo";

const Item = styled.div<{ isFailed: boolean }>`
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  font-size: 15px;
  line-height: 18px;

  &:hover {
    background: ${({ theme, isFailed }) => (isFailed ? theme.dangerTransparentColor : theme.greyColor0)};
  }
`;

const LoadLogs = styled.div`
  background: ${({ theme }) => theme.whiteColor};
  text-align: center;
  padding: 6px 0;
  min-height: 58px;
`;

const isJobEntity = (props: { job: JobListItem } | { jobInfo: JobInfo }): props is { job: JobListItem } => {
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
  if (attempts.length > 0 && attempts[attempts.length - 1].status === Status.FAILED) {
    return attempts.some((attempt) => attempt.failureSummary && attempt.failureSummary.partialSuccess);
  } else {
    return false;
  }
};

type IProps = {
  shortInfo?: boolean;
} & ({ job: JobListItem } | { jobInfo: JobInfo });

const JobItem: React.FC<IProps> = ({ shortInfo, ...props }) => {
  const jobMeta = isJobEntity(props) ? props.job.job : props.jobInfo;
  const { jobId: linkedJobId } = useAttemptLink();
  const [isOpen, setIsOpen] = useState(linkedJobId === String(jobMeta.id));
  const onExpand = () => setIsOpen(!isOpen);
  const scrollAnchor = useRef<HTMLDivElement>(null);

  const isFailed = jobMeta.status === Status.FAILED;
  const isPartialSuccess = isJobEntity(props) ? isPartialSuccessCheck(props.job.attempts) : undefined;

  useEffectOnce(() => {
    if (linkedJobId) {
      scrollAnchor.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });

  return (
    <Item isFailed={isFailed} ref={scrollAnchor}>
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
                <JobLogs id={jobMeta.id} jobIsFailed={isFailed} />
              ) : (
                <JobCurrentLogs id={jobMeta.id} jobIsFailed={isFailed} logs={props.jobInfo.logs} />
              )
            ) : null}
          </Suspense>
        </div>
      </ContentWrapper>
    </Item>
  );
};

export default JobItem;
