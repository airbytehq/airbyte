import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";
import { Field, FieldProps, Form, Formik } from "formik";

import LabeledDropDown from "../LabeledDropDown";
import FrequencyConfig from "../../data/FrequencyConfig.json";
import BottomBlock from "./components/BottomBlock";
import Label from "../Label";
import SchemaView from "./components/SchemaView";
import { IDataItem } from "../DropDown/components/ListItem";
import EditControls from "../ServiceForm/components/EditControls";
import {
  SyncMode,
  SyncSchema,
  SyncSchemaStream
} from "../../core/resources/Schema";
import ResetDataModal from "../ResetDataModal";
import { equal } from "../../utils/objects";
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
  frequencyValue?: string;
  isEditMode?: boolean;
};

const SmallLabeledDropDown = styled(LabeledDropDown)`
  max-width: 202px;
`;

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
  additionBottomControls
}) => {
  // get cursorField if it is empty and syncMode is INCREMENTAL
  const getDefaultCursorField = (stream: SyncSchemaStream) => {
    if (stream.defaultCursorField.length) {
      return stream.defaultCursorField;
    }
    if (stream.fields?.length) {
      return [stream.fields[0].cleanedName];
    }

    return stream.cursorField;
  };

  const initialSchema = React.useMemo(
    () => ({
      streams: schema.streams.map(item => {
        // If the value in supportedSyncModes is empty assume the only supported sync mode is FULL_REFRESH.
        // Otherwise it supports whatever sync modes are present.
        const itemWithSupportedSyncModes =
          !item.supportedSyncModes || !item.supportedSyncModes.length
            ? { ...item, supportedSyncModes: [SyncMode.FullRefresh] }
            : item;

        // If syncMode isn't null - don't change item
        if (!!itemWithSupportedSyncModes.syncMode) {
          return itemWithSupportedSyncModes;
        }

        const hasFullRefreshOption = itemWithSupportedSyncModes.supportedSyncModes.includes(
          SyncMode.FullRefresh
        );

        const hasIncrementalOption = itemWithSupportedSyncModes.supportedSyncModes.includes(
          SyncMode.Incremental
        );

        // If syncMode is null, FULL_REFRESH should be selected by default (if it support FULL_REFRESH).
        return hasFullRefreshOption
          ? {
              ...itemWithSupportedSyncModes,
              syncMode: SyncMode.FullRefresh
            }
          : hasIncrementalOption // If source support INCREMENTAL and not FULL_REFRESH. Set INCREMENTAL
          ? {
              ...itemWithSupportedSyncModes,
              cursorField: itemWithSupportedSyncModes.cursorField.length
                ? itemWithSupportedSyncModes.cursorField
                : getDefaultCursorField(itemWithSupportedSyncModes),
              syncMode: SyncMode.Incremental
            }
          : // If source don't support INCREMENTAL and FULL_REFRESH - set first value from supportedSyncModes list
            {
              ...itemWithSupportedSyncModes,
              syncMode: itemWithSupportedSyncModes.supportedSyncModes[0]
            };
      })
    }),
    [schema.streams]
  );

  const [newSchema, setNewSchema] = useState(initialSchema);
  const [modalIsOpen, setResetModalIsOpen] = useState(false);
  const formatMessage = useIntl().formatMessage;
  const dropdownData = React.useMemo(
    () =>
      FrequencyConfig.map(item => ({
        ...item,
        text:
          item.value === "manual"
            ? item.text
            : formatMessage(
                {
                  id: "form.every"
                },
                {
                  value: item.text
                }
              )
      })),
    [formatMessage]
  );

  return (
    <Formik
      initialValues={{
        frequency: frequencyValue || ""
      }}
      validateOnBlur={true}
      validateOnChange={true}
      validationSchema={connectionValidationSchema}
      onSubmit={async values => {
        const requiresReset = isEditMode && !equal(initialSchema, newSchema);
        await onSubmit({ frequency: values.frequency, schema: newSchema });

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
              <SmallLabeledDropDown
                {...field}
                labelAdditionLength={300}
                label={formatMessage({
                  id: "form.frequency"
                })}
                message={formatMessage({
                  id: "form.frequency.message"
                })}
                placeholder={formatMessage({
                  id: "form.frequency.placeholder"
                })}
                data={dropdownData}
                onSelect={item => {
                  if (onDropDownSelect) {
                    onDropDownSelect(item);
                  }
                  setFieldValue("frequency", item.value);
                }}
              />
            )}
          </Field>
          {isEditMode ? (
            <>
              <EditControls
                isSubmitting={isSubmitting}
                isValid={isValid}
                dirty={dirty || !equal(initialSchema, newSchema)}
                resetForm={resetForm}
                successMessage={successMessage}
                errorMessage={errorMessage}
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
