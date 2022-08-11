import React, { Suspense, useMemo } from "react";
import styled from "styled-components";

import { ContentCard } from "components";
import { IDataItem } from "components/base/DropDown/components/Option";
import { JobItem } from "components/JobItem/JobItem";
import LoadingSchema from "components/LoadingSchema";

import { Action, Namespace } from "core/analytics";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useCreateConnection, ValuesProps } from "hooks/services/useConnectionHook";
import ConnectionForm from "views/Connection/ConnectionForm";
import { ConnectionFormProps } from "views/Connection/ConnectionForm/ConnectionForm";

import { DestinationRead, SourceRead, WebBackendConnectionRead } from "../../core/request/AirbyteClient";
import { useDiscoverSchema } from "../../hooks/services/useSourceHook";
import TryAfterErrorBlock from "./components/TryAfterErrorBlock";

const SkipButton = styled.div`
  margin-top: 6px;

  & > button {
    min-width: 239px;
    margin-left: 9px;
  }
`;

interface CreateConnectionContentProps {
  additionBottomControls?: React.ReactNode;
  source: SourceRead;
  destination: DestinationRead;
  afterSubmitConnection?: (connection: WebBackendConnectionRead) => void;
}

const CreateConnectionContent: React.FC<CreateConnectionContentProps> = ({
  source,
  destination,
  afterSubmitConnection,
  additionBottomControls,
}) => {
  const { mutateAsync: createConnection } = useCreateConnection();
  const analyticsService = useAnalyticsService();

  const { schema, isLoading, schemaErrorStatus, catalogId, onDiscoverSchema } = useDiscoverSchema(source.sourceId);

  const connection = useMemo<ConnectionFormProps["connection"]>(
    () => ({
      syncCatalog: schema,
      destination,
      source,
      catalogId,
    }),
    [schema, destination, source, catalogId]
  );

  const onSubmitConnectionStep = async (values: ValuesProps) => {
    const connection = await createConnection({
      values,
      source,
      destination,
      sourceDefinition: {
        sourceDefinitionId: source?.sourceDefinitionId ?? "",
      },
      destinationDefinition: {
        name: destination?.name ?? "",
        destinationDefinitionId: destination?.destinationDefinitionId ?? "",
      },
      sourceCatalogId: catalogId,
    });

    return {
      onSubmitComplete: () => {
        afterSubmitConnection?.(connection);
      },
    };
  };

  const onSelectFrequency = (item: IDataItem | null) => {
    const enabledStreams = connection.syncCatalog.streams.filter((stream) => stream.config?.selected).length;

    if (item) {
      analyticsService.track(Namespace.CONNECTION, Action.FREQUENCY, {
        actionDescription: "Frequency selected",
        frequency: item.label,
        connector_source_definition: source?.sourceName,
        connector_source_definition_id: source?.sourceDefinitionId,
        connector_destination_definition: destination?.destinationName,
        connector_destination_definition_id: destination?.destinationDefinitionId,
        available_streams: connection.syncCatalog.streams.length,
        enabled_streams: enabledStreams,
      });
    }
  };

  if (schemaErrorStatus) {
    const job = LogsRequestError.extractJobInfo(schemaErrorStatus);
    return (
      <ContentCard>
        <TryAfterErrorBlock
          onClick={onDiscoverSchema}
          additionControl={<SkipButton>{additionBottomControls}</SkipButton>}
        />
        {job && <JobItem job={job} />}
      </ContentCard>
    );
  }

  return isLoading ? (
    <LoadingSchema />
  ) : (
    <Suspense fallback={<LoadingSchema />}>
      <ConnectionForm
        mode="create"
        connection={connection}
        additionBottomControls={additionBottomControls}
        onDropDownSelect={onSelectFrequency}
        onSubmit={onSubmitConnectionStep}
      />
    </Suspense>
  );
};

export default CreateConnectionContent;
