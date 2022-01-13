import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { useResource, useSubscription } from "rest-hooks";

import { Button, ContentCard, LoadingButton } from "components";
import StatusMainInfo from "./StatusMainInfo";
import { Connection } from "core/resources/Connection";
import JobResource from "core/resources/Job";
import JobsList from "./JobsList";
import EmptyResource from "components/EmptyResourceBlock";
import ResetDataModal from "components/ResetDataModal";
import useConnection from "hooks/services/useConnectionHook";
import useLoadingState from "hooks/useLoadingState";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";

type IProps = {
  connection: Connection;
  frequencyText?: string;
};

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

const StatusView: React.FC<IProps> = ({ connection, frequencyText }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { isLoading, showFeedback, startAction } = useLoadingState();

  const sourceDefinition = useResource(
    SourceDefinitionResource.detailShape(),
    connection.source
      ? {
          sourceDefinitionId: connection.source.sourceDefinitionId,
        }
      : null
  );

  const destinationDefinition = useResource(
    DestinationDefinitionResource.detailShape(),
    connection.destination
      ? {
          destinationDefinitionId:
            connection.destination.destinationDefinitionId,
        }
      : null
  );

  const { jobs } = useResource(JobResource.listShape(), {
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
  });
  useSubscription(JobResource.listShape(), {
    configId: connection.connectionId,
    configTypes: ["sync", "reset_connection"],
  });

  const { resetConnection, syncConnection } = useConnection();

  const onSync = () => syncConnection(connection);
  const onReset = () => resetConnection(connection.connectionId);

  return (
    <Content>
      <StatusMainInfo
        connection={connection}
        frequencyText={frequencyText}
        sourceDefinition={sourceDefinition}
        destinationDefinition={destinationDefinition}
      />
      <StyledContentCard
        title={
          <Title>
            <FormattedMessage id={"sources.syncHistory"} />
            <div>
              <Button onClick={() => setIsModalOpen(true)}>
                <FormattedMessage id={"connection.resetData"} />
              </Button>
              <SyncButton
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
          </Title>
        }
      >
        {jobs.length ? (
          <JobsList jobs={jobs} />
        ) : (
          <EmptyResource text={<FormattedMessage id="sources.noSync" />} />
        )}
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
