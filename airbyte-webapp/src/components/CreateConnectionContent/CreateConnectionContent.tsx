// import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { faSync } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense, useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components";
import { IDataItem } from "components/base/DropDown/components/Option";
import { Tooltip } from "components/base/Tooltip";
import { JobItem } from "components/JobItem/JobItem";
import LoadingSchema from "components/LoadingSchema";

import { Action, Namespace } from "core/analytics";
import { LogsRequestError } from "core/request/LogsRequestError";
import { useAnalyticsService } from "hooks/services/Analytics";
import { useCreateConnection, ValuesProps } from "hooks/services/useConnectionHook";
import { ConnectionForm, ConnectionFormProps } from "views/Connection/ConnectionForm";

import { DestinationRead, SourceRead, WebBackendConnectionRead } from "../../core/request/AirbyteClient";
import { useDiscoverSchema } from "../../hooks/services/useSourceHook";
import TryAfterErrorBlock from "./components/TryAfterErrorBlock";
import styles from "./CreateConnectionContent.module.scss";

interface CreateConnectionContentProps {
  source: SourceRead;
  destination: DestinationRead;
  afterSubmitConnection?: (connection: WebBackendConnectionRead) => void;
  onBack?: () => void;
  onListenAfterSubmit?: (isSuccess: boolean) => void;
}

const CreateConnectionContent: React.FC<CreateConnectionContentProps> = ({
  source,
  destination,
  afterSubmitConnection,
  onBack,
  onListenAfterSubmit,
}) => {
  const { mutateAsync: createConnection } = useCreateConnection();
  const analyticsService = useAnalyticsService();

  const { schema, isLoading, schemaErrorStatus, catalogId, onDiscoverSchema } = useDiscoverSchema(
    source.sourceId,
    true
  );

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
      <>
        <TryAfterErrorBlock onClick={onDiscoverSchema} />
        {job && <JobItem job={job} />}
      </>
    );
  }

  return isLoading ? (
    <LoadingSchema />
  ) : (
    <Suspense fallback={<LoadingSchema />}>
      <ConnectionForm
        mode="create"
        connection={connection}
        onDropDownSelect={onSelectFrequency}
        onSubmit={onSubmitConnectionStep}
        onBack={onBack}
        onListenAfterSubmit={onListenAfterSubmit}
        additionalSchemaControl={
          <Tooltip
            control={
              <Button onClick={onDiscoverSchema} type="button" secondary iconOnly>
                <FontAwesomeIcon className={styles.tryArrowIcon} icon={faSync} />
              </Button>
            }
            placement="top"
          >
            <FormattedMessage id="connection.refreshSchema" />
          </Tooltip>
        }
      />
    </Suspense>
  );
};

export default CreateConnectionContent;
