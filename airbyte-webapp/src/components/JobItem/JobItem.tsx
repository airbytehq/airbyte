import React, { Suspense, useRef, useState } from "react";
import { useEffectOnce } from "react-use";
import styled from "styled-components";

import { Spinner } from "components";

import { SynchronousJobReadWithStatus } from "core/request/LogsRequestError";
import { JobsWithJobs } from "pages/ConnectionPage/pages/ConnectionItemPage/components/JobsList";

import { JobStatus } from "../../core/request/AirbyteClient";
import { useAttemptLink } from "./attemptLinkUtils";
import ContentWrapper from "./components/ContentWrapper";
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

type JobItemProps = {
  shortInfo?: boolean;
  job: SynchronousJobReadWithStatus | JobsWithJobs;
};

const didJobSucceed = (job: SynchronousJobReadWithStatus | JobsWithJobs) => {
  return getJobStatus(job) !== "failed";
};

export const getJobStatus: (job: SynchronousJobReadWithStatus | JobsWithJobs) => JobStatus = (job) => {
  return (job as JobsWithJobs).job?.status ?? (job as SynchronousJobReadWithStatus).status;
};

export const getJobId = (job: SynchronousJobReadWithStatus | JobsWithJobs) =>
  (job as SynchronousJobReadWithStatus).id ?? (job as JobsWithJobs).job.id;

export const JobItem: React.FC<JobItemProps> = ({ shortInfo, job }) => {
  const { jobId: linkedJobId } = useAttemptLink();
  const [isOpen, setIsOpen] = useState(linkedJobId === getJobId(job));
  const onExpand = () => setIsOpen(!isOpen);
  const scrollAnchor = useRef<HTMLDivElement>(null);

  const isFailed = didJobSucceed(job);

  useEffectOnce(() => {
    if (linkedJobId) {
      scrollAnchor.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });

  if (!job) {
    return null;
  }

  return (
    <Item isFailed={isFailed} ref={scrollAnchor}>
      <MainInfo shortInfo={shortInfo} isOpen={isOpen} isFailed={isFailed} onExpand={onExpand} job={job} />
      <ContentWrapper isOpen={isOpen}>
        <div>
          <Suspense
            fallback={
              <LoadLogs>
                <Spinner />
              </LoadLogs>
            }
          >
            {isOpen && <JobLogs job={job} jobIsFailed={isFailed} />}
          </Suspense>
        </div>
      </ContentWrapper>
    </Item>
  );
};
