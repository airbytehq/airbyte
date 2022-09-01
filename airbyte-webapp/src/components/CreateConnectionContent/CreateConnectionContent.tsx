import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense, useCallback, useRef } from "react";
import { FormattedMessage } from "react-intl";

import { Button, ContentCard } from "components";
import { IDataItem } from "components/base/DropDown/components/Option";
import { JobItem } from "components/JobItem/JobItem";
import LoadingSchema from "components/LoadingSchema";

import { Action, Namespace } from "core/analytics";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAnalyticsService } from "hooks/services/Analytics";
import { ConnectionFormServiceProvider } from "hooks/services/Connection/ConnectionFormService";
import { useCreateConnection, ValuesProps } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";
import { ConnectionForm } from "views/Connection/ConnectionForm";

import { DestinationRead, SourceRead, WebBackendConnectionRead } from "../../core/request/AirbyteClient";
import { useDiscoverSchema } from "../../hooks/services/useSourceHook";
import TryAfterErrorBlock from "./components/TryAfterErrorBlock";
import styles from "./CreateConnectionContent.module.scss";

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
  const newConnection = useRef<WebBackendConnectionRead | null>(null);
  const analyticsService = useAnalyticsService();
  const { push } = useRouter();

  const { schema, isLoading, schemaErrorStatus, catalogId, onDiscoverSchema } = useDiscoverSchema(
    source.sourceId,
    true
  );

  const connection = {
    syncCatalog: schema,
    destination,
    source,
    catalogId,
  };

  const onSubmitConnectionStep = useCallback(
    async (values: ValuesProps) => {
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

      console.log(afterSubmitConnection?.toString());
      // We need the new connection ID to know where to go.
      newConnection.current = createdConnection;
    },
    [afterSubmitConnection, catalogId, createConnection, destination, source]
  );

  const onAfterSubmit = useCallback(
    () => afterSubmitConnection?.() ?? push(`../../connections/${newConnection.current?.connectionId}`),
    [afterSubmitConnection, newConnection, push]
  );

  const onFrequencySelect = useCallback(
    (item: IDataItem | null) => {
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
    },
    [
      analyticsService,
      connection.syncCatalog.streams,
      destination?.destinationDefinitionId,
      destination?.destinationName,
      source?.sourceDefinitionId,
      source?.sourceName,
    ]
  );

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
      <ConnectionFormServiceProvider
        connection={connection}
        mode="create"
        onSubmit={onSubmitConnectionStep}
        onAfterSubmit={onAfterSubmit}
        onFrequencySelect={onFrequencySelect}
      >
        <ConnectionForm
          additionalSchemaControl={
            <Button onClick={onDiscoverSchema} type="button">
              <FontAwesomeIcon className={styles.tryArrowIcon} icon={faRedoAlt} />
              <FormattedMessage id="connection.refreshSchema" />
            </Button>
          }
        />
      </ConnectionFormServiceProvider>
    </Suspense>
  );
};

export default CreateConnectionContent;
