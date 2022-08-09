import React, { Suspense, useCallback, useRef, useState } from "react";
import styled from "styled-components";

import { Spinner } from "components";

import { SynchronousJobReadWithStatus } from "core/request/LogsRequestError";
import { JobsWithJobs } from "pages/ConnectionPage/pages/ConnectionItemPage/components/JobsList";

import { AttemptRead, CheckConnectionReadStatus, JobStatus } from "../../core/request/AirbyteClient";
import { useAttemptLink } from "./attemptLinkUtils";
import ContentWrapper from "./components/ContentWrapper";
import ErrorDetails from "./components/ErrorDetails";
import JobLogs from "./components/JobLogs";
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

interface JobItemProps {
  job: SynchronousJobReadWithStatus | JobsWithJobs;
}

const didJobSucceed = (job: SynchronousJobReadWithStatus | JobsWithJobs) => {
  return getJobStatus(job) !== "failed";
};

export const getJobStatus: (
  job: SynchronousJobReadWithStatus | JobsWithJobs
) => JobStatus | CheckConnectionReadStatus = (job) => {
  return "status" in job ? job.status : job.job.status;
};

export const getJobAttemps: (job: SynchronousJobReadWithStatus | JobsWithJobs) => AttemptRead[] | undefined = (job) => {
  return "attempts" in job ? job.attempts : undefined;
};

export const getJobId = (job: SynchronousJobReadWithStatus | JobsWithJobs) => ("id" in job ? job.id : job.job.id);

export const JobItem: React.FC<JobItemProps> = ({ job }) => {
  const { jobId: linkedJobId } = useAttemptLink();
  const alreadyScrolled = useRef(false);
  const [isOpen, setIsOpen] = useState(() => linkedJobId === String(getJobId(job)));
  const scrollAnchor = useRef<HTMLDivElement>(null);

  const didSucceed = didJobSucceed(job);

  const onExpand = () => {
    setIsOpen(!isOpen);
  };

  const onDetailsToggled = useCallback(() => {
    if (alreadyScrolled.current || linkedJobId !== String(getJobId(job))) {
      return;
    }
    scrollAnchor.current?.scrollIntoView({
      block: "start",
    });
    alreadyScrolled.current = true;
  }, [job, linkedJobId]);

  return (
    <Item isFailed={!didSucceed} ref={scrollAnchor}>
      <MainInfo isOpen={isOpen} isFailed={!didSucceed} onExpand={onExpand} job={job} attempts={getJobAttemps(job)} />
      <ContentWrapper isOpen={isOpen} onToggled={onDetailsToggled}>
        <div>
          <Suspense
            fallback={
              <LoadLogs>
                <Spinner />
              </LoadLogs>
            }
          >
            {isOpen && (
              <>
                <ErrorDetails attempts={getJobAttemps(job)} />
                <JobLogs job={job} jobIsFailed={!didSucceed} />
              </>
            )}
          </Suspense>
        </div>
      </ContentWrapper>
    </Item>
  );
};
