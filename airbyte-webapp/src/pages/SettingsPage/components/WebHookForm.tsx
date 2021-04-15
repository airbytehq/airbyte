import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldProps, Form, Formik } from "formik";
import * as yup from "yup";

import { Label, Input } from "components";
import { Row, Cell } from "components/SimpleTableComponents";
import LoadingButton from "components/Button/LoadingButton";

const Text = styled.div`
  font-style: normal;
  font-weight: normal;
  font-size: 13px;
  line-height: 150%;
  padding-bottom: 5px;
`;

const InputRow = styled(Row)`
  height: auto;
  margin-bottom: 28px;
`;

const Message = styled(Text)`
  margin: -19px 0 0;
  padding: 0;
  color: ${({ theme }) => theme.greyColor40};
`;

const FeedbackCell = styled(Cell)`
  &:last-child {
    text-align: left;
  }
  padding-left: 11px;
`;

const webhookValidationSchema = yup.object().shape({
  webhook: yup.string().required("form.empty.error"),
});

const WebHookForm: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  return (
    <Formik
      initialValues={{ webhook: "" }}
      validateOnBlur={true}
      validateOnChange={false}
      validationSchema={webhookValidationSchema}
      onSubmit={async (values) => {
        console.log(values);
        // await onSubmit(values);
      }}
    >
      {({ isSubmitting, initialValues, values }) => (
        <Form>
          <Label>
            <FormattedMessage id="settings.webhookTitle" />
          </Label>
          <Text>
            <FormattedMessage id="settings.webhookDescriprion" />
          </Text>
          <InputRow>
            <Cell flex={3}>
              <Field name="webhook">
                {({ field, meta }: FieldProps<string>) => (
                  <Input
                    {...field}
                    placeholder={formatMessage({
                      id: "settings.yourWebhook",
                    })}
                    error={!!meta.error && meta.touched}
                  />
                )}
              </Field>
            </Cell>
            <FeedbackCell>
              {values.webhook ? (
                <LoadingButton isLoading={isSubmitting}>
                  <FormattedMessage id="settings.test" />
                </LoadingButton>
              ) : null}
            </FeedbackCell>
          </InputRow>
          {initialValues.webhook ? (
            <Message>
              <FormattedMessage id="settings.webhookTestText" />
            </Message>
          ) : null}
        </Form>
      )}
    </Formik>
  );
};

export default WebHookForm;
