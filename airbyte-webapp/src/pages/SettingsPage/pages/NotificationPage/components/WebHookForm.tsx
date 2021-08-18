import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldProps, Form, Formik } from "formik";
import * as yup from "yup";

import { Label, Input, LoadingButton, LabeledToggle } from "components";
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
  margin-bottom: 40px;
`;

const Message = styled(Text)`
  margin: -40px 0 21px;
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
  sendOnSuccess: yup.boolean(),
  sendOnFailure: yup.boolean(),
});

type WebHookFormProps = {
  webhook: {
    notificationUrl: string;
    sendOnSuccess: boolean;
    sendOnFailure: boolean;
  };
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  onSubmit: (data: {
    webhook: string;
    sendOnSuccess: boolean;
    sendOnFailure: boolean;
  }) => void;
  onTest: (data: {
    webhook: string;
    sendOnSuccess: boolean;
    sendOnFailure: boolean;
  }) => void;
};

const WebHookForm: React.FC<WebHookFormProps> = ({
  webhook,
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
      initialValues={{
        webhook: webhook.notificationUrl,
        sendOnSuccess: webhook.sendOnSuccess,
        sendOnFailure: webhook.sendOnFailure,
      }}
      validateOnBlur={true}
      validateOnChange={true}
      validationSchema={webhookValidationSchema}
      onSubmit={async (values: any) => {
        if (
          webhook &&
          webhook.notificationUrl === values.webhook &&
          webhook.sendOnSuccess === values.sendOnSuccess &&
          webhook.sendOnFailure === values.sendOnFailure
        ) {
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
          <InputRow>
            <Cell flex={1}>
              <Field name="sendOnFailure">
                {({ field }: FieldProps<string>) => (
                  <LabeledToggle
                    {...field}
                    name="sendOnFailure"
                    checked={webhook.sendOnFailure}
                    label={<FormattedMessage id="settings.sendOnFailure" />}
                  />
                )}
              </Field>
            </Cell>
            <Cell flex={1}>
              <Field name="sendOnSuccess">
                {({ field }: FieldProps<string>) => (
                  <LabeledToggle
                    {...field}
                    name="sendOnSuccess"
                    checked={webhook.sendOnSuccess}
                    label={<FormattedMessage id="settings.sendOnSuccess" />}
                  />
                )}
              </Field>
            </Cell>
          </InputRow>
        </Form>
      )}
    </Formik>
  );
};

export default WebHookForm;
