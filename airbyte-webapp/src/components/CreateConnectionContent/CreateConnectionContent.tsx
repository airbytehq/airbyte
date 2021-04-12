import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import LoadingSchema from "components/LoadingSchema";
import ContentCard from "components/ContentCard";
import { JobsLogItem } from "components/JobItem";
import FrequencyForm from "views/Connector/FrequencyForm";
import { createFormErrorMessage } from "utils/errorStatusMessage";

import TryAfterErrorBlock from "./components/TryAfterErrorBlock";

import config from "config";

import { AnalyticsService } from "core/analytics/AnalyticsService";
import { Source } from "core/resources/Source";
import { Destination } from "core/resources/Destination";
import { SyncSchema } from "core/domain/catalog";

import useConnection from "components/hooks/services/useConnectionHook";
import { useDiscoverSchema } from "components/hooks/services/useSchemaHook";

const SkipButton = styled.div`
  margin-top: 6px;

  & > button {
    min-width: 239px;
    margin-left: 9px;
  }
`;

type IProps = {
  additionBottomControls?: React.ReactNode;
  source?: Source;
  destination?: Destination;
  afterSubmitConnection?: () => void;
};

const CreateConnectionContent: React.FC<IProps> = ({
  source,
  destination,
  afterSubmitConnection,
  additionBottomControls,
}) => {
  const { createConnection } = useConnection();
  const [errorStatusRequest, setErrorStatusRequest] = useState<number>(0);
  const {
    schema,
    isLoading,
    schemaErrorStatus,
    onDiscoverSchema,
  } = useDiscoverSchema(source?.sourceId);

  const onSubmitConnectionStep = async (values: {
    frequency: string;
    prefix: string;
    schema: SyncSchema;
  }) => {
    setErrorStatusRequest(0);
    try {
      await createConnection({
        values: {
          frequency: values.frequency,
          prefix: values.prefix,
          syncCatalog: values.schema,
        },
        source: source,
        destination: destination,
        sourceDefinition: {
          name: source?.name ?? "",
          sourceDefinitionId: source?.sourceDefinitionId ?? "",
        },
        destinationDefinition: {
          name: destination?.name ?? "",
          destinationDefinitionId: destination?.destinationDefinitionId ?? "",
        },
      });

      if (afterSubmitConnection) {
        afterSubmitConnection();
      }
    } catch (e) {
      setErrorStatusRequest(e.status);
    }
  };

  const onSelectFrequency = (item: { text: string }) => {
    AnalyticsService.track("New Connection - Action", {
      user_id: config.ui.workspaceId,
      action: "Select a frequency",
      frequency: item?.text,
      connector_source_definition: source?.sourceName,
      connector_source_definition_id: source?.sourceDefinitionId,
      connector_destination_definition: destination?.destinationName,
      connector_destination_definition_id: destination?.destinationDefinitionId,
    });
  };

  if (isLoading) {
    return (
      <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
        <LoadingSchema />
      </ContentCard>
    );
  }

  if (schemaErrorStatus) {
    return (
      <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
        <TryAfterErrorBlock
          onClick={onDiscoverSchema}
          additionControl={<SkipButton>{additionBottomControls}</SkipButton>}
        />
        <JobsLogItem jobInfo={schemaErrorStatus?.response} />
      </ContentCard>
    );
  }

  return (
    <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
      <Suspense fallback={<LoadingSchema />}>
        <FrequencyForm
          additionBottomControls={additionBottomControls}
          onDropDownSelect={onSelectFrequency}
          onSubmit={onSubmitConnectionStep}
          errorMessage={createFormErrorMessage({ status: errorStatusRequest })}
          schema={schema}
          source={source}
          destination={destination}
        />
      </Suspense>
    </ContentCard>
  );
};

export default CreateConnectionContent;
