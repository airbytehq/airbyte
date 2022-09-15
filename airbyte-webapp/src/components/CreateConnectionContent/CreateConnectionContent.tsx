import { faRedoAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { Suspense, useCallback, useMemo } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { Button, Card } from "components";
import { JobItem } from "components/JobItem/JobItem";
import LoadingSchema from "components/LoadingSchema";

import { LogsRequestError } from "core/request/LogsRequestError";
import {
  ConnectionFormServiceProvider,
  isSubmitCancel,
  SubmitResult,
} from "hooks/services/Connection/ConnectionFormService";
import { useChangedFormsById, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useCreateConnection, ValuesProps } from "hooks/services/useConnectionHook";
import { ConnectionForm } from "views/Connection/ConnectionForm";

import { DestinationRead, SourceRead, WebBackendConnectionRead } from "../../core/request/AirbyteClient";
import { useDiscoverSchema } from "../../hooks/services/useSourceHook";
import TryAfterErrorBlock from "./components/TryAfterErrorBlock";
import styles from "./CreateConnectionContent.module.scss";

interface CreateConnectionContentProps {
  source: SourceRead;
  destination: DestinationRead;
  afterSubmitConnection?: (connection: WebBackendConnectionRead) => void;
}

const CreateConnectionContent: React.FC<CreateConnectionContentProps> = ({
  source,
  destination,
  afterSubmitConnection,
}) => {
  const { mutateAsync: createConnection } = useCreateConnection();
  const navigate = useNavigate();

  const formId = useUniqueFormId();
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
      return await createConnection({
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
    },
    [catalogId, createConnection, destination, source]
  );

  const afterSubmit = useCallback(
    (submitResult: SubmitResult) => {
      if (!isSubmitCancel(submitResult)) {
        afterSubmitConnection?.(submitResult) ?? navigate(`../../connections/${submitResult.connectionId}`);
      }
    },
    [afterSubmitConnection, navigate]
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
          onAfterSubmit={afterSubmit}
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
