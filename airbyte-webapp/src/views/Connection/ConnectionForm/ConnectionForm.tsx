import { Field, FieldProps, Form, Formik, FormikHelpers } from "formik";
import React, { useCallback, useEffect, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useToggle } from "react-use";
import styled from "styled-components";

import { ControlLabels, DropDown, DropDownRow, H4, Input } from "components"; // Card
import { FormChangeTracker } from "components/FormChangeTracker";

import {
  ConnectionScheduleDataBasicSchedule,
  ConnectionScheduleType,
  NamespaceDefinitionType,
  WebBackendConnectionRead,
} from "core/request/AirbyteClient";
import { useFormChangeTrackerService, useUniqueFormId } from "hooks/services/FormChangeTracker";
import { useGetDestinationDefinitionSpecification } from "services/connector/DestinationDefinitionSpecificationService";
import { useCurrentWorkspace } from "services/workspaces/WorkspacesService";
import { generateMessageFromError } from "utils/errorStatusMessage";

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
  margin-bottom: 20px;
`;

export const LeftFieldCol = styled.div`
  flex: 1;
  max-width: 640px;
  padding-right: 30px;
`;

export const RightFieldCol = styled.div`
  flex: 1;
  // max-width: 300px;
`;

const StyledSection = styled.div`
  padding: 34px 44px 10px 44px;
  display: flex;
  flex-direction: column;
  // gap: 15px;
  background: #ffffff;
  border-radius: 16px;

  // &:not(:last-child) {
  //   box-shadow: 0 1px 0 rgba(139, 139, 160, 0.25);
  // }
`;

interface SectionProps {
  title?: React.ReactNode;
}

const ConfigurationsLabel = styled.div`
  font-weight: 700;
  font-size: 20px;
  line-height: 30px;
  margin-bottom: 4px;
`;

// const LabelHeading = styled(H5)`
//   line-height: 16px;
//   display: inline;
// `;

const SectionTitle = styled(H4)`
  margin-bottom: 30px;
`;

const Section: React.FC<SectionProps> = ({ title, children }) => (
  // <Card>
  <StyledSection>
    {title && <SectionTitle bold>{title}</SectionTitle>}
    {children}
  </StyledSection>
  // </Card>
);

const FormContainer = styled(Form)`
  display: flex;
  flex-direction: column;
  // margin-bottom: 30px;
  gap: 20px;
`;

export interface ConnectionFormSubmitResult {
  onSubmitComplete?: () => void;
  submitCancelled?: boolean;
}

export type ConnectionFormMode = "create" | "edit" | "readonly";

interface DirtyChangeTrackerProps {
  dirty: boolean;
  onChanges: (dirty: boolean) => void;
}

const DirtyChangeTracker: React.FC<DirtyChangeTrackerProps> = ({ dirty, onChanges }) => {
  useEffect(() => {
    onChanges(dirty);
  }, [dirty, onChanges]);
  return null;
};

export type ConnectionOrPartialConnection =
  | WebBackendConnectionRead
  | (Partial<WebBackendConnectionRead> & Pick<WebBackendConnectionRead, "syncCatalog" | "source" | "destination">);

export interface ConnectionFormProps {
  onSubmit: (values: ConnectionFormValues) => Promise<ConnectionFormSubmitResult | void>;
  className?: string;
  successMessage?: React.ReactNode;
  onDropDownSelect?: (item: DropDownRow.IDataItem) => void;
  onCancel?: () => void;
  onBack?: () => void;
  onListenAfterSubmit?: (isSuccess: boolean) => void;
  onFormDirtyChanges?: (dirty: boolean) => void;

  /** Should be passed when connection is updated with withRefreshCatalog flag */
  canSubmitUntouchedForm?: boolean;
  mode: ConnectionFormMode;
  additionalSchemaControl?: React.ReactNode;

  connection: ConnectionOrPartialConnection;
}

export const ConnectionForm: React.FC<ConnectionFormProps> = ({
  onSubmit,
  onCancel,
  className,
  onDropDownSelect,
  mode,
  successMessage,
  canSubmitUntouchedForm,
  additionalSchemaControl,
  connection,
  onFormDirtyChanges,
  onBack,
  onListenAfterSubmit,
}) => {
  const destDefinition = useGetDestinationDefinitionSpecification(connection.destination.destinationDefinitionId);
  const { clearFormChange } = useFormChangeTrackerService();
  const formId = useUniqueFormId();
  const [submitError, setSubmitError] = useState<Error | null>(null);
  const [editingTransformation, toggleEditingTransformation] = useToggle(false);

  const { formatMessage } = useIntl();

  const isEditMode: boolean = mode !== "create";
  const initialValues = useInitialValues(connection, destDefinition, isEditMode);
  const workspace = useCurrentWorkspace();

  const onFormSubmit = useCallback(
    async (values: FormikConnectionFormValues, formikHelpers: FormikHelpers<FormikConnectionFormValues>) => {
      // Set the scheduleType based on the schedule value
      values["scheduleType"] = values.scheduleData?.basicSchedule
        ? ConnectionScheduleType.basic
        : ConnectionScheduleType.manual;

      const formValues: ConnectionFormValues = connectionValidationSchema.cast(values, {
        context: { isRequest: true },
      }) as unknown as ConnectionFormValues;

      formValues.operations = mapFormPropsToOperation(values, connection.operations, workspace.workspaceId);

      setSubmitError(null);
      onListenAfterSubmit && onListenAfterSubmit(true);
      try {
        const result = await onSubmit(formValues);

        if (result?.submitCancelled) {
          return;
        }

        formikHelpers.resetForm({ values });
        clearFormChange(formId);

        result?.onSubmitComplete?.();
      } catch (e) {
        onListenAfterSubmit && onListenAfterSubmit(false);
        setSubmitError(e);
      }
    },
    [connection.operations, workspace.workspaceId, onSubmit, clearFormChange, formId]
  );

  const errorMessage = submitError ? generateMessageFromError(submitError) : null;
  const frequencies = useFrequencyDropdownData(connection.scheduleData);

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={connectionValidationSchema}
      enableReinitialize
      onSubmit={onFormSubmit}
    >
      {({ isSubmitting, setFieldValue, isValid, dirty, resetForm, values }) => (
        <FormContainer className={className}>
          <FormChangeTracker changed={dirty} formId={formId} />
          {onFormDirtyChanges && <DirtyChangeTracker dirty={dirty} onChanges={onFormDirtyChanges} />}
          {mode === "create" && (
            <ConfigurationsLabel>
              <FormattedMessage id="onboarding.configurations" />
            </ConfigurationsLabel>
          )}

          <Section title={<FormattedMessage id="connection.basicSettings" />}>
            {/* {!isEditMode && (
              <Section> */}
            <Field name="name">
              {({ field, meta }: FieldProps<string>) => (
                <FlexRow>
                  <LeftFieldCol>
                    <ConnectorLabel
                      nextLine
                      error={!!meta.error && meta.touched}
                      label={<FormattedMessage id="form.connectionName" />}
                      // message={formatMessage({
                      //   id: "form.connectionName.message",
                      // })}
                    />
                  </LeftFieldCol>
                  <RightFieldCol>
                    <Input
                      {...field}
                      disabled={mode === "readonly"}
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
            {/* </Section>
            )} */}

            <Field name="scheduleData.basicSchedule">
              {({ field, meta }: FieldProps<ConnectionScheduleDataBasicSchedule>) => (
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
                  <RightFieldCol style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
                    <DropDown
                      {...field}
                      error={!!meta.error && meta.touched}
                      options={frequencies}
                      onChange={(item) => {
                        onDropDownSelect?.(item);
                        setFieldValue(field.name, item.value);
                      }}
                    />
                  </RightFieldCol>
                </FlexRow>
              )}
            </Field>
          </Section>
          {/* <Card> */}
          <Section title={<FormattedMessage id="connection.streamsSettings" />}>
            <span style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
              <Field name="namespaceDefinition" component={NamespaceDefinitionField} />
            </span>
            {values.namespaceDefinition === NamespaceDefinitionType.customformat && (
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
                    <RightFieldCol style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
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
                      data-testid="prefixInput"
                      style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}
                    />
                  </RightFieldCol>
                </FlexRow>
              )}
            </Field>
            {/* </StyledSection>
            <StyledSection> */}
            <Field
              name="syncCatalog.streams"
              destinationSupportedSyncModes={destDefinition.supportedDestinationSyncModes}
              additionalControl={additionalSchemaControl}
              component={SchemaField}
              isSubmitting={isSubmitting}
              mode={mode}
            />
          </Section>
          {/* </Card> */}
          {mode === "edit" && (
            <>
              <OperationsSection
                wrapper={({ children }) => <StyledSection>{children}</StyledSection>}
                destDefinition={destDefinition}
                onStartEditTransformation={toggleEditingTransformation}
                onEndEditTransformation={toggleEditingTransformation}
              />
              <EditControls
                isSubmitting={isSubmitting}
                dirty={dirty}
                resetForm={() => {
                  resetForm();
                  onCancel?.();
                }}
                onBack={onBack}
                successMessage={successMessage}
                errorMessage={
                  errorMessage || !isValid ? formatMessage({ id: "connectionForm.validation.error" }) : null
                }
                enableControls={canSubmitUntouchedForm}
              />
            </>
          )}
          {mode === "create" && (
            <>
              <OperationsSection
                wrapper={({ children }) => <StyledSection>{children}</StyledSection>}
                destDefinition={destDefinition}
                onStartEditTransformation={toggleEditingTransformation}
                onEndEditTransformation={toggleEditingTransformation}
              />
              <CreateControls
                isSubmitting={isSubmitting}
                isValid={isValid && !editingTransformation}
                errorMessage={
                  errorMessage || !isValid ? formatMessage({ id: "connectionForm.validation.error" }) : null
                }
                onBack={onBack}
              />
            </>
          )}
        </FormContainer>
      )}
    </Formik>
  );
};
