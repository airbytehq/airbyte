import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldProps, Form, Formik } from "formik";

import { SyncSchema } from "core/domain/catalog";
import { Source } from "core/resources/Source";
import { Destination } from "core/resources/Destination";
import ResetDataModal from "components/ResetDataModal";
import { ModalTypes } from "components/ResetDataModal/types";
import { equal } from "utils/objects";

import { ControlLabels, DropDown, DropDownRow, Input, Label } from "components";

import BottomBlock from "./components/BottomBlock";
import Connector from "./components/Connector";
import SchemaField from "./components/SchemaField";
import EditControls from "./components/EditControls";
import { useFrequencyDropdownData, useInitialSchema } from "./useInitialSchema";
import { useDestinationDefinitionSpecificationLoadAsync } from "components/hooks/services/useDestinationHook";
import { ConnectionFormValues, connectionValidationSchema } from "./formConfig";

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
  schema: SyncSchema;
  onSubmit: (values: ConnectionFormValues) => void;
  className?: string;
  source: Source;
  destination: Destination;
  errorMessage?: React.ReactNode;
  additionBottomControls?: React.ReactNode;
  successMessage?: React.ReactNode;
  onReset?: (connectionId?: string) => void;
  onDropDownSelect?: (item: DropDownRow.IDataItem) => void;
  onCancel?: () => void;
  editSchemeMode?: boolean;
  frequencyValue?: string;
  prefixValue?: string;
  isEditMode?: boolean;
  isLoading?: boolean;
  additionalSchemaControl?: React.ReactNode;
  sourceIcon?: string;
  destinationIcon?: string;
};

const ConnectionForm: React.FC<ConnectionFormProps> = ({
  onSubmit,
  onReset,
  onCancel,
  sourceIcon,
  destinationIcon,
  className,
  errorMessage,
  onDropDownSelect,
  frequencyValue,
  prefixValue,
  isEditMode,
  successMessage,
  additionBottomControls,
  editSchemeMode,
  isLoading,
  additionalSchemaControl,
  source,
  destination,
  ...props
}) => {
  const initialSchema = useInitialSchema(props.schema);
  const destDefinition = useDestinationDefinitionSpecificationLoadAsync(
    destination.destinationDefinitionId
  );
  const dropdownData = useFrequencyDropdownData();

  const [modalIsOpen, setResetModalIsOpen] = useState(false);
  const formatMessage = useIntl().formatMessage;

  return (
    <Formik
      initialValues={{
        frequency: frequencyValue || "",
        prefix: prefixValue || "",
        schema: initialSchema,
      }}
      validateOnBlur={true}
      validateOnChange={true}
      validationSchema={connectionValidationSchema}
      onSubmit={async (values) => {
        await onSubmit(
          connectionValidationSchema.cast(values, {
            context: { isRequest: true },
          })
        );

        const requiresReset =
          isEditMode && !equal(initialSchema, values.schema) && !editSchemeMode;
        if (requiresReset) {
          setResetModalIsOpen(true);
        }
      }}
    >
      {({ isSubmitting, setFieldValue, values, isValid, dirty, resetForm }) => (
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
                    data={dropdownData}
                    onSelect={(item) => {
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
          <SchemaField
            destinationSupportedSyncModes={
              destDefinition.supportedDestinationSyncModes
            }
            additionalControl={additionalSchemaControl}
          />
          {!isEditMode ? (
            <EditLaterMessage
              message={<FormattedMessage id="form.dataSync.message" />}
            />
          ) : null}
          {isEditMode ? (
            <>
              <EditControls
                isSubmitting={isLoading || isSubmitting}
                isValid={isValid}
                dirty={dirty || !equal(initialSchema, values.schema)}
                resetForm={() => {
                  resetForm();
                  if (onCancel) {
                    onCancel();
                  }
                }}
                successMessage={successMessage}
                errorMessage={errorMessage}
                editSchemeMode={editSchemeMode}
              />
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
            </>
          ) : (
            <BottomBlock
              additionBottomControls={additionBottomControls}
              isSubmitting={isSubmitting}
              isValid={isValid}
              errorMessage={errorMessage}
            />
          )}
        </FormContainer>
      )}
    </Formik>
  );
};

export default ConnectionForm;
