import { Field, FieldProps, Form, Formik, FormikHelpers } from "formik";
import React, { Suspense, useCallback } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useNavigate } from "react-router-dom";
import { useToggle } from "react-use";

import { Input } from "components/base";
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
import {
  ConnectionFormFields,
  ConnectorLabel,
  FlexRow,
  LabelHeading,
  LeftFieldCol,
  RightFieldCol,
  Section,
} from "views/Connection/ConnectionForm/ConnectionFormFields";
import { connectionValidationSchema, FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

import { SchemaError } from "./components/SchemaError";
import styles from "./CreateConnection.module.scss";

interface CreateConnectionProps {
  source: SourceRead;
  destination: DestinationRead;
  afterSubmitConnection?: () => void;
}

interface CreateConnectionPropsInner extends Pick<CreateConnectionProps, "afterSubmitConnection"> {
  schemaError: SchemaErrorType;
  onDiscoverSchema: () => Promise<void>;
}

const CreateConnectionInner: React.FC<CreateConnectionPropsInner> = ({
  schemaError,
  onDiscoverSchema,
  afterSubmitConnection,
}) => {
  const { mutateAsync: createConnection } = useCreateConnection();
  const workspaceId = useCurrentWorkspaceId();
  const formId = useUniqueFormId();
  const { clearFormChange } = useFormChangeTrackerService();
  const navigate = useNavigate();
  const [editingTransformation, toggleEditingTransformation] = useToggle(false);
  const { formatMessage } = useIntl();

  const { connection, initialValues, getErrorMessage, setSubmitError } = useConnectionFormService();

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
    return <SchemaError onDiscoverSchema={onDiscoverSchema} schemaErrorStatus={schemaError} />;
  }

  return (
    <Suspense fallback={<LoadingSchema />}>
      <div className={styles.connectionFormContainer}>
        <Formik initialValues={initialValues} validationSchema={connectionValidationSchema} onSubmit={onFormSubmit}>
          {({ values, isSubmitting, isValid, dirty }) => (
            <Form>
              <FormChangeTracker changed={dirty} formId={formId} />
              <Section>
                <Field name="name">
                  {({ field, meta }: FieldProps<string>) => (
                    <FlexRow>
                      <LeftFieldCol>
                        <ConnectorLabel
                          nextLine
                          error={!!meta.error && meta.touched}
                          label={
                            <LabelHeading bold>
                              <FormattedMessage id="form.connectionName" />
                            </LabelHeading>
                          }
                          message={formatMessage({
                            id: "form.connectionName.message",
                          })}
                        />
                      </LeftFieldCol>
                      <RightFieldCol>
                        <Input
                          {...field}
                          error={!!meta.error}
                          data-testid="connectionName"
                          placeholder={formatMessage({
                            id: "form.connectionName.placeholder",
                          })}
                        />
                      </RightFieldCol>
                    </FlexRow>
                  )}
                </Field>
              </Section>
              <ConnectionFormFields values={values} isSubmitting={isSubmitting} refreshSchema={onDiscoverSchema} />
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
    <ConnectionFormServiceProvider connection={partialConnection} mode="create">
      {isLoading ? (
        <LoadingSchema />
      ) : (
        <CreateConnectionInner
          afterSubmitConnection={afterSubmitConnection}
          schemaError={schemaErrorStatus}
          onDiscoverSchema={onDiscoverSchema}
        />
      )}
    </ConnectionFormServiceProvider>
  );
};
