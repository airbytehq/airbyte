import React from "react";
import { FormattedMessage } from "react-intl";
import styled, { keyframes } from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronRight } from "@fortawesome/free-solid-svg-icons";

import { Connection } from "core/domain/connection";
import Link from "components/Link";
import { Button, H1 } from "components/base";
import { Routes } from "pages/routes";
import Status from "core/statuses";

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
  background: ${({ theme }) => theme.darkBeigeColor} url("/rectangle.svg");
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
const PaddedButton = styled(Button)`
  margin-left: 10px;
`;

type ProgressBlockProps = {
  connection: Connection;
  onSync: () => void;
};

const ProgressBlock: React.FC<ProgressBlockProps> = ({
  connection,
  onSync,
}) => {
  const showMessage = (status: string | null) => {
    if (status === null || !status) {
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

  if (
    connection.latestSyncJobStatus !== Status.RUNNING &&
    connection.latestSyncJobStatus !== Status.INCOMPLETE
  ) {
    return (
      <ControlBlock>
        <H1 bold>{showMessage(connection.latestSyncJobStatus)}</H1>
        <PaddedButton onClick={onSync}>
          <FormattedMessage id={"sources.syncNow"} />
        </PaddedButton>
      </ControlBlock>
    );
  }

  return (
    <Bar>
      <Img src={"/process-arrow.svg"} width={20} />
      <FormattedMessage
        id="onboarding.synchronisationProgress"
        values={{
          sr: (...sr: React.ReactNode[]) => (
            <>
              <Lnk to={`${Routes.Source}/${connection.sourceId}`}>{sr}</Lnk>{" "}
              <FontAwesomeIcon icon={faChevronRight} />
            </>
          ),
          ds: (...ds: React.ReactNode[]) => (
            <Lnk to={`${Routes.Destination}/${connection.destinationId}`}>
              {ds}
            </Lnk>
          ),
          sync: (...sync: React.ReactNode[]) => (
            <Lnk to={`${Routes.Connections}/${connection.connectionId}`}>
              {sync}
            </Lnk>
          ),
        }}
      />
    </Bar>
  );
};

export default ProgressBlock;
