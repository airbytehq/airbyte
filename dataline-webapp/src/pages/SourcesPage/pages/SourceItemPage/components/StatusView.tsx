import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { useFetcher } from "rest-hooks";

import ContentCard from "../../../../../components/ContentCard";
import Button from "../../../../../components/Button";
import StatusMainInfo from "./StatusMainInfo";
import EmptySyncHistory from "./EmptySyncHistory";
import ConnectionResource, {
  Connection
} from "../../../../../core/resources/Connection";
import { useResource } from "rest-hooks/lib/react-integration/hooks";
import JobResource from "../../../../../core/resources/Job";
import JobsList from "./JobsList";

type IProps = {
  sourceData: Connection;
  onEnabledChange: () => void;
};

const Content = styled.div`
  max-width: 816px;
  margin: 18px auto;

  max-height: calc(100% - 104px);
  //overflow: hidden;
`;

const Title = styled.div`
  display: flex;
  justify-content: space-between;
  flex-direction: row;
  align-items: center;
`;

const TryArrow = styled(FontAwesomeIcon)`
  margin-right: 10px;
  font-size: 14px;
`;

const SyncButton = styled(Button)`
  padding: 5px 8px;
  margin: -5px 0;
`;

const StatusView: React.FC<IProps> = ({ sourceData, onEnabledChange }) => {
  const { jobs } = useResource(JobResource.listShape(), {
    config_id: sourceData.connectionId,
    config_type: "check_connection_source"
  });

  const SyncConnection = useFetcher(ConnectionResource.syncShape());

  const onSync = () =>
    SyncConnection({
      connectionId: sourceData.connectionId
    });

  return (
    <Content>
      <StatusMainInfo
        sourceData={sourceData}
        onEnabledChange={onEnabledChange}
      />
      <ContentCard
        title={
          <Title>
            <FormattedMessage id={"sources.syncHistory"} />
            <SyncButton onClick={onSync}>
              <TryArrow icon={faRedoAlt} />
              <FormattedMessage id={"sources.syncNow"} />
            </SyncButton>
          </Title>
        }
      >
        {jobs.length ? <JobsList jobs={jobs} /> : <EmptySyncHistory />}
      </ContentCard>
    </Content>
  );
};

export default StatusView;
