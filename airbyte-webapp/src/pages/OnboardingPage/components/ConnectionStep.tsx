import React, { Suspense } from "react";
import { FormattedMessage } from "react-intl";
import { useResource } from "rest-hooks";
import styled from "styled-components";

import ContentCard from "../../../components/ContentCard";
import ConnectionBlock from "../../../components/ConnectionBlock";
import ConnectionForm from "./ConnectionForm";
import SourceDefinitionResource from "../../../core/resources/SourceDefinition";
import DestinationDefinitionResource from "../../../core/resources/DestinationDefinition";
import Spinner from "../../../components/Spinner";
import { SyncSchema } from "../../../core/resources/Schema";
import { IDataItem } from "../../../components/DropDown/components/ListItem";
import { AnalyticsService } from "../../../core/analytics/AnalyticsService";
import config from "../../../config";

type IProps = {
  onSubmit: (values: { frequency: string; syncSchema: SyncSchema }) => void;
  sourceDefinitionId: string;
  destinationDefinitionId: string;
  sourceId: string;
  errorStatus?: number;
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
  sourceDefinitionId,
  destinationDefinitionId,
  errorStatus,
  sourceId
}) => {
  const currentSource = useResource(SourceDefinitionResource.detailShape(), {
    sourceDefinitionId
  });
  const currentDestinationDefinition = useResource(
    DestinationDefinitionResource.detailShape(),
    {
      destinationDefinitionId
    }
  );

  const onSubmitStep = async (values: {
    frequency: string;
    syncSchema: SyncSchema;
  }) => {
    await onSubmit({
      ...values
    });
  };

  const onSelectFrequency = (item: IDataItem) => {
    AnalyticsService.track("New Connection - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a frequency",
      frequency: item?.text,
      connector_source_definition: currentSource?.name,
      connector_source_definition_id: currentSource?.sourceDefinitionId,
      connector_destination_definition: currentDestinationDefinition?.name,
      connector_destination_definition_id:
        currentDestinationDefinition?.destinationDefinitionId
    });
  };

  const errorMessage =
    errorStatus === 0 ? null : errorStatus === 400 ? (
      <FormattedMessage id="form.validationError" />
    ) : (
      <FormattedMessage id="form.someError" />
    );
  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: currentSource.name }}
        itemTo={{ name: currentDestinationDefinition.name }}
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
            onSubmit={onSubmitStep}
            errorMessage={errorMessage}
            sourceId={sourceId}
          />
        </Suspense>
      </ContentCard>
    </>
  );
};

export default ConnectionStep;
