import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";
import { Field, FieldProps, Form, Formik } from "formik";

import ContentCard from "../../../components/ContentCard";
import Button from "../../../components/Button";
import { FormContainer, ButtonContainer } from "./FormComponents";
import LabeledDropDown from "../../../components/LabeledDropDown";

type IProps = {
  onSubmit: () => void;
};

const SmallLabeledDropDown = styled(LabeledDropDown)`
  max-width: 202px;
`;

const connectionValidationSchema = yup.object().shape({
  frequency: yup.string().required("form.empty.error")
});

const ConnectionStep: React.FC<IProps> = ({ onSubmit }) => {
  const formatMessage = useIntl().formatMessage;
  const dropDownData = [
    {
      text: "manual",
      value: "manual"
    },
    {
      text: "Every 5 min",
      value: "5m"
    },
    {
      text: "Every 15 min",
      value: "15m"
    },
    {
      text: "Every 30 min",
      value: "30m"
    },
    {
      text: "Every hour",
      value: "1h"
    },
    {
      text: "Every 2 hours",
      value: "2h"
    },
    {
      text: "Every 3 hours",
      value: "3h"
    },
    {
      text: "Every 6 hours",
      value: "6h"
    }
  ];

  return (
    <ContentCard title={<FormattedMessage id="onboarding.setConnection" />}>
      <FormContainer>
        <Formik
          initialValues={{
            frequency: ""
          }}
          validateOnBlur={true}
          validateOnChange={true}
          validationSchema={connectionValidationSchema}
          onSubmit={async (_, { setSubmitting }) => {
            setSubmitting(false);
            onSubmit();
          }}
        >
          {({ isSubmitting, setFieldValue, isValid, dirty }) => (
            <Form>
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
                    data={dropDownData}
                    onSelect={item => setFieldValue("frequency", item.value)}
                  />
                )}
              </Field>
              <ButtonContainer>
                <Button
                  type="submit"
                  disabled={isSubmitting || !isValid || !dirty}
                >
                  <FormattedMessage id="onboarding.setUpConnection" />
                </Button>
              </ButtonContainer>
            </Form>
          )}
        </Formik>
      </FormContainer>
    </ContentCard>
  );
};

export default ConnectionStep;
