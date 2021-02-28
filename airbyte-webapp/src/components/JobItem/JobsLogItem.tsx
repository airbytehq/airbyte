import React, { useState } from "react";
import styled from "styled-components";

import { JobInfo } from "core/resources/Scheduler";
import ContentWrapper from "./components/ContentWrapper";
import MainInfo from "./components/MainInfo";
import JobCurrentLogs from "./components/JobCurrenLogs";
import Status from "core/statuses";

type IProps = {
  jobInfo?: JobInfo;
};

const Item = styled.div<{ isFailed: boolean }>`
  border-top: 1px solid ${({ theme }) => theme.greyColor20};
  font-size: 15px;
  line-height: 18px;

  &:hover {
    background: ${({ theme, isFailed }) =>
      isFailed ? theme.dangerTransparentColor : theme.greyColor0};
  }
`;

const JobItem: React.FC<IProps> = ({ jobInfo }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!jobInfo || !jobInfo?.attempts?.length) {
    return null;
  }

  const onExpand = () => setIsOpen(!isOpen);
  const isFailed = jobInfo.job.status === Status.FAILED;
  const attempts = jobInfo.attempts.map((item) => item.attempt);

  return (
    <Item isFailed={isFailed}>
      <MainInfo
        shortInfo
        isOpen={isOpen}
        isFailed={isFailed}
        onExpand={onExpand}
        job={jobInfo.job}
        attempts={attempts}
      />
      <ContentWrapper isOpen={isOpen}>
        <div>
          {isOpen && (
            <JobCurrentLogs
              id={jobInfo.job.id}
              jobIsFailed={isFailed}
              attempts={jobInfo.attempts}
            />
          )}
        </div>
      </ContentWrapper>
    </Item>
  );
};

export default JobItem;
