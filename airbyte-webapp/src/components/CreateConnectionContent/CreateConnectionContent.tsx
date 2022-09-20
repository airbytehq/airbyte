import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense, useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { Button, Card } from "components";
import { JobItem } from "components/JobItem/JobItem";
import LoadingSchema from "components/LoadingSchema";

import { LogsRequestError } from "core/request/LogsRequestError";
import { ConnectionFormServiceProvider } from "hooks/services/Connection/ConnectionFormService";
import { useChangedFormsById, useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useCreateConnection, ValuesProps } from "hooks/services/useConnectionHook";
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
  const navigate = useNavigate();

  const formId = useUniqueFormId();
  const { clearFormChange } = useFormChangeTrackerService();
  const [changedFormsById] = useChangedFormsById();
  const formDirty = useMemo(() => !!changedFormsById?.[formId], [changedFormsById, formId]);

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
        navigate(`../../connections/${createdConnection.connectionId}`);
      }
    },
    [afterSubmitConnection, catalogId, clearFormChange, createConnection, destination, formId, navigate, source]
  );

  if (schemaErrorStatus) {
    const job = LogsRequestError.extractJobInfo(schemaErrorStatus);
    return (
      <Card>
        <TryAfterErrorBlock onClick={onDiscoverSchema} />
        {job && <JobItem job={job} />}
      </Card>
    );
  }

  return isLoading ? (
    <LoadingSchema />
  ) : (
    <Suspense fallback={<LoadingSchema />}>
      <div className={styles.connectionFormContainer}>
        <ConnectionFormServiceProvider
          connection={connection}
          mode="create"
          formId={formId}
          onSubmit={onSubmitConnectionStep}
          onAfterSubmit={afterSubmitConnection}
          formDirty={formDirty}
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
      </div>
    </Suspense>
  );
};

export default CreateConnectionContent;
