import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";
import { Field, FieldProps, Form, Formik } from "formik";

import ContentCard from "../../../components/ContentCard";
import ConnectionBlock from "../../../components/ConnectionBlock";
import Button from "../../../components/Button";
import { FormContainer, ButtonContainer } from "./FormComponents";
import LabeledDropDown from "../../../components/LabeledDropDown";
import FrequencyConfig from "../../../data/FrequencyConfig.json";

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

  return (
    <>
      <ConnectionBlock
        itemFrom={{ name: "Test 1" }}
        itemTo={{ name: "Test 2" }}
      />
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
                      data={FrequencyConfig}
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
    </>
  );
};

export default ConnectionStep;
