import React from "react";
import { useResource, useSubscription } from "rest-hooks";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import JobResource from "../../../../../core/resources/Job";

type IProps = {
  id: number;
};

const Logs = styled.div`
  padding: 20px 42px;
  font-size: 12px;
  line-height: 18px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  font-family: ${({ theme }) => theme.codeFont};
`;

const JobLogs: React.FC<IProps> = ({ id }) => {
  const job = useResource(JobResource.detailShape(), { id });
  useSubscription(JobResource.detailShape(), { id });

  if (!job.attempts.length) {
    return (
      <Logs>
        <FormattedMessage id="sources.emptyLogs" />
      </Logs>
    );
  }

  return (
    <Logs>
      {job.attempts[0].logs?.logLines.map((item, key) => (
        <div key={`log-${id}-${key}`}>{item}</div>
      ))}
    </Logs>
  );
};

export default JobLogs;
