import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";
import { Field, FieldProps, Form, Formik } from "formik";

import LabeledDropDown from "../LabeledDropDown";
import FrequencyConfig from "../../data/FrequencyConfig.json";
import BottomBlock from "./components/BottomBlock";
import Label from "../Label";
import TreeView, { INode } from "../TreeView/TreeView";
import { IDataItem } from "../DropDown/components/ListItem";

type IProps = {
  className?: string;
  schema: INode[];
  allSchemaChecked: string[];
  errorMessage?: React.ReactNode;
  onSubmit: (values: { frequency: string }, checkedState: string[]) => void;
  onDropDownSelect?: (item: IDataItem) => void;
  initialCheckedSchema: Array<string>;
};

const SmallLabeledDropDown = styled(LabeledDropDown)`
  max-width: 202px;
`;

const FormContainer = styled(Form)`
  padding: 22px 27px 23px 24px;
`;

const TreeViewContainer = styled.div`
  width: 100%;
  background: ${({ theme }) => theme.greyColor0};
  margin-bottom: 29px;
  border-radius: 4px;
  overflow: hidden;
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
  allSchemaChecked
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
        frequency: ""
      }}
      validateOnBlur={true}
      validateOnChange={true}
      validationSchema={connectionValidationSchema}
      onSubmit={async (values, { setSubmitting }) => {
        await onSubmit(values, checkedState);
        setSubmitting(false);
      }}
    >
      {({ isSubmitting, setFieldValue, isValid, dirty }) => (
        <FormContainer className={className}>
          <Label message={<FormattedMessage id="form.dataSync.message" />}>
            <FormattedMessage id="form.dataSync" />
          </Label>
          <TreeViewContainer>
            <TreeView
              checkedAll={allSchemaChecked}
              nodes={schema}
              onCheck={onCheckAction}
              checked={checkedState}
            />
          </TreeViewContainer>
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
          <BottomBlock
            isSubmitting={isSubmitting}
            isValid={isValid}
            dirty={dirty}
            errorMessage={errorMessage}
          />
        </FormContainer>
      )}
    </Formik>
  );
};

export default FrequencyForm;
