import { Form, Formik, FormikHelpers } from "formik";
import React, { Suspense, useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";

import { ConnectionFormFields } from "components/connection/ConnectionForm/ConnectionFormFields";
import CreateControls from "components/connection/ConnectionForm/CreateControls";
import {
  FormikConnectionFormValues,
  useConnectionValidationSchema,
} from "components/connection/ConnectionForm/formConfig";
import { OperationsSection } from "components/connection/ConnectionForm/OperationsSection";
import LoadingSchema from "components/LoadingSchema";

import { DestinationRead, SourceRead } from "core/request/AirbyteClient";
import {
  ConnectionFormServiceProvider,
  tidyConnectionFormValues,
  useConnectionFormService,
} from "hooks/services/ConnectionForm/ConnectionFormService";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useFormChangeTrackerService } from "hooks/services/FormChangeTracker";
import { useCreateConnection } from "hooks/services/useConnectionHook";
import { SchemaError as SchemaErrorType, useDiscoverSchema } from "hooks/services/useSourceHook";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";

import styles from "./CreateConnectionForm.module.scss";
import { CreateConnectionNameField } from "./CreateConnectionNameField";
import { DataResidency } from "./DataResidency";
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
  const canEditDataGeographies = useFeature(FeatureItem.AllowChangeDataGeographies);
  const { mutateAsync: createConnection } = useCreateConnection();
  const { clearFormChange } = useFormChangeTrackerService();

  const workspaceId = useCurrentWorkspaceId();

  const { connection, initialValues, mode, formId, getErrorMessage, setSubmitError } = useConnectionFormService();
  const [editingTransformation, setEditingTransformation] = useState(false);
  const validationSchema = useConnectionValidationSchema({ mode });

  const onFormSubmit = useCallback(
    async (formValues: FormikConnectionFormValues, formikHelpers: FormikHelpers<FormikConnectionFormValues>) => {
      const values = tidyConnectionFormValues(formValues, workspaceId, validationSchema);

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
      validationSchema,
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
        <Formik initialValues={initialValues} validationSchema={validationSchema} onSubmit={onFormSubmit}>
          {({ values, isSubmitting, isValid, dirty }) => (
            <Form>
              <CreateConnectionNameField />
              {canEditDataGeographies && <DataResidency />}
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
