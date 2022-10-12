import { faXmark } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { Field, FieldProps, Form, Formik } from "formik";
import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { Label, LabeledSwitch } from "components";
import { DocsIcon } from "components/icons/DocsIcon";
import { PlayIcon } from "components/icons/PlayIcon";
import { Row, Cell } from "components/SimpleTableComponents";
import { Button } from "components/ui/Button";
import { Input } from "components/ui/Input";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import useWorkspace, { WebhookPayload } from "hooks/services/useWorkspace";
import { links } from "utils/links";

import { Content, SettingsCard } from "../../SettingsComponents";
import help from "./help.png";
import styles from "./WebHookForm.module.scss";

const enum WebhookAction {
  Test = "test",
  Save = "save",
}

interface FormActionType {
  [WebhookAction.Test]: boolean;
  [WebhookAction.Save]: boolean;
}

interface WebHookFormProps {
  webhook: WebhookPayload;
}

const webhookValidationSchema = yup.object().shape({
  webhook: yup.string().url("form.url.error"),
  sendOnSuccess: yup.boolean(),
  sendOnFailure: yup.boolean(),
});

export const WebHookForm: React.FC<WebHookFormProps> = ({ webhook }) => {
  const [webhookViewGuide, setWebhookViewGuide] = useState(false);
  const [formAction, setFormAction] = useState<FormActionType>({ test: false, save: false });
  const [webhookUrlError, setWebhookUrlError] = useState<boolean>(false);
  const { updateWebhook, testWebhook } = useWorkspace();
  const { formatMessage } = useIntl();

  const webhookChange = async (action: WebhookAction, data: WebhookPayload) => {
    setFormAction((value) => ({ ...value, [action]: true }));
    if (action === WebhookAction.Test) {
      await testWebhookAction(data);
    }
    if (action === WebhookAction.Save) {
      await updateWebhook(data);
    }
    setFormAction((value) => ({ ...value, [action]: false }));
  };

  const testWebhookAction = async (data: WebhookPayload) => {
    if (webhookUrlError) {
      setWebhookUrlError(false);
    }
    try {
      const response = await testWebhook(data);
      if (response.status === "failed") {
        setWebhookUrlError(true);
      }
    } catch (e) {
      setWebhookUrlError(true);
    }
  };

  return (
    <Formik
      initialValues={webhook}
      enableReinitialize
      validateOnBlur
      validateOnChange={false}
      validationSchema={webhookValidationSchema}
      onSubmit={(values: WebhookPayload) => webhookChange(WebhookAction.Save, values)}
    >
      {({ dirty, errors, values }) => (
        <Form>
          <SettingsCard title={<FormattedMessage id="settings.notificationSettings" />}>
            <Content>
              <div className={classNames(styles.webhookGuide, { [styles.active]: webhookViewGuide })}>
                <div className={styles.webhookGuideTitle}>
                  <Text as="h5">
                    <FormattedMessage id="settings.notificationGuide.title" />
                  </Text>
                  <div>
                    <Button type="button" variant="clear" onClick={() => setWebhookViewGuide(false)}>
                      <FontAwesomeIcon className={styles.crossIcon} icon={faXmark} />
                    </Button>
                  </div>
                </div>
                <ul>
                  <li>
                    <a
                      className={styles.webhookGuideLink}
                      target="_blank"
                      href={links.webhookGuideLink}
                      rel="noreferrer"
                    >
                      <DocsIcon />
                      <Text className={styles.text} size="lg">
                        <FormattedMessage id="settings.notificationGuide.link.configuration" />
                      </Text>
                    </a>
                  </li>
                  <li>
                    <a
                      className={styles.webhookGuideLink}
                      target="_blank"
                      href={links.webhookVideoGuideLink}
                      rel="noreferrer"
                    >
                      <PlayIcon />
                      <Text className={styles.text} size="lg">
                        <FormattedMessage id="settings.notificationGuide.link.slackConfiguration" />
                      </Text>
                    </a>
                  </li>
                </ul>
                <img
                  className={styles.webhookGuideImg}
                  alt={formatMessage({
                    id: "settings.notificationGuide.button",
                  })}
                  src={help}
                />
              </div>
              <Row className={styles.webhookUrlLabelRow}>
                <Cell className={styles.webhookUrlLabelCell}>
                  <Label
                    error={!!errors.webhook}
                    message={
                      !!errors.webhook && <FormattedMessage id={errors.webhook} defaultMessage={errors.webhook} />
                    }
                  >
                    <FormattedMessage id="settings.webhookTitle" />
                  </Label>
                </Cell>
                <Cell className={styles.webhookGuideButtonCell}>
                  {!webhookViewGuide && (
                    <>
                      <Button
                        type="button"
                        className={styles.webhookGuideButton}
                        variant="clear"
                        onClick={() => setWebhookViewGuide(true)}
                      >
                        <FormattedMessage id="settings.notificationGuide.button" />
                      </Button>
                      <img
                        className={styles.webhookGuideButtonImg}
                        alt={formatMessage({
                          id: "settings.notificationGuide.button",
                        })}
                        src={help}
                      />
                    </>
                  )}
                </Cell>
              </Row>
              <Row className={styles.webhookUrlRow}>
                <Cell className={styles.webhookUrlInputCell}>
                  <Field name="webhook">
                    {({ field, meta }: FieldProps<string>) => (
                      <Input
                        {...field}
                        placeholder={formatMessage({
                          id: "settings.yourWebhook",
                        })}
                        error={(!!meta.error && meta.touched) || webhookUrlError}
                      />
                    )}
                  </Field>
                  {webhookUrlError && (
                    <Text className={styles.webhookErrorMessage} size="sm">
                      <FormattedMessage id="form.someError" />
                    </Text>
                  )}
                </Cell>
                <Cell className={styles.testButtonCell}>
                  <Tooltip
                    className={styles.tooltip}
                    placement="top"
                    control={
                      <Button
                        className={styles.testButton}
                        size="sm"
                        type="button"
                        variant="secondary"
                        isLoading={formAction.test}
                        disabled={!values.webhook || !!errors.webhook || formAction.save}
                        onClick={() => webhookChange(WebhookAction.Test, values)}
                      >
                        <FormattedMessage id="settings.test" />
                      </Button>
                    }
                  >
                    <FormattedMessage id="settings.webhookTestText" />
                  </Tooltip>
                </Cell>
              </Row>
              <Row className={styles.notificationSettingsLabelRow}>
                <Cell className={styles.notificationSettingsLabelCell}>
                  <Label>
                    <FormattedMessage id="settings.syncNotifications.label" />
                  </Label>
                </Cell>
              </Row>
              <Row className={styles.notificationSettingsRow}>
                <Cell className={styles.notificationSettingsCell}>
                  <Field name="sendOnFailure">
                    {({ field }: FieldProps<boolean>) => (
                      <LabeledSwitch
                        className={styles.sendOnFailure}
                        name={field.name}
                        checked={field.value}
                        onChange={field.onChange}
                        label={<FormattedMessage id="settings.sendOnFailure" />}
                      />
                    )}
                  </Field>
                  <Field name="sendOnSuccess">
                    {({ field }: FieldProps<boolean>) => (
                      <LabeledSwitch
                        name={field.name}
                        checked={field.value}
                        onChange={field.onChange}
                        label={<FormattedMessage id="settings.sendOnSuccess" />}
                      />
                    )}
                  </Field>
                </Cell>
              </Row>
            </Content>
          </SettingsCard>
          <div className={styles.action}>
            <Button
              type="submit"
              size="sm"
              isLoading={formAction.save}
              disabled={!dirty || !!errors.webhook || formAction.test}
            >
              <FormattedMessage id="form.saveChanges" />
            </Button>
          </div>
        </Form>
      )}
    </Formik>
  );
};
