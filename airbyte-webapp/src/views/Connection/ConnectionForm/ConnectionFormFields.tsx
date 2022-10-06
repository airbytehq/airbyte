import { faSyncAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { Field, FieldProps } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useUnmount } from "react-use";

import { ControlLabels } from "components";
import { FormChangeTracker } from "components/FormChangeTracker";
import { Button } from "components/ui/Button";
import { Input } from "components/ui/Input";
import { Text } from "components/ui/Text";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { useFormChangeTrackerService } from "hooks/services/FormChangeTracker";
import { ValuesProps } from "hooks/services/useConnectionHook";

import { NamespaceDefinitionField } from "./components/NamespaceDefinitionField";
import { useRefreshSourceSchemaWithConfirmationOnDirty } from "./components/refreshSourceSchemaWithConfirmationOnDirty";
import ScheduleField from "./components/ScheduleField";
import { Section } from "./components/Section";
import SchemaField from "./components/SyncCatalogField";
import styles from "./ConnectionFormFields.module.scss";
import { FormikConnectionFormValues } from "./formConfig";

interface ConnectionFormFieldsProps {
  values: ValuesProps | FormikConnectionFormValues;
  isSubmitting: boolean;
  dirty: boolean;
}

export const ConnectionFormFields: React.FC<ConnectionFormFieldsProps> = ({ values, isSubmitting, dirty }) => {
  const { mode, formId } = useConnectionFormService();
  const { formatMessage } = useIntl();
  const { clearFormChange } = useFormChangeTrackerService();

  const readonlyClass = classNames({
    [styles.readonly]: mode === "readonly",
  });

  const refreshSchema = useRefreshSourceSchemaWithConfirmationOnDirty(dirty);

  useUnmount(() => {
    clearFormChange(formId);
  });

  return (
    <>
      {/* FormChangeTracker is here as it has access to everything it needs without being repeated */}
      <FormChangeTracker changed={dirty} formId={formId} />
      <div className={styles.formContainer}>
        <Section title={<FormattedMessage id="connection.transfer" />}>
          <ScheduleField />
        </Section>
        <Section>
          <Text as="h5">
            <FormattedMessage id="connection.streams" />
          </Text>
          <span className={readonlyClass}>
            <Field name="namespaceDefinition" component={NamespaceDefinitionField} />
          </span>
          {values.namespaceDefinition === NamespaceDefinitionType.customformat && (
            <Field name="namespaceFormat">
              {({ field, meta }: FieldProps<string>) => (
                <div className={styles.flexRow}>
                  <div className={styles.leftFieldCol}>
                    <ControlLabels
                      className={styles.namespaceFormatLabel}
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
            component={SchemaField}
            isSubmitting={isSubmitting}
            additionalControl={
              <Button onClick={refreshSchema} type="button" variant="secondary">
                <FontAwesomeIcon icon={faSyncAlt} className={styles.tryArrow} />
                <FormattedMessage id="connection.updateSchema" />
              </Button>
            }
          />
        </Section>
      </div>
    </>
  );
};
