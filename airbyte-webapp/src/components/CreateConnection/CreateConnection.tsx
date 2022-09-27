import { Form, Formik, FormikHelpers } from "formik";
import React, { Suspense, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useToggle } from "react-use";

import { FormChangeTracker } from "components/FormChangeTracker";
import LoadingSchema from "components/LoadingSchema";

import { DestinationRead, SourceRead } from "core/request/AirbyteClient";
import {
  ConnectionFormServiceProvider,
  tidyConnectionFormValues,
  useConnectionFormService,
} from "hooks/services/ConnectionForm/ConnectionFormService";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useCreateConnection } from "hooks/services/useConnectionHook";
import { SchemaError as SchemaErrorType, useDiscoverSchema } from "hooks/services/useSourceHook";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";
import CreateControls from "views/Connection/ConnectionForm/components/CreateControls";
import { OperationsSection } from "views/Connection/ConnectionForm/components/OperationsSection";
import { ConnectionFormFields } from "views/Connection/ConnectionForm/ConnectionFormFields";
import { connectionValidationSchema, FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

import { CreateConnectionName } from "./components/CreateConnectionName";
import { SchemaError } from "./components/SchemaError";
import styles from "./CreateConnection.module.scss";

interface CreateConnectionProps {
  source: SourceRead;
  destination: DestinationRead;
  afterSubmitConnection?: () => void;
}

interface CreateConnectionPropsInner extends Pick<CreateConnectionProps, "afterSubmitConnection"> {
  schemaError: SchemaErrorType;
}

const CreateConnectionInner: React.FC<CreateConnectionPropsInner> = ({ schemaError, afterSubmitConnection }) => {
  const navigate = useNavigate();

  const { mutateAsync: createConnection } = useCreateConnection();

  const { clearFormChange } = useFormChangeTrackerService();

  const workspaceId = useCurrentWorkspaceId();
  const formId = useUniqueFormId();

  const { connection, initialValues, getErrorMessage, setSubmitError } = useConnectionFormService();
  const [editingTransformation, toggleEditingTransformation] = useToggle(false);

  const onFormSubmit = useCallback(
    async (formValues: FormikConnectionFormValues, formikHelpers: FormikHelpers<FormikConnectionFormValues>) => {
      const values = tidyConnectionFormValues(formValues, workspaceId);

      try {
        const createdConnection = await createConnection({
          values,
          source: connection.source,
          destination: connection.destination,
          sourceDefinition: {
            sourceDefinitionId: connection.source?.sourceDefinitionId ?? "",
          },
          destinationDefinition: {
            name: connection.destination?.name ?? "",
            destinationDefinitionId: connection.destination?.destinationDefinitionId ?? "",
          },
          sourceCatalogId: connection.catalogId,
        });

        formikHelpers.resetForm();
        // We need to clear the form changes otherwise the dirty form intercept service will prevent navigation
        clearFormChange(formId);

        afterSubmitConnection?.() ?? navigate(`../../connections/${createdConnection.connectionId}`);
      } catch (e) {
        setSubmitError(e);
      }
    },
    [
      workspaceId,
      createConnection,
      connection.source,
      connection.destination,
      connection.catalogId,
      clearFormChange,
      formId,
      afterSubmitConnection,
      navigate,
      setSubmitError,
    ]
  );

  if (schemaError) {
    return <SchemaError schemaErrorStatus={schemaError} />;
  }

  return (
    <Suspense fallback={<LoadingSchema />}>
      <div className={styles.connectionFormContainer}>
        <Formik initialValues={initialValues} validationSchema={connectionValidationSchema} onSubmit={onFormSubmit}>
          {({ values, isSubmitting, isValid, dirty }) => (
            <Form>
              <FormChangeTracker changed={dirty} formId={formId} />
              <CreateConnectionName />
              <ConnectionFormFields values={values} isSubmitting={isSubmitting} dirty={dirty} />
              <OperationsSection
                onStartEditTransformation={toggleEditingTransformation}
                onEndEditTransformation={toggleEditingTransformation}
              />
              <CreateControls
                isSubmitting={isSubmitting}
                isValid={isValid && !editingTransformation}
                errorMessage={getErrorMessage(isValid, dirty)}
              />
            </Form>
          )}
        </Formik>
      </div>
    </Suspense>
  );
};

export const CreateConnection: React.FC<CreateConnectionProps> = ({ source, destination, afterSubmitConnection }) => {
  const { schema, isLoading, schemaErrorStatus, catalogId, onDiscoverSchema } = useDiscoverSchema(
    source.sourceId,
    true
  );

  const partialConnection = {
    syncCatalog: schema,
    destination,
    source,
    catalogId,
  };

  return (
    <ConnectionFormServiceProvider connection={partialConnection} mode="create" refreshSchema={onDiscoverSchema}>
      {isLoading ? (
        <LoadingSchema />
      ) : (
        <CreateConnectionInner afterSubmitConnection={afterSubmitConnection} schemaError={schemaErrorStatus} />
      )}
    </ConnectionFormServiceProvider>
  );
};
