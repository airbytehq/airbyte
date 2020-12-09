import React, { useState } from "react";
import { useResource, useSubscription } from "rest-hooks";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import JobResource from "../../../../../core/resources/Job";
import StepsMenu from "../../../../../components/StepsMenu";
import AttemptDetails from "./AttemptDetails";

type IProps = {
  id: number;
  jobIsFailed?: boolean;
};

const Logs = styled.div`
  padding: 15px 42px 20px;
  font-size: 12px;
  line-height: 18px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  font-family: ${({ theme }) => theme.codeFont};
`;

const Tabs = styled.div<{ isFailed?: boolean }>`
  padding: 6px 0;
  border-bottom: 1px solid
    ${({ theme, isFailed }) =>
      isFailed ? theme.dangerTransparentColor : theme.greyColor20};
`;

const CenteredAttemptDetails = styled(AttemptDetails)`
  text-align: center;
  padding-top: 9px;
`;

const JobLogs: React.FC<IProps> = ({ id, jobIsFailed }) => {
  const job = useResource(JobResource.detailShape(), { id });
  useSubscription(JobResource.detailShape(), { id });

  const [attemptNumber, setAttemptNumber] = useState<any>(
    job.attempts.length ? job.attempts.length - 1 : 0
  );

  if (!job.attempts.length) {
    return (
      <Logs>
        <FormattedMessage id="sources.emptyLogs" />
      </Logs>
    );
  }

  const data = job.attempts.map((item, key: any) => ({
    id: key,
    status: item.status,
    name: (
      <FormattedMessage id="sources.attemptNum" values={{ number: key + 1 }} />
    )
  }));

  return (
    <>
      {job.attempts.length > 1 ? (
        <>
          <Tabs isFailed={jobIsFailed}>
            <StepsMenu
              lightMode
              activeStep={attemptNumber}
              onSelect={setAttemptNumber}
              data={data}
            />
          </Tabs>
          <CenteredAttemptDetails attempt={job.attempts[attemptNumber]} />
        </>
      ) : null}

      <Logs>
        {job.logsByAttempt[attemptNumber]?.logLines?.length ? (
          job.logsByAttempt[attemptNumber].logLines.map((item, key) => (
            <div key={`log-${id}-${key}`}>{item}</div>
          ))
        ) : (
          <FormattedMessage id="sources.emptyLogs" />
        )}
      </Logs>
    </>
  );
};

export default JobLogs;
