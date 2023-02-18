import { faRecycle, faTrash } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { Field, FieldProps, Form, Formik } from "formik";
import React, { useState } from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { LabeledInput } from "components/LabeledInput";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";

import { useDbtCloudServiceToken } from "packages/cloud/services/dbtCloud";
import { SettingsCard } from "pages/SettingsPage/pages/SettingsComponents";
import { links } from "utils/links";

import styles from "./DbtCloudSettingsView.module.scss";

const cleanedErrorMessage = (e: Error): string => e.message.replace("Internal Server Error: ", "");

export const DbtCloudSettingsView: React.FC = () => {
  const { formatMessage } = useIntl();
  const { hasExistingToken, saveToken, isSavingToken, deleteToken, isDeletingToken } = useDbtCloudServiceToken();
  const [hasValidationError, setHasValidationError] = useState(false);
  const [confirmationMessage, setConfirmationMessage] = useState("");
  const [isReplacingToken, setIsReplacingToken] = useState(false);

  const ServiceTokenForm = () => (
    <Formik
      initialValues={{
        serviceToken: "",
      }}
      onSubmit={({ serviceToken }) => {
        setHasValidationError(false);
        setConfirmationMessage("");
        return saveToken(serviceToken, {
          onError: (e) => {
            setHasValidationError(true);

            setConfirmationMessage(cleanedErrorMessage(e));
          },
          onSuccess: () => {
            setConfirmationMessage(formatMessage({ id: "settings.integrationSettings.dbtCloudSettings.form.success" }));
          },
        });
      }}
    >
      <Form>
        <Field name="serviceToken">
          {({ field }: FieldProps<string>) => (
            <LabeledInput
              {...field}
              label={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.serviceToken" />}
              error={hasValidationError}
              message={confirmationMessage}
              type="text"
            />
          )}
        </Field>
        <div className={classNames(styles.controlGroup, styles.formButtons)}>
          {hasExistingToken && (
            <Button
              variant="secondary"
              onClick={(e) => {
                e.preventDefault();
                setIsReplacingToken(false);
              }}
            >
              Cancel
            </Button>
          )}
          <Button variant="primary" type="submit" className={styles.button} isLoading={isSavingToken}>
            <FormattedMessage id="settings.integrationSettings.dbtCloudSettings.form.submit" />
          </Button>
        </div>
      </Form>
    </Formik>
  );

  const ReplaceOrDeleteToken = () => {
    return (
      <div className={styles.controlGroup}>
        <Button
          className={classNames(styles.button, styles.replaceButton)}
          variant="light"
          icon={<FontAwesomeIcon icon={faRecycle} />}
          onClick={() => {
            setConfirmationMessage("");
            setIsReplacingToken(true);
          }}
        >
          <FormattedMessage id="settings.integrationSettings.dbtCloudSettings.actions.replace" />
        </Button>
        <Button
          variant="danger"
          className={styles.button}
          onClick={() => {
            deleteToken(void 0, {
              onError: (e) => {
                // TODO pop up error toast
                console.error(e);
              },
              onSuccess: () => {
                // TODO pop up success toast
                console.log("I never liked that token, anyway.");
              },
            });
          }}
          isLoading={isDeletingToken}
          icon={<FontAwesomeIcon icon={faTrash} />}
        >
          <FormattedMessage id="settings.integrationSettings.dbtCloudSettings.actions.delete" />
        </Button>
      </div>
    );
  };

  return (
    <SettingsCard title={<FormattedMessage id="settings.integrationSettings.dbtCloudSettings" />}>
      <div className={styles.cardContent}>
        <Text className={styles.description}>
          <FormattedMessage
            id="settings.integrationSettings.dbtCloudSettings.form.description"
            values={{
              lnk: (node: React.ReactNode) => (
                <a href={links.dbtCloudIntegrationDocs} target="_blank" rel="noreferrer">
                  {node}
                </a>
              ),
            }}
          />
        </Text>
        {hasExistingToken && !isReplacingToken ? <ReplaceOrDeleteToken /> : <ServiceTokenForm />}
      </div>
    </SettingsCard>
  );
};
