import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import { Field, FieldProps, Form, Formik } from "formik";
import * as yup from "yup";

import { Label, Input, LoadingButton, LabeledToggle } from "components";
import { Row, Cell } from "components/SimpleTableComponents";
import { WebhookPayload } from "hooks/services/useWorkspace";
import { equal } from "utils/objects";

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
  webhook: WebhookPayload;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  onSubmit: (data: WebhookPayload) => void;
  onTest: (data: WebhookPayload) => void;
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
      initialValues={webhook}
      enableReinitialize={true}
      validateOnBlur={true}
      validateOnChange={false}
      validationSchema={webhookValidationSchema}
      onSubmit={async (values: WebhookPayload) => {
        if (equal(webhook, values)) {
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
                {({ field }: FieldProps<boolean>) => (
                  <LabeledToggle
                    name={field.name}
                    checked={field.value}
                    onChange={field.onChange}
                    label={<FormattedMessage id="settings.sendOnFailure" />}
                  />
                )}
              </Field>
            </Cell>
            <Cell flex={1}>
              <Field name="sendOnSuccess">
                {({ field }: FieldProps<boolean>) => (
                  <LabeledToggle
                    name={field.name}
                    checked={field.value}
                    onChange={field.onChange}
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
