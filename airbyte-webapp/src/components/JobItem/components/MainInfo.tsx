import React from "react";
import {
  FormattedMessage,
  FormattedDateParts,
  FormattedTimeParts,
} from "react-intl";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faAngleDown } from "@fortawesome/free-solid-svg-icons";

import { JobItem as JobApiItem, Attempt } from "core/resources/Job";
import { JobInfo } from "core/resources/Scheduler";
import { Row, Cell } from "components/SimpleTableComponents";
import { Button, StatusIcon } from "components";
import AttemptDetails from "./AttemptDetails";
import Status from "core/statuses";
import useJob from "components/hooks/services/useJob";

type IProps = {
  job: JobApiItem | JobInfo;
  attempts: Attempt[];
  isOpen?: boolean;
  onExpand: () => void;
  isFailed?: boolean;
  shortInfo?: boolean;
};

const MainView = styled(Row)<{
  isOpen?: boolean;
  isFailed?: boolean;
}>`
  cursor: pointer;
  height: 59px;
  padding: 10px 44px 10px 40px;
  justify-content: space-between;
  border-bottom: 1px solid
    ${({ theme, isOpen, isFailed }) =>
      !isOpen
        ? "none"
        : isFailed
        ? theme.dangerTransparentColor
        : theme.greyColor20};
`;

const Title = styled.div<{ isFailed?: boolean }>`
  position: relative;
  color: ${({ theme, isFailed }) =>
    isFailed ? theme.dangerColor : theme.darkPrimaryColor};
`;

const ErrorSign = styled(StatusIcon)`
  position: absolute;
  left: -30px;
`;

const AttemptCount = styled.div`
  font-size: 12px;
  line-height: 15px;
  color: ${({ theme }) => theme.dangerColor};
`;

const CancelButton = styled(Button)`
  margin-right: 10px;
  padding: 3px 7px;
  z-index: 1;
`;

const InfoCell = styled(Cell)`
  flex: none;
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

const MainInfo: React.FC<IProps> = ({
  job,
  attempts,
  isOpen,
  onExpand,
  isFailed,
  shortInfo,
}) => {
  const { cancelJob } = useJob();

  const onCancelJob = (event: React.SyntheticEvent) => {
    event.stopPropagation();
    cancelJob(job.id);
  };

  const isNotCompleted =
    job.status &&
    [Status.PENDING, Status.RUNNING, Status.INCOMPLETE].includes(job.status);

  return (
    <MainView isOpen={isOpen} isFailed={isFailed} onClick={onExpand}>
      <InfoCell>
        <Title isFailed={isFailed}>
          {isFailed && !shortInfo && <ErrorSign />}
          <FormattedMessage id={`sources.${job.status}`} />
          {shortInfo ? <FormattedMessage id="sources.additionLogs" /> : null}
          {attempts.length && !shortInfo ? (
            <AttemptDetails
              attempt={attempts[attempts.length - 1]}
              configType={job.configType}
            />
          ) : null}
        </Title>
      </InfoCell>
      <InfoCell>
        {!shortInfo && isNotCompleted && (
          <CancelButton secondary onClick={onCancelJob}>
            <FormattedMessage id="form.cancel" />
          </CancelButton>
        )}
        <FormattedTimeParts
          value={job.createdAt * 1000}
          hour="numeric"
          minute="2-digit"
        >
          {(parts) => (
            <span>{`${parts[0].value}:${parts[2].value}${parts[4].value} `}</span>
          )}
        </FormattedTimeParts>
        <FormattedDateParts
          value={job.createdAt * 1000}
          month="2-digit"
          day="2-digit"
        >
          {(parts) => <span>{`${parts[0].value}/${parts[2].value}`}</span>}
        </FormattedDateParts>
        {attempts.length > 1 ? (
          <AttemptCount>
            <FormattedMessage
              id="sources.countAttempts"
              values={{ count: attempts.length }}
            />
          </AttemptCount>
        ) : null}
        <Arrow isOpen={isOpen} isFailed={isFailed}>
          <FontAwesomeIcon icon={faAngleDown} />
        </Arrow>
      </InfoCell>
    </MainView>
  );
};

export default MainInfo;
