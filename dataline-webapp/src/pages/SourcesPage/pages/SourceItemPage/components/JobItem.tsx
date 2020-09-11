import React from "react";
import {
  FormattedMessage,
  FormattedDateParts,
  FormattedTimeParts
} from "react-intl";
import styled from "styled-components";

import { Job } from "../../../../../core/resources/Job";
import { Row, Cell } from "../../../../../components/SimpleTableComponents";
import StatusIcon from "../../../../../components/StatusIcon";

type IProps = {
  job: Job;
};

const Item = styled(Row)`
  height: 59px;
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  padding: 10px 44px 10px 40px;
  font-size: 15px;
  line-height: 18px;
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

const JobItem: React.FC<IProps> = ({ job }) => {
  const isFailed = job.status === "failed";
  return (
    <Item>
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
      </Cell>
    </Item>
  );
};

export default JobItem;
