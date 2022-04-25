import { Field, FieldProps, Form, Formik, FormikHelpers } from "formik";
import React, { useCallback, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { ControlLabels, DropDown, DropDownRow, H5, Input, Label } from "components";
import { FormChangeTracker } from "components/FormChangeTracker";
import ResetDataModal from "components/ResetDataModal";
import { ModalTypes } from "components/ResetDataModal/types";

import { Connection, ConnectionNamespaceDefinition, ScheduleProperties } from "core/domain/connection";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { equal } from "utils/objects";

import CreateControls from "./components/CreateControls";
import EditControls from "./components/EditControls";
import { NamespaceDefinitionField } from "./components/NamespaceDefinitionField";
import { OperationsSection } from "./components/OperationsSection";
import SchemaField from "./components/SyncCatalogField";
import {
  ConnectionFormValues,
  connectionValidationSchema,
  FormikConnectionFormValues,
  mapFormPropsToOperation,
  useFrequencyDropdownData,
  useInitialValues,
} from "./formConfig";

const EditLaterMessage = styled(Label)`
  margin: -20px 0 29px;
`;

const ConnectorLabel = styled(ControlLabels)`
  max-width: 328px;
  margin-right: 20px;
  vertical-align: top;
`;

const NamespaceFormatLabel = styled(ControlLabels)`
  flex: 5 0 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`;

export const FlexRow = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 10px;
`;

export const LeftFieldCol = styled.div`
  width: 470px;
`;

export const RightFieldCol = styled.div`
  width: 300px;
`;

const StyledSection = styled.div`
  padding: 15px 20px;

  & > div:not(:last-child) {
    margin-bottom: 20px;
  }
`;

const Header = styled(H5)`
  margin-bottom: 16px;
`;

const Section: React.FC<{ title: React.ReactNode }> = (props) => (
  <StyledSection>
    <Header bold>{props.title}</Header>
    {props.children}
  </StyledSection>
);

const FormContainer = styled(Form)`
  & > ${StyledSection}:not(:last-child) {
    box-shadow: 0 1px 0 rgba(139, 139, 160, 0.25);
  }
`;

interface ConnectionFormSubmitResult {
  onSubmitComplete: () => void;
}

interface ConnectionFormProps {
  onSubmit: (values: ConnectionFormValues) => Promise<ConnectionFormSubmitResult | void>;
  className?: string;
  additionBottomControls?: React.ReactNode;
  successMessage?: React.ReactNode;
  onReset?: (connectionId?: string) => void;
  onDropDownSelect?: (item: DropDownRow.IDataItem) => void;
  onCancel?: () => void;

  /** Should be passed when connection is updated with withRefreshCatalog flag */
  editSchemeMode?: boolean;
  isEditMode?: boolean;
  additionalSchemaControl?: React.ReactNode;

  connection: Connection | (Partial<Connection> & Pick<Connection, "syncCatalog" | "source" | "destination">);
}

const ConnectionForm: React.FC<ConnectionFormProps> = ({
  onSubmit,
  onReset,
  onCancel,
  className,
  onDropDownSelect,
  isEditMode,
  successMessage,
  additionBottomControls,
  editSchemeMode,
  additionalSchemaControl,
  connection,
}) => {
  const destDefinition = useGetDestinationDefinitionSpecification(connection.destination.destinationDefinitionId);
  const { clearFormChange } = useFormChangeTrackerService();
  const formId = useUniqueFormId();

  const [modalIsOpen, setResetModalIsOpen] = useState(false);
  const [submitError, setSubmitError] = useState<Error | null>(null);

  const formatMessage = useIntl().formatMessage;

  const initialValues = useInitialValues(connection, destDefinition, isEditMode);

  const workspace = useCurrentWorkspace();
  const onFormSubmit = useCallback(
    async (values: FormikConnectionFormValues, formikHelpers: FormikHelpers<FormikConnectionFormValues>) => {
      const formValues: ConnectionFormValues = connectionValidationSchema.cast(values, {
        context: { isRequest: true },
      }) as unknown as ConnectionFormValues;

      formValues.operations = mapFormPropsToOperation(values, connection.operations, workspace.workspaceId);

      setSubmitError(null);
      try {
        const result = await onSubmit(formValues);

        formikHelpers.resetForm({ values });
        clearFormChange(formId);

        const requiresReset = isEditMode && !equal(initialValues.syncCatalog, values.syncCatalog) && !editSchemeMode;
        if (requiresReset) {
          setResetModalIsOpen(true);
        }

        result?.onSubmitComplete?.();
      } catch (e) {
        setSubmitError(e);
      }
    },
    [
      connection.operations,
      workspace.workspaceId,
      onSubmit,
      clearFormChange,
      formId,
      isEditMode,
      initialValues.syncCatalog,
      editSchemeMode,
    ]
  );

  const errorMessage = submitError ? createFormErrorMessage(submitError) : null;
  const frequencies = useFrequencyDropdownData();

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={connectionValidationSchema}
      enableReinitialize={true}
      onSubmit={onFormSubmit}
    >
      {({ isSubmitting, setFieldValue, isValid, dirty, resetForm, values }) => (
        <FormContainer className={className}>
          <FormChangeTracker changed={dirty} formId={formId} />
          <Section title={<FormattedMessage id="connection.transfer" />}>
            <Field name="schedule">
              {({ field, meta }: FieldProps<ScheduleProperties>) => (
                <FlexRow>
                  <LeftFieldCol>
                    <ConnectorLabel
                      nextLine
                      error={!!meta.error && meta.touched}
                      label={formatMessage({
                        id: "form.frequency",
                      })}
                      message={formatMessage({
                        id: "form.frequency.message",
                      })}
                    />
                  </LeftFieldCol>
                  <RightFieldCol>
                    <DropDown
                      {...field}
                      error={!!meta.error && meta.touched}
                      options={frequencies}
                      onChange={(item) => {
                        if (onDropDownSelect) {
                          onDropDownSelect(item);
                        }
                        setFieldValue(field.name, item.value);
                      }}
                    />
                  </RightFieldCol>
                </FlexRow>
              )}
            </Field>
          </Section>
          <Section title={<FormattedMessage id="connection.streams" />}>
            <Field name="namespaceDefinition" component={NamespaceDefinitionField} />
            {values.namespaceDefinition === ConnectionNamespaceDefinition.CustomFormat && (
              <Field name="namespaceFormat">
                {({ field, meta }: FieldProps<string>) => (
                  <FlexRow>
                    <LeftFieldCol>
                      <NamespaceFormatLabel
                        nextLine
                        error={!!meta.error}
                        label={<FormattedMessage id="connectionForm.namespaceFormat.title" />}
                        message={<FormattedMessage id="connectionForm.namespaceFormat.subtitle" />}
                      />
                    </LeftFieldCol>
                    <RightFieldCol>
                      <Input
                        {...field}
                        error={!!meta.error}
                        placeholder={formatMessage({
                          id: "connectionForm.namespaceFormat.placeholder",
                        })}
                      />
                    </RightFieldCol>
                  </FlexRow>
                )}
              </Field>
            )}
            <Field name="prefix">
              {({ field }: FieldProps<string>) => (
                <FlexRow>
                  <LeftFieldCol>
                    <ControlLabels
                      nextLine
                      label={formatMessage({
                        id: "form.prefix",
                      })}
                      message={formatMessage({
                        id: "form.prefix.message",
                      })}
                    />
                  </LeftFieldCol>
                  <RightFieldCol>
                    <Input
                      {...field}
                      type="text"
                      placeholder={formatMessage({
                        id: `form.prefix.placeholder`,
                      })}
                    />
                  </RightFieldCol>
                </FlexRow>
              )}
            </Field>
            <Field
              name="syncCatalog.streams"
              destinationSupportedSyncModes={destDefinition.supportedDestinationSyncModes}
              additionalControl={additionalSchemaControl}
              component={SchemaField}
            />
            {isEditMode ? (
              <EditControls
                isSubmitting={isSubmitting}
                dirty={dirty}
                resetForm={() => {
                  resetForm();
                  if (onCancel) {
                    onCancel();
                  }
                }}
                successMessage={successMessage}
                errorMessage={
                  errorMessage || !isValid ? formatMessage({ id: "connectionForm.validation.error" }) : null
                }
                editSchemeMode={editSchemeMode}
              />
            ) : (
              <>
                <OperationsSection destDefinition={destDefinition} />
                <EditLaterMessage message={<FormattedMessage id="form.dataSync.message" />} />
                <CreateControls
                  additionBottomControls={additionBottomControls}
                  isSubmitting={isSubmitting}
                  isValid={isValid}
                  errorMessage={
                    errorMessage || !isValid ? formatMessage({ id: "connectionForm.validation.error" }) : null
                  }
                />
              </>
            )}
          </Section>
          {modalIsOpen && (
            <ResetDataModal
              modalType={ModalTypes.RESET_CHANGED_COLUMN}
              onClose={() => setResetModalIsOpen(false)}
              onSubmit={async () => {
                await onReset?.();
                setResetModalIsOpen(false);
              }}
            />
          )}
        </FormContainer>
      )}
    </Formik>
  );
};

export type { ConnectionFormProps };
export default ConnectionForm;
