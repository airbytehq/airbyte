import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import dayjs from "dayjs";

import { Attempt } from "core/domain/job/Job";
import Status from "core/statuses";

type IProps = {
  className?: string;
  attempt: Attempt;
  configType?: string;
};

const Details = styled.div`
  font-size: 12px;
  line-height: 15px;
  color: ${({ theme }) => theme.greyColor40};
`;

const AttemptDetails: React.FC<IProps> = ({
  attempt,
  className,
  configType,
}) => {
  if (attempt.status !== Status.SUCCEEDED && attempt.status !== Status.FAILED) {
    return (
      <Details className={className}>
        <FormattedMessage
          id={`sources.${configType}`}
          defaultMessage={configType}
        />
      </Details>
    );
  }

  const formatBytes = (bytes: number) => {
    if (!bytes) {
      return (
        <FormattedMessage id="sources.countBytes" values={{ count: bytes }} />
      );
    }

    const k = 1024;
    const dm = 2;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    const result = parseFloat((bytes / Math.pow(k, i)).toFixed(dm));

    return (
      <FormattedMessage
        id={`sources.count${sizes[i]}`}
        values={{ count: result }}
      />
    );
  };

  const date1 = dayjs(attempt.createdAt * 1000);
  const date2 = dayjs(attempt.updatedAt * 1000);
  const hours = Math.abs(date2.diff(date1, "hour"));
  const minutes = Math.abs(date2.diff(date1, "minute")) - hours * 60;
  const seconds =
    Math.abs(date2.diff(date1, "second")) - minutes * 60 - hours * 3600;

  return (
    <Details className={className}>
      <span>{formatBytes(attempt.bytesSynced)} | </span>
      <span>
        <FormattedMessage
          id="sources.countRecords"
          values={{ count: attempt.recordsSynced }}
        />{" "}
        |{" "}
      </span>
      <span>
        {hours ? (
          <FormattedMessage id="sources.hour" values={{ hour: hours }} />
        ) : null}
        {hours || minutes ? (
          <FormattedMessage id="sources.minute" values={{ minute: minutes }} />
        ) : null}
        <FormattedMessage id="sources.second" values={{ second: seconds }} />
      </span>
      {configType ? (
        <span>
          {" "}
          |{" "}
          <FormattedMessage
            id={`sources.${configType}`}
            defaultMessage={configType}
          />
        </span>
      ) : null}
    </Details>
  );
};

export default AttemptDetails;
