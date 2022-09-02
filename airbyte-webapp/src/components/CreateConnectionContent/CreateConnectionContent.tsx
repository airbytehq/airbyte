import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense, useCallback } from "react";
import { FormattedMessage } from "react-intl";

import { Button, ContentCard } from "components";
import { JobItem } from "components/JobItem/JobItem";
import LoadingSchema from "components/LoadingSchema";

import { LogsRequestError } from "core/request/LogsRequestError";
import { ConnectionFormServiceProvider } from "hooks/services/Connection/ConnectionFormService";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useCreateConnection, ValuesProps } from "hooks/services/useConnectionHook";
import useRouter from "hooks/useRouter";
import { ConnectionForm } from "views/Connection/ConnectionForm";

import { DestinationRead, SourceRead } from "../../core/request/AirbyteClient";
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
  const { push } = useRouter();

  const formId = useUniqueFormId();
  const { clearFormChange } = useFormChangeTrackerService();

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

      // We only want to go to the new connection if we _do not_ have an after submit action.
      if (!afterSubmitConnection) {
        // We have to clear the form change to prevent the dirty-form tracking modal from appearing.
        clearFormChange(formId);
        // This is the "default behavior", go to the created connection.
        push(`../../connections/${createdConnection.connectionId}`);
      }
    },
    [afterSubmitConnection, catalogId, clearFormChange, createConnection, destination, formId, push, source]
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
        formId={formId}
        onSubmit={onSubmitConnectionStep}
        onAfterSubmit={afterSubmitConnection}
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
