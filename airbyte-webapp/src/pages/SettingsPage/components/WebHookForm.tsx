import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldProps, Form, Formik } from "formik";
import * as yup from "yup";

import { Label, Input, LoadingButton } from "components";
import { Row, Cell } from "components/SimpleTableComponents";

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

const Success = styled.div`
  font-size: 13px;
  color: ${({ theme }) => theme.successColor};
`;

const Error = styled(Success)`
  color: ${({ theme }) => theme.dangerColor};
`;

const webhookValidationSchema = yup.object().shape({
  webhook: yup.string().url("form.url.error"),
});

type WebHookFormProps = {
  notificationUrl: string;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  onSubmit: (data: { webhook: string }) => void;
  onTest: (data: { webhook: string }) => void;
};

const WebHookForm: React.FC<WebHookFormProps> = ({
  notificationUrl,
  onSubmit,
  successMessage,
  errorMessage,
  onTest,
}) => {
  const formatMessage = useIntl().formatMessage;

  const feedBackBlock = (
    dirty: boolean,
    isSubmitting: boolean,
    webhook?: string
  ) => {
    if (successMessage) {
      return <Success>{successMessage}</Success>;
    }

    if (errorMessage) {
      return <Error>{errorMessage}</Error>;
    }

    if (dirty) {
      return (
        <LoadingButton isLoading={isSubmitting} type="submit">
          <FormattedMessage id="form.saveChanges" />
        </LoadingButton>
      );
    }

    if (webhook) {
      return (
        <LoadingButton isLoading={isSubmitting} type="submit">
          <FormattedMessage id="settings.test" />
        </LoadingButton>
      );
    }

    return null;
  };

  return (
    <Formik
      initialValues={{ webhook: notificationUrl }}
      validateOnBlur={true}
      validateOnChange={false}
      validationSchema={webhookValidationSchema}
      onSubmit={async (values) => {
        if (notificationUrl && notificationUrl === values.webhook) {
          await onTest(values);
        } else {
          await onSubmit(values);
        }
      }}
    >
      {({ isSubmitting, initialValues, dirty, errors }) => (
        <Form>
          <Label
            error={!!errors.webhook}
            message={
              !!errors.webhook && (
                <FormattedMessage
                  id={errors.webhook}
                  defaultMessage={errors.webhook}
                />
              )
            }
          >
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
              {feedBackBlock(dirty, isSubmitting, initialValues.webhook)}
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
