import { faSyncAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classNames from "classnames";
import { Field, FieldProps } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useUnmount } from "react-use";

import { ControlLabels } from "components";
import { FormChangeTracker } from "components/common/FormChangeTracker";
import { Button } from "components/ui/Button";
import { FlexContainer } from "components/ui/Flex";
import { Input } from "components/ui/Input";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { FeatureItem, useFeature } from "hooks/services/Feature";
import { useFormChangeTrackerService } from "hooks/services/FormChangeTracker";
import { ValuesProps } from "hooks/services/useConnectionHook";

import { NamespaceDefinitionField } from "./components/NamespaceDefinitionField";
import { NonBreakingChangesPreferenceField } from "./components/NonBreakingChangesPreferenceField";
import { useRefreshSourceSchemaWithConfirmationOnDirty } from "./components/refreshSourceSchemaWithConfirmationOnDirty";
import { Section } from "./components/Section";
import { SyncCatalogField } from "./components/SyncCatalogField";
import styles from "./ConnectionFormFields.module.scss";
import { FormikConnectionFormValues } from "./formConfig";
import { ScheduleField } from "./ScheduleField";

interface ConnectionFormFieldsProps {
  values: ValuesProps | FormikConnectionFormValues;
  isSubmitting: boolean;
  dirty: boolean;
}

export const ConnectionFormFields: React.FC<ConnectionFormFieldsProps> = ({ values, isSubmitting, dirty }) => {
  const allowAutoDetectSchema = useFeature(FeatureItem.AllowAutoDetectSchema);

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

  const isNewStreamsTableEnabled = process.env.REACT_APP_NEW_STREAMS_TABLE ?? false;
  const firstSectionTitle = isNewStreamsTableEnabled ? undefined : <FormattedMessage id="connection.transfer" />;

  return (
    <>
      {/* FormChangeTracker is here as it has access to everything it needs without being repeated */}
      <FormChangeTracker changed={dirty} formId={formId} />
      <div className={styles.formContainer}>
        <Section title={firstSectionTitle}>
          <ScheduleField />
          {allowAutoDetectSchema && (
            <Field name="nonBreakingChangesPreference" component={NonBreakingChangesPreferenceField} />
          )}
        </Section>
        {!isNewStreamsTableEnabled && (
          <Section title={<FormattedMessage id="connection.streams" />}>
            <span className={readonlyClass}>
              <Field name="namespaceDefinition" component={NamespaceDefinitionField} />
            </span>
            {values.namespaceDefinition === NamespaceDefinitionType.customformat && (
              <Field name="namespaceFormat">
                {({ field, meta }: FieldProps<string>) => (
                  <FlexContainer alignItems="flex-start">
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
                  </FlexContainer>
                )}
              </Field>
            )}
            <Field name="prefix">
              {({ field }: FieldProps<string>) => (
                <FlexContainer alignItems="flex-start">
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
                </FlexContainer>
              )}
            </Field>
          </Section>
        )}
        <Section className={styles.flush}>
          <Field
            name="syncCatalog.streams"
            component={SyncCatalogField}
            isSubmitting={isSubmitting}
            additionalControl={
              <Button
                onClick={refreshSchema}
                type="button"
                variant="secondary"
                data-testid="refresh-source-schema-btn"
                disabled={isSubmitting}
              >
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
