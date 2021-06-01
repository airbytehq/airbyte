import React, { Suspense, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useResource } from "rest-hooks";

import LoadingSchema from "components/LoadingSchema";
import ContentCard from "components/ContentCard";
import { JobsLogItem } from "components/JobItem";
import ConnectionForm from "views/Connection/ConnectionForm";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { Button } from "components";
import TryAfterErrorBlock from "./components/TryAfterErrorBlock";

import { AnalyticsService } from "core/analytics/AnalyticsService";
import { Source } from "core/resources/Source";
import { Destination } from "core/resources/Destination";
import { SyncSchema } from "core/domain/catalog";

import useConnection from "components/hooks/services/useConnectionHook";
import { useDiscoverSchema } from "components/hooks/services/useSchemaHook";
import { useDestinationDefinitionSpecificationLoad } from "components/hooks/services/useDestinationHook";
import SourceDefinitionResource from "core/resources/SourceDefinition";
import DestinationDefinitionResource from "core/resources/DestinationDefinition";

const SkipButton = styled.div`
  margin-top: 6px;

  & > button {
    min-width: 239px;
    margin-left: 9px;
  }
`;

const TryArrow = styled(FontAwesomeIcon)`
  margin: 0 10px -1px 0;
  font-size: 14px;
`;

type IProps = {
  additionBottomControls?: React.ReactNode;
  source: Source;
  destination: Destination;
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

  const sourceDefinition = useResource(SourceDefinitionResource.detailShape(), {
    sourceDefinitionId: source.sourceDefinitionId,
  });
  const destinationDefinition = useResource(
    DestinationDefinitionResource.detailShape(),
    {
      destinationDefinitionId: destination.destinationDefinitionId,
    }
  );

  const {
    isLoading: loadingDestination,
  } = useDestinationDefinitionSpecificationLoad(
    destination?.destinationDefinitionId
  );

  if (isLoading || loadingDestination) {
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
      action: "Select a frequency",
      frequency: item?.text,
      connector_source_definition: source?.sourceName,
      connector_source_definition_id: source?.sourceDefinitionId,
      connector_destination_definition: destination?.destinationName,
      connector_destination_definition_id: destination?.destinationDefinitionId,
    });
  };

  const RefreshSchemaButton = () => {
    return (
      <Button onClick={onDiscoverSchema} type="button">
        <TryArrow icon={faRedoAlt} />
        <FormattedMessage id="connection.refreshSchema" />
      </Button>
    );
  };

  return (
    <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
      <Suspense fallback={<LoadingSchema />}>
        <ConnectionForm
          additionBottomControls={additionBottomControls}
          onDropDownSelect={onSelectFrequency}
          additionalSchemaControl={RefreshSchemaButton()}
          onSubmit={onSubmitConnectionStep}
          errorMessage={createFormErrorMessage({ status: errorStatusRequest })}
          schema={schema}
          source={source}
          destination={destination}
          sourceIcon={sourceDefinition?.icon}
          destinationIcon={destinationDefinition?.icon}
        />
      </Suspense>
    </ContentCard>
  );
};

export default CreateConnectionContent;
