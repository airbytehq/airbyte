import { Field, FieldProps, Formik, FormikHelpers } from "formik";
import { Suspense, useCallback, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useNavigate } from "react-router-dom";
import { useToggle } from "react-use";

import { Input } from "components/base";
import LoadingSchema from "components/LoadingSchema";

import { DestinationRead, SourceRead, WebBackendConnectionRead } from "core/request/AirbyteClient";
import {
  ConnectionFormServiceProvider,
  tidyConnectionFormValues,
} from "hooks/services/Connection/ConnectionFormService";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useCreateConnection } from "hooks/services/useConnectionHook";
import { useDiscoverSchema } from "hooks/services/useSourceHook";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { useCurrentWorkspaceId } from "services/workspaces/WorkspacesService";
import { FormError, generateMessageFromError } from "utils/errorStatusMessage";
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
import {
  connectionValidationSchema,
  FormikConnectionFormValues,
  useInitialValues,
} from "views/Connection/ConnectionForm/formConfig";

import { SchemaError } from "./components/SchemaError";
import styles from "./CreateConnection.module.scss";

interface CreateConnectionProps {
  source: SourceRead;
  destination: DestinationRead;
  afterSubmitConnection?: () => void;
}

export const CreateConnection = ({ source, destination, afterSubmitConnection }: CreateConnectionProps) => {
  const { mutateAsync: createConnection } = useCreateConnection();
  const { schema, isLoading, schemaErrorStatus, catalogId, onDiscoverSchema } = useDiscoverSchema(
    source.sourceId,
    true
  );
  const workspaceId = useCurrentWorkspaceId();
  const formId = useUniqueFormId();
  const { clearFormChange } = useFormChangeTrackerService();
  const navigate = useNavigate();
  const [editingTransformation, toggleEditingTransformation] = useToggle(false);
  const { formatMessage } = useIntl();
  const [submitError, setSubmitError] = useState<FormError>();

  const partialConnection = {
    syncCatalog: schema,
    destination,
    source,
    catalogId,
  };

  const destDefinition = useGetDestinationDefinitionSpecification(destination.destinationDefinitionId);
  const initialValues = useInitialValues(partialConnection, destDefinition);

  const onFormSubmit = useCallback(
    async (formValues: FormikConnectionFormValues, formikHelpers: FormikHelpers<FormikConnectionFormValues>) => {
      const values = tidyConnectionFormValues(formValues, workspaceId);

      try {
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
      source,
      destination,
      catalogId,
      clearFormChange,
      formId,
      afterSubmitConnection,
      navigate,
    ]
  );

  const getErrorMessage = useCallback(
    (formValid: boolean, dirty: boolean) =>
      submitError
        ? generateMessageFromError(submitError)
        : dirty && !formValid
        ? formatMessage({ id: "connectionForm.validation.error" })
        : null,
    [formatMessage, submitError]
  );

  if (schemaErrorStatus) {
    return <SchemaError onDiscoverSchema={onDiscoverSchema} schemaErrorStatus={schemaErrorStatus} />;
  }

  return isLoading ? (
    <LoadingSchema />
  ) : (
    <Suspense fallback={<LoadingSchema />}>
      <div className={styles.connectionFormContainer}>
        <Formik initialValues={initialValues} validationSchema={connectionValidationSchema} onSubmit={onFormSubmit}>
          {({ values, isSubmitting, isValid, dirty }) => (
            <>
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
              <ConnectionFormServiceProvider
                mode="create"
                refreshCatalog={onDiscoverSchema}
                connection={partialConnection as unknown as WebBackendConnectionRead}
                formId={formId}
              >
                <ConnectionFormFields values={values} isSubmitting={isSubmitting} />
                <OperationsSection
                  onStartEditTransformation={toggleEditingTransformation}
                  onEndEditTransformation={toggleEditingTransformation}
                />
                <CreateControls
                  isSubmitting={isSubmitting}
                  isValid={isValid && !editingTransformation}
                  errorMessage={getErrorMessage(isValid, dirty)}
                />
              </ConnectionFormServiceProvider>
            </>
          )}
        </Formik>
      </div>
    </Suspense>
  );
};
