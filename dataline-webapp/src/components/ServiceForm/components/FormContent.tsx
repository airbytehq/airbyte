import { Field, FieldProps } from "formik";
import { FormattedMessage, useIntl } from "react-intl";
import React from "react";
import styled from "styled-components";

import LabeledInput from "../../LabeledInput";
import LabeledDropDown from "../../LabeledDropDown";
import { IDataItem } from "../../DropDown/components/ListItem";
import Instruction from "./Instruction";

type IProps = {
  isEditMode?: boolean;
  dropDownData: Array<IDataItem>;
  setFieldValue: (item: any, value: any) => void;
  formType: "source" | "destination";
  values: { name: string; serviceType: string };
};

const FormItem = styled.div`
  margin-bottom: 27px;
`;

const SmallLabeledDropDown = styled(LabeledDropDown)`
  max-width: 202px;
`;

const FormContent: React.FC<IProps> = ({
  dropDownData,
  formType,
  setFieldValue,
  values,
  isEditMode
}) => {
  const formatMessage = useIntl().formatMessage;

  return (
    <>
      <FormItem>
        <Field name="name">
          {({ field }: FieldProps<string>) => (
            <LabeledInput
              {...field}
              label={<FormattedMessage id="form.name" />}
              placeholder={formatMessage({
                id: `form.${formType}Name.placeholder`
              })}
              type="text"
              message={formatMessage({
                id: `form.${formType}Name.message`
              })}
            />
          )}
        </Field>
      </FormItem>

      <FormItem>
        <Field name="serviceType">
          {({ field }: FieldProps<string>) => (
            <SmallLabeledDropDown
              {...field}
              disabled={isEditMode}
              label={formatMessage({
                id: `form.${formType}Type`
              })}
              hasFilter
              placeholder={formatMessage({
                id: "form.selectConnector"
              })}
              filterPlaceholder={formatMessage({
                id: "form.searchName"
              })}
              data={dropDownData}
              onSelect={item => setFieldValue("serviceType", item.value)}
            />
          )}
        </Field>
        {values.serviceType && (
          <Instruction
            serviceId={values.serviceType}
            dropDownData={dropDownData}
          />
        )}
      </FormItem>
    </>
  );
};

export default FormContent;
