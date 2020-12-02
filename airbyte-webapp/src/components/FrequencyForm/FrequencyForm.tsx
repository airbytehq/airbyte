import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";
import { Field, FieldProps, Form, Formik } from "formik";

import LabeledDropDown from "../LabeledDropDown";
import FrequencyConfig from "../../data/FrequencyConfig.json";
import BottomBlock from "./components/BottomBlock";
import Label from "../Label";
import { INode } from "../TreeView/TreeView";
import SchemaView from "./components/SchemaView";
import { IDataItem } from "../DropDown/components/ListItem";
import EditControls from "../ServiceForm/components/EditControls";

type IProps = {
  className?: string;
  schema: INode[];
  allSchemaChecked: string[];
  errorMessage?: React.ReactNode;
  successMessage?: React.ReactNode;
  onSubmit: (values: { frequency: string }, checkedState: string[]) => void;
  onDropDownSelect?: (item: IDataItem) => void;
  initialCheckedSchema: Array<string>;
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
  className,
  errorMessage,
  schema,
  initialCheckedSchema,
  onDropDownSelect,
  allSchemaChecked,
  frequencyValue,
  isEditMode,
  successMessage
}) => {
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

  const [checkedState, setCheckedState] = useState(initialCheckedSchema);
  const onCheckAction = (data: Array<string>) => setCheckedState(data);

  return (
    <Formik
      initialValues={{
        frequency: frequencyValue || ""
      }}
      validateOnBlur={true}
      validateOnChange={true}
      validationSchema={connectionValidationSchema}
      onSubmit={async (values, { setSubmitting }) => {
        await onSubmit(values, checkedState);
        setSubmitting(false);
      }}
    >
      {({ isSubmitting, setFieldValue, isValid, dirty, resetForm }) => (
        <FormContainer className={className}>
          <SchemaView
            onCheckAction={onCheckAction}
            checkedState={checkedState}
            schema={schema}
            allSchemaChecked={allSchemaChecked}
          />
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
            <EditControls
              isSubmitting={isSubmitting}
              isValid={isValid}
              dirty={
                dirty ||
                JSON.stringify(checkedState) !==
                  JSON.stringify(initialCheckedSchema)
              }
              resetForm={resetForm}
              successMessage={successMessage}
              errorMessage={errorMessage}
            />
          ) : (
            <BottomBlock
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
