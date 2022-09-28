import classNames from "classnames";
import { Field, FieldProps, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useToggle } from "react-use";
import styled from "styled-components";

import { FormChangeTracker } from "components/FormChangeTracker";
import { ControlLabels } from "components/LabeledControl";
import { Card } from "components/ui/Card";
import { Input } from "components/ui/Input";
import { Text } from "components/ui/Text";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

import CreateControls from "./components/CreateControls";
import EditControls from "./components/EditControls";
import { NamespaceDefinitionField } from "./components/NamespaceDefinitionField";
import { OperationsSection } from "./components/OperationsSection";
import ScheduleField from "./components/ScheduleField";
import { Section } from "./components/Section";
import SchemaField from "./components/SyncCatalogField";
import styles from "./ConnectionForm.module.css";
import { connectionValidationSchema } from "./formConfig";

// This is removed in KC's main refactor PR.  Removing it would require major scope creep for this PR.
const ConnectorLabel = styled(ControlLabels)`
  max-width: 328px;
  margin-right: 20px;
  vertical-align: top;
`;

export type ConnectionFormMode = "create" | "edit" | "readonly";

export interface ConnectionFormProps {
  successMessage?: React.ReactNode;

  /** Should be passed when connection is updated with withRefreshCatalog flag */
  canSubmitUntouchedForm?: boolean;
  additionalSchemaControl?: React.ReactNode;
}

export const ConnectionForm: React.FC<ConnectionFormProps> = ({
  successMessage,
  canSubmitUntouchedForm,
  additionalSchemaControl,
}) => {
  const { initialValues, formId, mode, onFormSubmit, errorMessage, onCancel } = useConnectionFormService();

  const [editingTransformation, toggleEditingTransformation] = useToggle(false);
  const { formatMessage } = useIntl();

  const readonlyClass = classNames({
    [styles.readonly]: mode === "readonly",
  });

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={connectionValidationSchema}
      enableReinitialize
      onSubmit={onFormSubmit}
    >
      {({ isSubmitting, isValid, dirty, resetForm, values }) => (
        <div className={styles.formContainer}>
          <FormChangeTracker changed={dirty} formId={formId} />
          {mode === "create" && (
            <Section>
              <Field name="name">
                {({ field, meta }: FieldProps<string>) => (
                  <div className={styles.flexRow}>
                    <div className={styles.leftFieldCol}>
                      <ConnectorLabel
                        nextLine
                        error={!!meta.error && meta.touched}
                        label={
                          <Text as="h5">
                            <FormattedMessage id="form.connectionName" />
                          </Text>
                        }
                        message={formatMessage({
                          id: "form.connectionName.message",
                        })}
                      />
                    </div>
                    <div className={styles.RightFieldCol}>
                      <Input
                        {...field}
                        error={!!meta.error}
                        data-testid="connectionName"
                        placeholder={formatMessage({
                          id: "form.connectionName.placeholder",
                        })}
                      />
                    </div>
                  </div>
                )}
              </Field>
            </Section>
          )}
          <Section title={<FormattedMessage id="connection.transfer" />}>
            <ScheduleField />
          </Section>
          <Card>
            <Section>
              <Text as="h5">
                <FormattedMessage id="connection.streams" />
              </Text>
              <span style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
                <Field name="namespaceDefinition" component={NamespaceDefinitionField} />
              </span>
              {values.namespaceDefinition === NamespaceDefinitionType.customformat && (
                <Field name="namespaceFormat">
                  {({ field, meta }: FieldProps<string>) => (
                    <div className={styles.flexRow}>
                      <div className={styles.leftFieldCol}>
                        <ControlLabels
                          className={styles.NamespaceFormatLabel}
                          nextLine
                          error={!!meta.error}
                          label={<FormattedMessage id="connectionForm.namespaceFormat.title" />}
                          message={<FormattedMessage id="connectionForm.namespaceFormat.subtitle" />}
                        />
                      </div>
                      <div className={classNames(styles.rightFieldCol, readonlyClass)}>
                        <Input
                          {...field}
                          error={!!meta.error}
                          placeholder={formatMessage({
                            id: "connectionForm.namespaceFormat.placeholder",
                          })}
                        />
                      </div>
                    </div>
                  )}
                </Field>
              )}
              <Field name="prefix">
                {({ field }: FieldProps<string>) => (
                  <div className={styles.flexRow}>
                    <div className={styles.leftFieldCol}>
                      <ControlLabels
                        nextLine
                        label={formatMessage({
                          id: "form.prefix",
                        })}
                        message={formatMessage({
                          id: "form.prefix.message",
                        })}
                      />
                    </div>
                    <div className={styles.rightFieldCol}>
                      <Input
                        {...field}
                        type="text"
                        placeholder={formatMessage({
                          id: `form.prefix.placeholder`,
                        })}
                        data-testid="prefixInput"
                        style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}
                      />
                    </div>
                  </div>
                )}
              </Field>
            </Section>
            <Section>
              <Field
                name="syncCatalog.streams"
                additionalControl={additionalSchemaControl}
                component={SchemaField}
                isSubmitting={isSubmitting}
              />
            </Section>
          </Card>
          {mode === "edit" && (
            <EditControls
              isSubmitting={isSubmitting}
              dirty={dirty}
              resetForm={() => {
                resetForm();
                onCancel?.();
              }}
              successMessage={successMessage}
              errorMessage={!isValid && errorMessage}
              enableControls={canSubmitUntouchedForm}
            />
          )}
          {mode === "create" && (
            <>
              <OperationsSection
                onStartEditTransformation={toggleEditingTransformation}
                onEndEditTransformation={toggleEditingTransformation}
              />
              <CreateControls
                isSubmitting={isSubmitting}
                isValid={isValid && !editingTransformation}
                errorMessage={!isValid && errorMessage}
              />
            </>
          )}
        </div>
      )}
    </Formik>
  );
};
