import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import dayjs from "dayjs";

import { Attempt } from "../../../../../core/resources/Job";

type IProps = {
  attempt: Attempt;
};

const CompletedTime = styled.div`
  font-size: 12px;
  line-height: 15px;
  color: ${({ theme }) => theme.greyColor40};
`;

// TODO: add other data (size and records)
const AttemptDetails: React.FC<IProps> = ({ attempt }) => {
  const date1 = dayjs(attempt.createdAt * 1000);
  const date2 = dayjs(attempt.updatedAt * 1000);
  const hours = Math.abs(date2.diff(date1, "hour"));
  const minutes = Math.abs(date2.diff(date1, "minute")) - hours * 60;
  const seconds =
    Math.abs(date2.diff(date1, "second")) - minutes * 60 - hours * 3600;

  return (
    <CompletedTime>
      {hours ? (
        <FormattedMessage id="sources.hour" values={{ hour: hours }} />
      ) : null}
      {hours || minutes ? (
        <FormattedMessage id="sources.minute" values={{ minute: minutes }} />
      ) : null}
      <FormattedMessage id="sources.second" values={{ second: seconds }} />
    </CompletedTime>
  );
};

export default AttemptDetails;
