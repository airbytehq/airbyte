import React, { Suspense, useCallback, useRef, useState } from "react";
import styled from "styled-components";

import { Spinner } from "components/ui/Spinner";

import { SynchronousJobRead } from "core/request/AirbyteClient";

import { useAttemptLink } from "./attemptLinkUtils";
import ContentWrapper from "./components/ContentWrapper";
import ErrorDetails from "./components/ErrorDetails";
import { JobLogs } from "./components/JobLogs";
import MainInfo from "./components/MainInfo";
import styles from "./JobItem.module.scss";
import { JobsWithJobs } from "./types";
import { didJobSucceed, getJobAttempts, getJobId } from "./utils";

const Item = styled.div<{ isFailed: boolean }>`
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  font-size: 15px;
  line-height: 18px;

  &:hover {
    background: ${({ theme, isFailed }) => (isFailed ? theme.dangerTransparentColor : theme.greyColor0)};
  }
`;

interface JobItemProps {
  job: SynchronousJobRead | JobsWithJobs;
}

export const JobItem: React.FC<JobItemProps> = ({ job }) => {
  const { jobId: linkedJobId } = useAttemptLink();
  const alreadyScrolled = useRef(false);
  const [isOpen, setIsOpen] = useState(() => linkedJobId === String(getJobId(job)));
  const scrollAnchor = useRef<HTMLDivElement>(null);

  const didSucceed = didJobSucceed(job);

  const onExpand = () => {
    setIsOpen((prevIsOpen) => !prevIsOpen);
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
      <MainInfo isOpen={isOpen} isFailed={!didSucceed} onExpand={onExpand} job={job} attempts={getJobAttempts(job)} />
      <ContentWrapper isOpen={isOpen} onToggled={onDetailsToggled}>
        <div>
          <Suspense
            fallback={
              <div className={styles.logsLoadingContainer}>
                <Spinner small />
              </div>
            }
          >
            {isOpen && (
              <>
                <ErrorDetails attempts={getJobAttempts(job)} />
                <JobLogs job={job} jobIsFailed={!didSucceed} />
              </>
            )}
          </Suspense>
        </div>
      </ContentWrapper>
    </Item>
  );
};
