import React, { Suspense, useState } from "react";
import pose from "react-pose";
import {
  FormattedMessage,
  FormattedDateParts,
  FormattedTimeParts
} from "react-intl";
import styled from "styled-components";
import dayjs from "dayjs";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAngleDown } from "@fortawesome/free-solid-svg-icons";

import { Job } from "../../../core/resources/Job";
import { Row, Cell } from "../../../components/SimpleTableComponents";
import StatusIcon from "../../../components/StatusIcon";
import Spinner from "../../../components/Spinner";
import JobLogs from "./JobLogs";

type IProps = {
  job: Job;
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

const MainInfo = styled(Row)<{
  isOpen?: boolean;
  isFailed?: boolean;
}>`
  cursor: pointer;
  height: 59px;
  padding: 10px 44px 10px 40px;
  border-bottom: 1px solid
    ${({ theme, isOpen, isFailed }) =>
      !isOpen
        ? "none"
        : isFailed
        ? theme.dangerTransparentColor
        : theme.greyColor20};
`;

const Title = styled.div<{ isFailed: boolean }>`
  position: relative;
  color: ${({ theme, isFailed }) =>
    isFailed ? theme.dangerColor : theme.darkPrimaryColor};
`;

const ErrorSign = styled(StatusIcon)`
  position: absolute;
  left: -30px;
`;

const LoadLogs = styled.div`
  background: ${({ theme }) => theme.whiteColor};
  text-align: center;
  padding: 6px 0;
  min-height: 58px;
`;

const CompletedTime = styled.div`
  font-size: 12px;
  line-height: 15px;
  color: ${({ theme }) => theme.greyColor40};
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
  color: ${({ theme, isFailed }) =>
    isFailed ? theme.dangerColor : theme.darkPrimaryColor};
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

const itemConfig = {
  open: {
    height: "auto",
    opacity: 1,
    transition: "tween"
  },
  closed: {
    height: "1px",
    opacity: 0,
    transition: "tween"
  }
};

const ContentWrapper = pose.div(itemConfig);

const JobItem: React.FC<IProps> = ({ job }) => {
  const [isOpen, setIsOpen] = useState(false);
  const onExpand = () => setIsOpen(!isOpen);

  const date1 = dayjs(job.createdAt * 1000);
  const date2 = dayjs(job.updatedAt * 1000);
  const hours = Math.abs(date2.diff(date1, "hour"));
  const minutes = Math.abs(date2.diff(date1, "minute")) - hours * 60;
  const seconds =
    Math.abs(date2.diff(date1, "second")) - minutes * 60 - hours * 3600;

  const isFailed = job.status === "failed";
  return (
    <Item isFailed={isFailed}>
      <MainInfo isOpen={isOpen} isFailed={isFailed} onClick={onExpand}>
        <Cell>
          <Title isFailed={isFailed}>
            {isFailed && <ErrorSign />}
            <FormattedMessage id={`sources.${job.status}`} />
          </Title>
        </Cell>
        <Cell>
          <FormattedTimeParts
            value={job.createdAt * 1000}
            hour="numeric"
            minute="2-digit"
          >
            {parts => (
              <span>{`${parts[0].value}:${parts[2].value}${parts[4].value} `}</span>
            )}
          </FormattedTimeParts>
          <FormattedDateParts
            value={job.createdAt * 1000}
            month="2-digit"
            day="2-digit"
          >
            {parts => <span>{`${parts[0].value}/${parts[2].value}`}</span>}
          </FormattedDateParts>
          <CompletedTime>
            {hours ? (
              <FormattedMessage id="sources.hour" values={{ hour: hours }} />
            ) : null}
            {hours || minutes ? (
              <FormattedMessage
                id="sources.minute"
                values={{ minute: minutes }}
              />
            ) : null}
            <FormattedMessage
              id="sources.second"
              values={{ second: seconds }}
            />
          </CompletedTime>
          <Arrow isOpen={isOpen} isFailed={isFailed}>
            <FontAwesomeIcon icon={faAngleDown} />
          </Arrow>
        </Cell>
      </MainInfo>
      <ContentWrapper pose={!isOpen ? "closed" : "open"} withParent={false}>
        <div>
          <Suspense
            fallback={
              <LoadLogs>
                <Spinner />
              </LoadLogs>
            }
          >
            {isOpen && <JobLogs id={job.id} />}
          </Suspense>
        </div>
      </ContentWrapper>
    </Item>
  );
};

export default JobItem;
