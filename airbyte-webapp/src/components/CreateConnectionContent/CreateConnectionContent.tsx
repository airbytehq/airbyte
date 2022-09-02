import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense, useCallback, useRef } from "react";
import { FormattedMessage } from "react-intl";

import { Button, ContentCard } from "components";
import { JobItem } from "components/JobItem/JobItem";
import LoadingSchema from "components/LoadingSchema";

import { LogsRequestError } from "core/request/LogsRequestError";
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

      // We need the new connection ID to know where to go.
      newConnection.current = createdConnection;
    },
    [catalogId, createConnection, destination, source]
  );

  const onAfterSubmit = useCallback(
    () => afterSubmitConnection?.() ?? push(`../../connections/${newConnection.current?.connectionId}`),
    [afterSubmitConnection, newConnection, push]
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
