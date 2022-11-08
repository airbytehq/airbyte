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
import { Heading } from "components/ui/Heading";
import { Input } from "components/ui/Input";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import useWorkspace, { WebhookPayload } from "hooks/services/useWorkspace";
import { links } from "utils/links";

import { useNotificationService } from "../../../../../hooks/services/Notification";
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
  const { registerNotification, unregisterAllNotifications } = useNotificationService();
  const { updateWebhook, testWebhook } = useWorkspace();
  const { formatMessage } = useIntl();

  const webhookAction = async (action: WebhookAction, data: WebhookPayload) => {
    unregisterAllNotifications();
    setFormAction((value) => ({ ...value, [action]: true }));
    if (action === WebhookAction.Test) {
      switch (await testWebhookAction(data)) {
        case true: {
          registerNotification({
            id: "settings.webhook.test.passed",
            title: formatMessage({ id: "settings.webhook.test.passed" }),
            isError: false,
          });
          break;
        }
        case false: {
          registerNotification({
            id: "settings.webhook.test.failed",
            title: formatMessage({ id: "settings.webhook.test.failed" }),
            isError: true,
          });
          break;
        }
      }
    }
    if (action === WebhookAction.Save) {
      switch (await testWebhookAction(data)) {
        case true: {
          await updateWebhook(data);
          break;
        }
        case false: {
          registerNotification({
            id: "settings.webhook.save.failed",
            title: formatMessage({ id: "settings.webhook.save.failed" }),
            isError: true,
          });
          break;
        }
      }
    }
    setFormAction((value) => ({ ...value, [action]: false }));
  };

  const testWebhookAction = async (data: WebhookPayload): Promise<boolean> => {
    try {
      // TODO: Temporary solution. The current implementation of the back-end requires at least one selected trigger). Should be removed after back-end fixes
      const payload = { ...data, sendOnSuccess: true };
      return (await testWebhook(payload))?.status === "succeeded";
    } catch (e) {
      return false;
    }
  };

  return (
    <Formik
      initialValues={webhook}
      enableReinitialize
      validateOnBlur
      validateOnChange={false}
      validationSchema={webhookValidationSchema}
      onSubmit={(values: WebhookPayload) => webhookAction(WebhookAction.Save, values)}
    >
      {({ dirty, errors, values }) => (
        <Form>
          <SettingsCard title={<FormattedMessage id="settings.notificationSettings" />}>
            <Content>
              <div className={classNames(styles.webhookGuide, { [styles.active]: webhookViewGuide })}>
                <div className={styles.webhookGuideTitle}>
                  <Heading as="h5">
                    <FormattedMessage id="settings.notificationGuide.title" />
                  </Heading>
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
                <img className={styles.webhookGuideImg} alt="" src={help} />
              </div>
              <Row className={styles.webhookUrlLabelRow}>
                <Cell className={styles.webhookUrlLabelCell}>
                  <Label error={!!errors.webhook}>
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
                      <img className={styles.webhookGuideButtonImg} alt="" src={help} />
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
                        error={!!meta.error && meta.touched}
                      />
                    )}
                  </Field>
                  {!!errors.webhook && (
                    <Text className={styles.webhookErrorMessage} size="sm">
                      <FormattedMessage id={errors.webhook} defaultMessage={errors.webhook} />
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
                        onClick={() => webhookAction(WebhookAction.Test, values)}
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
