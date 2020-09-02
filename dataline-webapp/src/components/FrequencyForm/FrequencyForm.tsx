import React from "react";
import { useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";
import { Field, FieldProps, Form, Formik } from "formik";

import LabeledDropDown from "../LabeledDropDown";
import FrequencyConfig from "../../data/FrequencyConfig.json";
import BottomBlock from "./components/BottomBlock";

type IProps = {
  className?: string;
  errorMessage?: React.ReactNode;
  onSubmit: (values: { frequency: string }) => void;
};

const SmallLabeledDropDown = styled(LabeledDropDown)`
  max-width: 202px;
`;

const FormContainer = styled(Form)`
  padding: 22px 27px 23px 24px;
`;

const connectionValidationSchema = yup.object().shape({
  frequency: yup.string().required("form.empty.error")
});

const FrequencyForm: React.FC<IProps> = ({
  onSubmit,
  className,
  errorMessage
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

  return (
    <Formik
      initialValues={{
        frequency: ""
      }}
      validateOnBlur={true}
      validateOnChange={true}
      validationSchema={connectionValidationSchema}
      onSubmit={async (values, { setSubmitting }) => {
        await onSubmit(values);
        setSubmitting(false);
      }}
    >
      {({ isSubmitting, setFieldValue, isValid, dirty }) => (
        <FormContainer className={className}>
          <Field name="serviceType">
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
                onSelect={item => setFieldValue("frequency", item.value)}
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
