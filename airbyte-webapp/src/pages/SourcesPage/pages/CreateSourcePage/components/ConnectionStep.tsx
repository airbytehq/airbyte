import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";
import styled from "styled-components";

import ConnectionBlock from "../../../../../components/ConnectionBlock";
import ContentCard from "../../../../../components/ContentCard";
import { Destination } from "../../../../../core/resources/Destination";
import SourceResource from "../../../../../core/resources/Source";
import Spinner from "../../../../../components/Spinner";
import { SyncSchema } from "../../../../../core/resources/Schema";
import ConnectionForm from "./ConnectionForm";
import { IDataItem } from "../../../../../components/DropDown/components/ListItem";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import config from "../../../../../config";

type IProps = {
  onSubmit: (values: { frequency: string; syncSchema: SyncSchema }) => void;
  destination: Destination;
  sourceId: string;
  sourceImplementationId: string;
};

const SpinnerBlock = styled.div`
  margin: 40px;
  text-align: center;
`;

const FetchMessage = styled.div`
  font-size: 14px;
  line-height: 17px;
  color: ${({ theme }) => theme.textColor};
  margin-top: 15px;
  white-space: pre-line;
`;

const CreateSourcePage: React.FC<IProps> = ({
  onSubmit,
  destination,
  sourceId,
  sourceImplementationId
}) => {
  const source = useResource(SourceResource.detailShape(), {
    sourceId
  });

  const onSelectFrequency = (item: IDataItem) => {
    AnalyticsService.track("New Connection - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a frequency",
      frequency: item?.text,
      connector_source: source.name,
      connector_source_id: source.sourceId,
      connector_destination: destination.name,
      connector_destination_id: destination.destinationId
    });
  };

  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: source.name }}
        itemTo={{ name: destination.name }}
      />
      <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
        <Suspense
          fallback={
            <SpinnerBlock>
              <Spinner />
              <FetchMessage>
                <FormattedMessage id="onboarding.fetchingSchema" />
              </FetchMessage>
            </SpinnerBlock>
          }
        >
          <ConnectionForm
            onSelectFrequency={onSelectFrequency}
            onSubmit={onSubmit}
            sourceImplementationId={sourceImplementationId}
          />
        </Suspense>
      </ContentCard>
    </>
  );
};

export default CreateSourcePage;
