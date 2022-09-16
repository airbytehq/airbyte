import React, { Suspense } from "react";

import { Card } from "components";
import { JobItem } from "components/JobItem/JobItem";
import LoadingSchema from "components/LoadingSchema";

import { LogsRequestError } from "core/request/LogsRequestError";

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
  // destination,
  // afterSubmitConnection,
}) => {
  // const { mutateAsync: createConnection } = useCreateConnection();
  // const navigate = useNavigate();

  // TODO: Probably remove this
  // const formId = useUniqueFormId();

  const { isLoading, schemaErrorStatus, onDiscoverSchema } = useDiscoverSchema(source.sourceId, true);

  // const connection = {
  //   syncCatalog: schema,
  //   destination,
  //   source,
  //   catalogId,
  // };

  // const onSubmitConnectionStep = useCallback(
  //   async (values: ValuesProps) => {
  //     return await createConnection({
  //       values,
  //       source,
  //       destination,
  //       sourceDefinition: {
  //         sourceDefinitionId: source?.sourceDefinitionId ?? "",
  //       },
  //       destinationDefinition: {
  //         name: destination?.name ?? "",
  //         destinationDefinitionId: destination?.destinationDefinitionId ?? "",
  //       },
  //       sourceCatalogId: catalogId,
  //     });
  //   },
  //   [catalogId, createConnection, destination, source]
  // );

  // const afterSubmit = useCallback(
  //   (submitResult: SubmitResult) => {
  //     if (!isSubmitCancel(submitResult)) {
  //       afterSubmitConnection?.(submitResult) ?? navigate(`../../connections/${submitResult.connectionId}`);
  //     }
  //   },
  //   [afterSubmitConnection, navigate]
  // );

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
        {/* <ConnectionFormServiceProvider
          connection={connection as WebBackendConnectionRead /* TODO: IoC so this is what we want }
          mode="create"
          onAfterSubmit={afterSubmit}
          refreshCatalog={onDiscoverSchema}
          formId={formId}
        >
          <ConnectionForm
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            onFormSubmit={onSubmitConnectionStep as any}
          />
        </ConnectionFormServiceProvider> */}
      </div>
    </Suspense>
  );
};

export default CreateConnectionContent;
