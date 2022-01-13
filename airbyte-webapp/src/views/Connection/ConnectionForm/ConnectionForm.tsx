import React, { useCallback, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldArray, FieldProps, Form, Formik } from "formik";
import ResetDataModal from "components/ResetDataModal";
import { ModalTypes } from "components/ResetDataModal/types";
import { equal } from "utils/objects";

import { ControlLabels, DropDown, DropDownRow, Input, Label } from "components";

import { useDestinationDefinitionSpecificationLoadAsync } from "hooks/services/useDestinationHook";
import useWorkspace from "hooks/services/useWorkspace";
import { createFormErrorMessage } from "utils/errorStatusMessage";
import { TransformationField } from "./components/TransformationField";
import { NormalizationField } from "./components/NormalizationField";
import { NamespaceField } from "./components/NamespaceField";
import {
  ConnectionFormValues,
  connectionValidationSchema,
  FormikConnectionFormValues,
  mapFormPropsToOperation,
  useDefaultTransformation,
  useFrequencyDropdownData,
  useInitialValues,
} from "./formConfig";
import SectionTitle from "./components/SectionTitle";
import CreateControls from "./components/CreateControls";
import SchemaField from "./components/SyncCatalogField";
import EditControls from "./components/EditControls";
import { Connection, ScheduleProperties } from "core/resources/Connection";
import { FeatureItem, useFeatureService } from "hooks/services/Feature";
import { DestinationDefinitionSpecification } from "core/domain/connector";

const FormContainer = styled(Form)`
  padding: 22px 27px 15px 24px;
`;

const EditLaterMessage = styled(Label)`
  margin: -20px 0 29px;
`;

const ControlLabelsWithMargin = styled(ControlLabels)`
  margin-bottom: 29px;
`;

const ConnectorLabel = styled(ControlLabels)`
  max-width: 247px;
  margin-right: 20px;
  vertical-align: top;
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

const OperationsSection: React.FC<{
  destDefinition: DestinationDefinitionSpecification;
}> = ({ destDefinition }) => {
  const formatMessage = useIntl().formatMessage;
  const { hasFeature } = useFeatureService();

  const supportsNormalization = destDefinition.supportsNormalization;
  const supportsTransformations =
    destDefinition.supportsDbt && hasFeature(FeatureItem.AllowCustomDBT);

  const defaultTransformation = useDefaultTransformation();

  return (
    <>
      {supportsNormalization || supportsTransformations ? (
        <SectionTitle>
          {[
            supportsNormalization &&
              formatMessage({ id: "connectionForm.normalization.title" }),
            supportsTransformations &&
              formatMessage({ id: "connectionForm.transformation.title" }),
          ]
            .filter(Boolean)
            .join(" & ")}
        </SectionTitle>
      ) : null}
      {supportsNormalization && (
        <Field name="normalization" component={NormalizationField} />
      )}
      {supportsTransformations && (
        <FieldArray name="transformations">
          {(formProps) => (
            <TransformationField
              defaultTransformation={defaultTransformation}
              {...formProps}
            />
          )}
        </FieldArray>
      )}
    </>
  );
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

  const { operations } = connection;

  const initialValues = useInitialValues(
    connection,
    destDefinition,
    isEditMode
  );

  const { workspace } = useWorkspace();

  const onFormSubmit = useCallback(
    async (values: FormikConnectionFormValues) => {
      const formValues: ConnectionFormValues = connectionValidationSchema.cast(
        values,
        {
          context: { isRequest: true },
        }
      ) as any;

      const newOperations = mapFormPropsToOperation(
        values,
        operations,
        workspace.workspaceId
      );

      if (newOperations.length > 0) {
        formValues.operations = newOperations;
      }

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
      operations,
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
      {({ isSubmitting, setFieldValue, isValid, dirty, resetForm }) => (
        <FormContainer className={className}>
          {!isEditMode && (
            <ControlLabelsWithMargin>
              <Field name="schedule">
                {({ field, meta }: FieldProps<ScheduleProperties>) => (
                  <ConnectorLabel
                    error={!!meta.error && meta.touched}
                    label={formatMessage({
                      id: "form.frequency",
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
            </ControlLabelsWithMargin>
          )}
          <NamespaceField />
          <Field name="prefix">
            {({ field }: FieldProps<string>) => (
              <ControlLabelsWithMargin
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
              </ControlLabelsWithMargin>
            )}
          </Field>
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
