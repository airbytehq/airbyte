import React from "react";
import { useResource } from "rest-hooks";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import JobResource from "../../../../../core/resources/Job";

type IProps = {
  id: number;
};

const Logs = styled.div`
  padding: 20px 42px;
  font-size: 15px;
  line-height: 18px;
  color: ${({ theme }) => theme.darkPrimaryColor};
`;

const JobLogs: React.FC<IProps> = ({ id }) => {
  const job = useResource(JobResource.detailShape(), { id });

  if (!job.logs.logLines.length) {
    return (
      <Logs>
        <FormattedMessage id="sources.emptyLogs" />
      </Logs>
    );
  }

  // now logs always empty. TODO: Test ui with data
  return (
    <Logs>
      {job.logs.logLines.map((item, key) => (
        <div key={`log-${id}-${key}`}>{item}</div>
      ))}
    </Logs>
  );
};

export default JobLogs;
