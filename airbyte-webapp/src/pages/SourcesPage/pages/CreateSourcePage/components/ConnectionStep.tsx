import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";
import styled from "styled-components";

import ConnectionBlock from "../../../../../components/ConnectionBlock";
import ContentCard from "../../../../../components/ContentCard";
import { DestinationDefinition } from "../../../../../core/resources/DestinationDefinition";
import SourceDefinitionResource from "../../../../../core/resources/SourceDefinition";
import Spinner from "../../../../../components/Spinner";
import { SyncSchema } from "../../../../../core/resources/Schema";
import ConnectionForm from "./ConnectionForm";
import { IDataItem } from "../../../../../components/DropDown/components/ListItem";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import config from "../../../../../config";

type IProps = {
  onSubmit: (values: { frequency: string; syncSchema: SyncSchema }) => void;
  destinationDefinition: DestinationDefinition;
  sourceDefinitionId: string;
  sourceId: string;
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

const ConnectionStep: React.FC<IProps> = ({
  onSubmit,
  destinationDefinition,
  sourceDefinitionId,
  sourceId
}) => {
  const sourceDefinition = useResource(SourceDefinitionResource.detailShape(), {
    sourceDefinitionId
  });

  const onSelectFrequency = (item: IDataItem) => {
    AnalyticsService.track("New Connection - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a frequency",
      frequency: item?.text,
      connector_source: sourceDefinition.name,
      connector_source_definition_id: sourceDefinition.sourceDefinitionId,
      connector_destination: destinationDefinition.name,
      connector_destination_definition_id:
        destinationDefinition.destinationDefinitionId
    });
  };

  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: sourceDefinition.name }}
        itemTo={{ name: destinationDefinition.name }}
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
            sourceId={sourceId}
          />
        </Suspense>
      </ContentCard>
    </>
  );
};

export default ConnectionStep;
