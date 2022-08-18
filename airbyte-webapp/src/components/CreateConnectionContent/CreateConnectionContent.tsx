import React, { Suspense } from "react";

import { ContentCard } from "components";
import { IDataItem } from "components/base/DropDown/components/Option";
import { JobItem } from "components/JobItem/JobItem";
import LoadingSchema from "components/LoadingSchema";

import { Action, Namespace } from "core/analytics";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAnalyticsService } from "hooks/services/Analytics";
import { ConnectionFormProvider } from "hooks/services/Connection/ConnectionFormService";
import { useCreateConnection, ValuesProps } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";
import { ConnectionForm } from "views/Connection/ConnectionForm";

import { DestinationRead, SourceRead } from "../../core/request/AirbyteClient";
import { useDiscoverSchema } from "../../hooks/services/useSourceHook";
import TryAfterErrorBlock from "./components/TryAfterErrorBlock";

interface CreateConnectionContentProps {
  source: SourceRead;
  destination: DestinationRead;
  afterSubmitConnection?: () => void;
}

const CreateConnectionContent: React.FC<CreateConnectionContentProps> = ({
  source,
  destination,
  afterSubmitConnection,
}) => {
  const { mutateAsync: createConnection } = useCreateConnection();
  const analyticsService = useAnalyticsService();
  const { push } = useRouter();

  const { schema, isLoading, schemaErrorStatus, catalogId, onDiscoverSchema } = useDiscoverSchema(source.sourceId);

  const connection = {
    syncCatalog: schema,
    destination,
    source,
    catalogId,
  };

  const onSubmitConnectionStep = async (values: ValuesProps) => {
    const createdConnection = await createConnection({
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

    push(`../${createdConnection.connectionId}`);
  };

  const onFrequencySelect = (item: IDataItem | null) => {
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
        <TryAfterErrorBlock onClick={onDiscoverSchema} />
        {job && <JobItem job={job} />}
      </ContentCard>
    );
  }

  return isLoading ? (
    <LoadingSchema />
  ) : (
    <Suspense fallback={<LoadingSchema />}>
      <ConnectionFormProvider connection={connection} mode="create">
        <ConnectionForm
          onFrequencySelect={onFrequencySelect}
          onSubmit={onSubmitConnectionStep}
          onAfterSubmit={afterSubmitConnection}
        />
      </ConnectionFormProvider>
    </Suspense>
  );
};

export default CreateConnectionContent;
