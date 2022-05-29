import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, ContentCard, LoadingButton } from "components";
import EmptyResource from "components/EmptyResourceBlock";
import ResetDataModal from "components/ResetDataModal";

import { FeatureItem, useFeatureService } from "hooks/services/Feature";
import { useResetConnection, useSyncConnection } from "hooks/services/useConnectionHook";
import useLoadingState from "hooks/useLoadingState";
import { useDestinationDefinition } from "services/connector/DestinationDefinitionService";
import { useSourceDefinition } from "services/connector/SourceDefinitionService";
import { useListJobs } from "services/job/JobService";

import { ConnectionStatus, WebBackendConnectionRead } from "../../../../../core/request/AirbyteClient";
import JobsList from "./JobsList";
import { StatusMainInfo } from "./StatusMainInfo";

interface StatusViewProps {
  connection: WebBackendConnectionRead;
  frequencyText?: string;
}

const Content = styled.div`
  margin: 0 10px;
`;

const StyledContentCard = styled(ContentCard)`
  margin-bottom: 20px;
`;

const Title = styled.div`
  display: flex;
  justify-content: space-between;
  flex-direction: row;
  align-items: center;
`;

const TryArrow = styled(FontAwesomeIcon)`
  margin: 0 10px -1px 0;
  font-size: 14px;
`;

const SyncButton = styled(LoadingButton)`
  padding: 5px 8px;
  margin: -5px 0 -5px 9px;
  min-width: 101px;
  min-height: 28px;
`;

const StatusView: React.FC<StatusViewProps> = ({ connection, frequencyText }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { isLoading, showFeedback, startAction } = useLoadingState();
  const { hasFeature } = useFeatureService();
  const allowSync = hasFeature(FeatureItem.AllowSync);

  const sourceDefinition = useSourceDefinition(connection?.source.sourceDefinitionId);

  const destinationDefinition = useDestinationDefinition(connection.destination.destinationDefinitionId);

  const jobs = useListJobs({
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
  });

  const [isStatusUpdating, setStatusUpdating] = useState(false);

  const { mutateAsync: resetConnection } = useResetConnection();
  const { mutateAsync: syncConnection } = useSyncConnection();

  const onSync = () => syncConnection(connection);
  const onReset = () => resetConnection(connection.connectionId);

  return (
    <Content>
      <StatusMainInfo
        connection={connection}
        frequencyText={frequencyText}
        sourceDefinition={sourceDefinition}
        destinationDefinition={destinationDefinition}
        allowSync={allowSync}
        onStatusUpdating={setStatusUpdating}
      />
      <StyledContentCard
        title={
          <Title>
            <FormattedMessage id={"sources.syncHistory"} />
            {connection.status === ConnectionStatus.active && (
              <div>
                <Button onClick={() => setIsModalOpen(true)} disabled={isStatusUpdating}>
                  <FormattedMessage id={"connection.resetData"} />
                </Button>
                <SyncButton
                  disabled={!allowSync || isStatusUpdating}
                  isLoading={isLoading}
                  wasActive={showFeedback}
                  onClick={() => startAction({ action: onSync })}
                >
                  {showFeedback ? (
                    <FormattedMessage id={"sources.syncingNow"} />
                  ) : (
                    <>
                      <TryArrow icon={faRedoAlt} />
                      <FormattedMessage id={"sources.syncNow"} />
                    </>
                  )}
                </SyncButton>
              </div>
            )}
          </Title>
        }
      >
        {jobs.length ? <JobsList jobs={jobs} /> : <EmptyResource text={<FormattedMessage id="sources.noSync" />} />}
      </StyledContentCard>
      {isModalOpen && (
        <ResetDataModal
          onClose={() => setIsModalOpen(false)}
          onSubmit={async () => {
            await onReset();
            setIsModalOpen(false);
          }}
        />
      )}
    </Content>
  );
};

export default StatusView;
