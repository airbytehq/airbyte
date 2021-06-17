import React, { useCallback, useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldArray, FieldProps, Form, Formik } from "formik";

import { SyncSchema } from "core/domain/catalog";
import { Source } from "core/resources/Source";
import { Destination } from "core/resources/Destination";
import ResetDataModal from "components/ResetDataModal";
import { ModalTypes } from "components/ResetDataModal/types";
import { equal } from "utils/objects";

import { ControlLabels, DropDown, DropDownRow, Input, Label } from "components";

import CreateControls from "./components/CreateControls";
import Connector from "./components/Connector";
import SchemaField from "./components/SyncCatalogField";
import EditControls from "./components/EditControls";
import { useDestinationDefinitionSpecificationLoadAsync } from "components/hooks/services/useDestinationHook";
import {
  ConnectionFormValues,
  connectionValidationSchema,
  DEFAULT_TRANSFORMATION,
  FormikConnectionFormValues,
  mapFormPropsToOperation,
  useFrequencyDropdownData,
  useInitialValues,
} from "./formConfig";
import NormalizationField from "./components/NormalizationField";
import SectionTitle from "./components/SectionTitle";
import { TransformationField } from "./components/TransformationField";
import { Operation } from "core/domain/connection/operation";
import { createFormErrorMessage } from "utils/errorStatusMessage";

const FormContainer = styled(Form)`
  padding: 22px 27px 23px 24px;
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
  sourceIcon?: string;
  destinationIcon?: string;

  syncCatalog: SyncSchema;
  source: Source;
  destination: Destination;
  prefixValue?: string;
  frequencyValue?: string;
  operations?: Operation[];
};

const ConnectionForm: React.FC<ConnectionFormProps> = ({
  onSubmit,
  onReset,
  onCancel,
  sourceIcon,
  destinationIcon,
  className,
  onDropDownSelect,
  frequencyValue,
  prefixValue,
  isEditMode,
  successMessage,
  additionBottomControls,
  editSchemeMode,
  additionalSchemaControl,
  source,
  destination,
  operations,
  syncCatalog,
}) => {
  const destDefinition = useDestinationDefinitionSpecificationLoadAsync(
    destination.destinationDefinitionId
  );

  const [modalIsOpen, setResetModalIsOpen] = useState(false);
  const [submitError, setSubmitError] = useState<Error | null>(null);

  const formatMessage = useIntl().formatMessage;

  const supportsNormalization = destDefinition.supportsNormalization;
  const supportsTransformations = destDefinition.supportsDbt;

  const initialValues = useInitialValues({
    operations,
    frequencyValue,
    prefixValue,
    isEditMode,
    destDefinition,
    syncCatalog,
  });

  const onFormSubmit = useCallback(
    async (values: FormikConnectionFormValues) => {
      const formValues: ConnectionFormValues = connectionValidationSchema.cast(
        values,
        {
          context: { isRequest: true },
        }
      );

      const newOperations = mapFormPropsToOperation(values, operations);

      if (newOperations.length > 0) {
        formValues.withOperations = newOperations;
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
          <ControlLabelsWithMargin>
            <ConnectorLabel
              label={formatMessage({
                id: "form.sourceConnector",
              })}
            >
              <Connector name={source.name} icon={sourceIcon} />
            </ConnectorLabel>
            <ConnectorLabel
              label={formatMessage({
                id: "form.destinationConnector",
              })}
            >
              <Connector name={destination.name} icon={destinationIcon} />
            </ConnectorLabel>
            <Field name="frequency">
              {({ field, meta }: FieldProps<string>) => (
                <ConnectorLabel
                  error={!!meta.error && meta.touched}
                  label={formatMessage({
                    id: "form.frequency",
                  })}
                >
                  <DropDown
                    {...field}
                    error={!!meta.error && meta.touched}
                    data={frequencies}
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
                  defaultTransformation={DEFAULT_TRANSFORMATION}
                  {...formProps}
                />
              )}
            </FieldArray>
          )}
          {!isEditMode && (
            <EditLaterMessage
              message={<FormattedMessage id="form.dataSync.message" />}
            />
          )}
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
