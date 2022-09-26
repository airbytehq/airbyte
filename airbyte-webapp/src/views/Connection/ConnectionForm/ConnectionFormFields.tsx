import { faSyncAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { Field, FieldProps, Form } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

import { Button, Card, ControlLabels, Input } from "components";
import { Text } from "components/base/Text";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { ValuesProps } from "hooks/services/useConnectionHook";

import { NamespaceDefinitionField } from "./components/NamespaceDefinitionField";
import ScheduleField from "./components/ScheduleField";
import { Section } from "./components/Section";
import SchemaField from "./components/SyncCatalogField";
import styles from "./ConnectionFormFields.module.scss";
import { FormikConnectionFormValues } from "./formConfig";

interface ConnectionFormFieldsProps {
  className?: string;
  values: ValuesProps | FormikConnectionFormValues;
  isSubmitting: boolean;
  refreshSchema: () => void;
}

export const ConnectionFormFields: React.FC<ConnectionFormFieldsProps> = ({
  className,
  values,
  isSubmitting,
  refreshSchema,
}) => {
  const { mode } = useConnectionFormService();
  const { formatMessage } = useIntl();

  const formContainerClassnames = classNames(className, styles.formContainer);
  const readonlyClass = classNames({
    [styles.readonly]: mode === "readonly",
  });

  return (
    <Form className={formContainerClassnames}>
      <Section title={<FormattedMessage id="connection.transfer" />}>
        <ScheduleField />
      </Section>
      <Card>
        <div className={styles.styledSection}>
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
        </div>
        <div className={styles.styledSection}>
          <Field
            name="syncCatalog.streams"
            component={SchemaField}
            isSubmitting={isSubmitting}
            additionalControl={
              <Button onClick={refreshSchema} type="button" secondary>
                <FontAwesomeIcon icon={faSyncAlt} className={styles.tryArrow} />
                <FormattedMessage id="connection.updateSchema" />
              </Button>
            }
          />
        </div>
      </Card>
    </Form>
  );
};
