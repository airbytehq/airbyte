import React, { Suspense, useState } from "react";
import styled from "styled-components";

import { JobItem as JobApiItem, Attempt } from "core/resources/Job";
import Spinner from "../Spinner";
import JobLogs from "./components/JobLogs";
import ContentWrapper from "./components/ContentWrapper";
import MainInfo from "./components/MainInfo";
import Status from "core/statuses";

type IProps = {
  job: JobApiItem;
  attempts: Attempt[];
};

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

const JobItem: React.FC<IProps> = ({ job, attempts }) => {
  const [isOpen, setIsOpen] = useState(false);
  const onExpand = () => setIsOpen(!isOpen);
  const isFailed = job.status === Status.FAILED;

  return (
    <Item isFailed={isFailed}>
      <MainInfo
        isOpen={isOpen}
        isFailed={isFailed}
        onExpand={onExpand}
        job={job}
        attempts={attempts}
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
            {isOpen && <JobLogs id={job.id} jobIsFailed={isFailed} />}
          </Suspense>
        </div>
      </ContentWrapper>
    </Item>
  );
};

export default JobItem;
