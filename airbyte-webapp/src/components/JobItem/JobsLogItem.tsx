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

const JobsLogItem: React.FC<IProps> = ({ jobInfo }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!jobInfo) {
    return null;
  }

  const onExpand = () => setIsOpen(!isOpen);
  const isFailed = jobInfo.status === Status.FAILED;

  return (
    <Item isFailed={isFailed}>
      <MainInfo
        shortInfo
        isOpen={isOpen}
        isFailed={isFailed}
        onExpand={onExpand}
        job={jobInfo}
        attempts={[]}
      />
      <ContentWrapper isOpen={isOpen}>
        <div>
          {isOpen && (
            <JobCurrentLogs
              id={jobInfo.id}
              jobIsFailed={isFailed}
              attempts={[]}
              logs={jobInfo.logs}
            />
          )}
        </div>
      </ContentWrapper>
    </Item>
  );
};

export default JobsLogItem;
