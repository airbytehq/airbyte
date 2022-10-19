import { Form, Formik, FormikHelpers } from "formik";
import React, { Suspense, useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";

import LoadingSchema from "components/LoadingSchema";

import { DestinationRead, SourceRead } from "core/request/AirbyteClient";
import {
  ConnectionFormServiceProvider,
  tidyConnectionFormValues,
  useConnectionFormService,
} from "hooks/services/ConnectionForm/ConnectionFormService";
import { useFormChangeTrackerService } from "hooks/services/FormChangeTracker";
import { useCreateConnection } from "hooks/services/useConnectionHook";
import { SchemaError as SchemaErrorType, useDiscoverSchema } from "hooks/services/useSourceHook";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";
import CreateControls from "views/Connection/ConnectionForm/components/CreateControls";
import { OperationsSection } from "views/Connection/ConnectionForm/components/OperationsSection";
import { ConnectionFormFields } from "views/Connection/ConnectionForm/ConnectionFormFields";
import { connectionValidationSchema, FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

import styles from "./CreateConnectionForm.module.scss";
import { CreateConnectionNameField } from "./CreateConnectionNameField";
import { SchemaError } from "./SchemaError";

interface CreateConnectionProps {
  source: SourceRead;
  destination: DestinationRead;
  afterSubmitConnection?: () => void;
}

interface CreateConnectionPropsInner extends Pick<CreateConnectionProps, "afterSubmitConnection"> {
  schemaError: SchemaErrorType;
}

const CreateConnectionFormInner: React.FC<CreateConnectionPropsInner> = ({ schemaError, afterSubmitConnection }) => {
  const navigate = useNavigate();

  const { mutateAsync: createConnection } = useCreateConnection();

  const { clearFormChange } = useFormChangeTrackerService();

  const workspaceId = useCurrentWorkspaceId();

  const { connection, initialValues, mode, formId, getErrorMessage, setSubmitError } = useConnectionFormService();
  const [editingTransformation, setEditingTransformation] = useState(false);

  const onFormSubmit = useCallback(
    async (formValues: FormikConnectionFormValues, formikHelpers: FormikHelpers<FormikConnectionFormValues>) => {
      const values = tidyConnectionFormValues(formValues, workspaceId, mode);

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

        if (afterSubmitConnection) {
          afterSubmitConnection();
        } else {
          navigate(`../../connections/${createdConnection.connectionId}`);
        }
      } catch (e) {
        setSubmitError(e);
      }
    },
    [
      workspaceId,
      mode,
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
    return <SchemaError schemaError={schemaError} />;
  }

  return (
    <Suspense fallback={<LoadingSchema />}>
      <div className={styles.connectionFormContainer}>
        <Formik
          initialValues={initialValues}
          validationSchema={connectionValidationSchema(mode)}
          onSubmit={onFormSubmit}
          validateOnChange={false}
        >
          {({ values, isSubmitting, isValid, dirty }) => (
            <Form>
              <CreateConnectionNameField />
              <ConnectionFormFields values={values} isSubmitting={isSubmitting} dirty={dirty} />
              <OperationsSection
                onStartEditTransformation={() => setEditingTransformation(true)}
                onEndEditTransformation={() => setEditingTransformation(false)}
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

export const CreateConnectionForm: React.FC<CreateConnectionProps> = ({
  source,
  destination,
  afterSubmitConnection,
}) => {
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
    <ConnectionFormServiceProvider
      connection={partialConnection}
      mode="create"
      refreshSchema={onDiscoverSchema}
      schemaError={schemaErrorStatus}
    >
      {isLoading ? (
        <LoadingSchema />
      ) : (
        <CreateConnectionFormInner afterSubmitConnection={afterSubmitConnection} schemaError={schemaErrorStatus} />
      )}
    </ConnectionFormServiceProvider>
  );
};
