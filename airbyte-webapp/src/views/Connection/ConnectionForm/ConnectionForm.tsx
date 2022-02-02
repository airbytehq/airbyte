import React, { useCallback, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldProps, Form, Formik } from "formik";

import ResetDataModal from "components/ResetDataModal";
import { ModalTypes } from "components/ResetDataModal/types";
import { equal } from "utils/objects";

import { ControlLabels, DropDown, DropDownRow, Input, Label } from "components";

import { useDestinationDefinitionSpecificationLoadAsync } from "hooks/services/useDestinationHook";
import useWorkspace from "hooks/services/useWorkspace";
import { createFormErrorMessage } from "utils/errorStatusMessage";

import { Connection, ScheduleProperties } from "core/resources/Connection";
import { ConnectionNamespaceDefinition } from "core/domain/connection";
import { NamespaceDefinitionField } from "./components/NamespaceDefinitionField";
import CreateControls from "./components/CreateControls";
import SchemaField from "./components/SyncCatalogField";
import EditControls from "./components/EditControls";
import {
  ConnectionFormValues,
  connectionValidationSchema,
  FormikConnectionFormValues,
  mapFormPropsToOperation,
  useFrequencyDropdownData,
  useInitialValues,
} from "./formConfig";
import { OperationsSection } from "./OperationsSection";

const EditLaterMessage = styled(Label)`
  margin: -20px 0 29px;
`;

const ConnectorLabel = styled(ControlLabels)`
  max-width: 328px;
  margin-right: 20px;
  vertical-align: top;
`;

const FormContainer = styled(Form)`
  padding: 15px 20px;

  & > div:not(:last-child) {
    margin-bottom: 20px;
  }
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

  & > div:not(:last-child) {
    margin-right: 10px;
  }
`;

type ConnectionFormProps = {
  onSubmit: (values: ConnectionFormValues) => void;
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

  connection:
    | Connection
    | (Partial<Connection> &
        Pick<Connection, "syncCatalog" | "source" | "destination">);
};

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
  const destDefinition = useDestinationDefinitionSpecificationLoadAsync(
    connection.destination.destinationDefinitionId
  );

  const [modalIsOpen, setResetModalIsOpen] = useState(false);
  const [submitError, setSubmitError] = useState<Error | null>(null);

  const formatMessage = useIntl().formatMessage;

  const initialValues = useInitialValues(
    connection,
    destDefinition,
    isEditMode
  );

  const { workspace } = useWorkspace();

  const onFormSubmit = useCallback(
    async (values: FormikConnectionFormValues) => {
      const formValues: ConnectionFormValues = connectionValidationSchema.cast(
        values
      ) as any;

      formValues.operations = mapFormPropsToOperation(
        values,
        connection.operations,
        workspace.workspaceId
      );

      setSubmitError(null);
      try {
        await onSubmit(formValues);

        const requiresReset =
          isEditMode &&
          !equal(initialValues.syncCatalog, values.syncCatalog) &&
          !editSchemeMode;
        if (requiresReset) {
          setResetModalIsOpen(true);
        }
      } catch (e) {
        setSubmitError(e);
      }
    },
    [
      editSchemeMode,
      initialValues.syncCatalog,
      isEditMode,
      onSubmit,
      connection.operations,
      workspace.workspaceId,
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
          {/* in create mode schedule is part of form */}
          {!isEditMode && (
            <Field name="schedule">
              {({ field, meta }: FieldProps<ScheduleProperties>) => (
                <ConnectorLabel
                  nextLine
                  error={!!meta.error && meta.touched}
                  label={formatMessage({
                    id: "form.frequency",
                  })}
                  message={formatMessage({
                    id: "form.frequency.message",
                  })}
                >
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
                </ConnectorLabel>
              )}
            </Field>
          )}
          <FlexRow>
            <Field
              name="namespaceDefinition"
              component={NamespaceDefinitionField}
            />
            <Field name="prefix">
              {({ field }: FieldProps<string>) => (
                <ControlLabels
                  nextLine
                  label={formatMessage({
                    id: "form.prefix",
                  })}
                  message={formatMessage({
                    id: "form.prefix.message",
                  })}
                >
                  <Input
                    {...field}
                    type="text"
                    placeholder={formatMessage({
                      id: `form.prefix.placeholder`,
                    })}
                  />
                </ControlLabels>
              )}
            </Field>
          </FlexRow>
          {values.namespaceDefinition ===
            ConnectionNamespaceDefinition.CustomFormat && (
            <Field name="namespaceFormat">
              {({ field, meta }: FieldProps<string>) => (
                <NamespaceFormatLabel
                  nextLine
                  error={!!meta.error}
                  label={
                    <FormattedMessage id="connectionForm.namespaceFormat.title" />
                  }
                  message={
                    <FormattedMessage id="connectionForm.namespaceFormat.subtitle" />
                  }
                >
                  <Input
                    {...field}
                    error={!!meta.error}
                    placeholder={formatMessage({
                      id: "connectionForm.namespaceFormat.placeholder",
                    })}
                  />
                </NamespaceFormatLabel>
              )}
            </Field>
          )}
          <Field
            name="syncCatalog.streams"
            destinationSupportedSyncModes={
              destDefinition.supportedDestinationSyncModes
            }
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
                errorMessage || !isValid
                  ? formatMessage({ id: "connectionForm.validation.error" })
                  : null
              }
              editSchemeMode={editSchemeMode}
            />
          ) : (
            <>
              <OperationsSection destDefinition={destDefinition} />
              <EditLaterMessage
                message={<FormattedMessage id="form.dataSync.message" />}
              />
              <CreateControls
                additionBottomControls={additionBottomControls}
                isSubmitting={isSubmitting}
                isValid={isValid}
                errorMessage={
                  errorMessage || !isValid
                    ? formatMessage({ id: "connectionForm.validation.error" })
                    : null
                }
              />
            </>
          )}
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
