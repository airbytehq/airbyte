import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";
import { Field, FieldProps, Form, Formik } from "formik";

import BottomBlock from "./components/BottomBlock";
import Label from "../Label";
import SchemaView from "./components/SchemaView";
import { IDataItem } from "../DropDown/components/ListItem";
import EditControls from "./components/EditControls";
import { SyncSchema } from "../../core/domain/catalog";
import ResetDataModal from "../ResetDataModal";
import { equal } from "../../utils/objects";
import { useFrequencyDropdownData, useInitialSchema } from "./useInitialSchema";
import { ControlLabels } from "../LabeledControl";
import DropDown from "../DropDown";
import { ModalTypes } from "../ResetDataModal/types";

type IProps = {
  className?: string;
  schema: SyncSchema;
  errorMessage?: React.ReactNode;
  additionBottomControls?: React.ReactNode;
  successMessage?: React.ReactNode;
  onSubmit: (values: { frequency: string; schema: SyncSchema }) => void;
  onReset?: (connectionId?: string) => void;
  onDropDownSelect?: (item: IDataItem) => void;
  onCancel?: () => void;
  editSchemeMode?: boolean;
  frequencyValue?: string;
  isEditMode?: boolean;
  isLoading?: boolean;
};

const FormContainer = styled(Form)`
  padding: 22px 27px 23px 24px;
`;

const EditLaterMessage = styled(Label)`
  margin: -20px 0 29px;
`;

const connectionValidationSchema = yup.object().shape({
  frequency: yup.string().required("form.empty.error")
});

const FrequencyForm: React.FC<IProps> = ({
  onSubmit,
  onReset,
  className,
  errorMessage,
  schema,
  onDropDownSelect,
  frequencyValue,
  isEditMode,
  successMessage,
  additionBottomControls,
  onCancel,
  editSchemeMode,
  isLoading
}) => {
  const initialSchema = useInitialSchema(schema);
  const dropdownData = useFrequencyDropdownData();

  const [modalIsOpen, setResetModalIsOpen] = useState(false);
  const formatMessage = useIntl().formatMessage;
  const [newSchema, setNewSchema] = useState(initialSchema);

  return (
    <Formik
      initialValues={{
        frequency: frequencyValue || ""
      }}
      validateOnBlur={true}
      validateOnChange={true}
      validationSchema={connectionValidationSchema}
      onSubmit={async values => {
        const requiresReset =
          isEditMode && !equal(initialSchema, newSchema) && !editSchemeMode;
        await onSubmit({
          frequency: values.frequency,
          schema: newSchema
        });

        if (requiresReset) {
          setResetModalIsOpen(true);
        }
      }}
    >
      {({ isSubmitting, setFieldValue, isValid, dirty, resetForm }) => (
        <FormContainer className={className}>
          <SchemaView schema={newSchema} onChangeSchema={setNewSchema} />
          {!isEditMode ? (
            <EditLaterMessage
              message={<FormattedMessage id="form.dataSync.message" />}
            />
          ) : null}
          <Field name="frequency">
            {({ field }: FieldProps<string>) => (
              <ControlLabels
                // error={!!fieldProps.meta.error && fieldProps.meta.touched}
                label={formatMessage({
                  id: "form.frequency"
                })}
                message={formatMessage({
                  id: "form.frequency.message"
                })}
                labelAdditionLength={300}
              >
                <DropDown
                  {...field}
                  data={dropdownData}
                  onSelect={item => {
                    if (onDropDownSelect) {
                      onDropDownSelect(item);
                    }
                    setFieldValue("frequency", item.value);
                  }}
                />
              </ControlLabels>
            )}
          </Field>
          {isEditMode ? (
            <>
              <EditControls
                isSubmitting={isLoading || isSubmitting}
                isValid={isValid}
                dirty={dirty || !equal(initialSchema, newSchema)}
                resetForm={() => {
                  resetForm();
                  setNewSchema(initialSchema);
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
              dirty={dirty}
              errorMessage={errorMessage}
            />
          )}
        </FormContainer>
      )}
    </Formik>
  );
};

export default FrequencyForm;
