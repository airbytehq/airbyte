import React, { Suspense, useRef, useState } from "react";
import { useEffectOnce } from "react-use";
import styled from "styled-components";

import { Spinner } from "components";

import Status from "core/statuses";

import { AttemptRead, JobStatus, JobWithAttemptsRead } from "../../core/request/GeneratedApi";
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

const isPartialSuccessCheck = (attempts?: AttemptRead[]) => {
  if (attempts && attempts.length > 0 && attempts[attempts.length - 1].status === Status.FAILED) {
    return attempts.some((attempt) => attempt.failureSummary && attempt.failureSummary.partialSuccess);
  } else {
    return false;
  }
};

type IProps = {
  shortInfo?: boolean;
  job: JobWithAttemptsRead;
};

export const JobItem: React.FC<IProps> = ({ shortInfo, job }) => {
  const { jobId: linkedJobId } = useAttemptLink();
  const [isOpen, setIsOpen] = useState(linkedJobId === String(job.job?.id));
  const onExpand = () => setIsOpen(!isOpen);
  const scrollAnchor = useRef<HTMLDivElement>(null);

  const isFailed = job.job?.status === JobStatus.failed;
  const isPartialSuccess = isPartialSuccessCheck(job.attempts);

  useEffectOnce(() => {
    if (linkedJobId) {
      scrollAnchor.current?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });

  if (!job.job) {
    return null;
  }

  return (
    <Item isFailed={isFailed} ref={scrollAnchor}>
      <MainInfo
        shortInfo={shortInfo}
        isOpen={isOpen}
        isFailed={isFailed}
        isPartialSuccess={isPartialSuccess}
        onExpand={onExpand}
        job={job.job}
        attempts={job.attempts}
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
            {isOpen && job.job.id ? <JobLogs id={job.job.id} jobIsFailed={isFailed} /> : null}
          </Suspense>
        </div>
      </ContentWrapper>
    </Item>
  );
};
