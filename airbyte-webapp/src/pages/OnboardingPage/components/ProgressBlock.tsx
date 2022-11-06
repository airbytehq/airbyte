import { faChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { FormattedMessage } from "react-intl";
import styled, { keyframes } from "styled-components";

import { Link } from "components/common/Link";
import { Button } from "components/ui/Button";
import { Heading } from "components/ui/Heading";

import { JobStatus, WebBackendConnectionRead } from "core/request/AirbyteClient";
import Status from "core/statuses";
import { RoutePaths } from "pages/routePaths";

import styles from "./ProgressBlock.module.scss";

const run = keyframes`
  from {
    background-position: 0 0;
  }

  to {
    background-position: 98% 0;
  }
`;

const Bar = styled.div`
  width: 100%;
  height: 49px;
  background: #ffebd7 url("/rectangle.svg");
  color: ${({ theme }) => theme.redColor};
  border-radius: 15px;
  font-weight: 500;
  font-size: 13px;
  line-height: 16px;
  display: flex;
  justify-content: center;
  align-items: center;

  animation: ${run} 15s linear infinite;
`;
const Lnk = styled(Link)`
  font-weight: 600;
  text-decoration: underline;
  color: ${({ theme }) => theme.redColor};
  padding: 0 5px;
`;
const Img = styled.img`
  margin-right: 9px;
`;
const ControlBlock = styled.div`
  height: 49px;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
`;

interface ProgressBlockProps {
  connection: WebBackendConnectionRead;
  onSync: () => void;
}

const ProgressBlock: React.FC<ProgressBlockProps> = ({ connection, onSync }) => {
  const showMessage = (status: JobStatus | undefined) => {
    if (!status) {
      return <FormattedMessage id="onboarding.firstSync" />;
    }
    if (status === Status.FAILED) {
      return <FormattedMessage id="onboarding.syncFailed" />;
    }
    if (status === Status.CANCELLED) {
      return <FormattedMessage id="onboarding.startAgain" />;
    }

    return "";
  };

  if (connection.latestSyncJobStatus === Status.SUCCEEDED) {
    return null;
  }

  if (connection.latestSyncJobStatus !== Status.RUNNING && connection.latestSyncJobStatus !== Status.INCOMPLETE) {
    return (
      <ControlBlock>
        <Heading as="h1" size="xl">
          {showMessage(connection.latestSyncJobStatus)}
        </Heading>
        <Button className={styles.paddedButton} onClick={onSync}>
          <FormattedMessage id="sources.syncNow" />
        </Button>
      </ControlBlock>
    );
  }

  return (
    <Bar>
      <Img src="/process-arrow.svg" width={20} />
      <FormattedMessage
        id="onboarding.synchronizationProgress"
        values={{
          source: (
            <>
              <Lnk to={`../${RoutePaths.Source}/${connection.sourceId}`}>{connection.source.name}</Lnk>{" "}
              <FontAwesomeIcon icon={faChevronRight} />
            </>
          ),
          destination: (
            <Lnk to={`../${RoutePaths.Destination}/${connection.destinationId}`}>{connection.destination.name}</Lnk>
          ),
          sync: (sync: React.ReactNode) => (
            <Lnk to={`../${RoutePaths.Connections}/${connection.connectionId}`}>{sync}</Lnk>
          ),
        }}
      />
    </Bar>
  );
};

export default ProgressBlock;
