import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { useToggle } from "react-use";
import styled from "styled-components";

import { Card, ControlLabels, H5, Input } from "components";
import { FormChangeTracker } from "components/FormChangeTracker";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/Connection/ConnectionFormService";

import CreateControls from "./components/CreateControls";
import EditControls from "./components/EditControls";
import { NamespaceDefinitionField } from "./components/NamespaceDefinitionField";
import { OperationsSection } from "./components/OperationsSection";
import ScheduleField from "./components/ScheduleField";
import SchemaField from "./components/SyncCatalogField";
import { connectionValidationSchema } from "./formConfig";

const ConnectorLabel = styled(ControlLabels)`
  max-width: 328px;
  margin-right: 20px;
  vertical-align: top;
`;

const NamespaceFormatLabel = styled(ControlLabels)`
  flex: 5 0 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
`;

export const FlexRow = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 10px;
`;

export const LeftFieldCol = styled.div`
  flex: 1;
  max-width: 640px;
  padding-right: 30px;
`;

export const RightFieldCol = styled.div`
  flex: 1;
  max-width: 300px;
`;

export const StyledSection = styled.div`
  padding: 20px 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;

  &:not(:last-child) {
    box-shadow: 0 1px 0 rgba(139, 139, 160, 0.25);
  }
`;

interface SectionProps {
  title?: React.ReactNode;
}

const LabelHeading = styled(H5)`
  line-height: 16px;
  display: inline;
`;

const Section: React.FC<React.PropsWithChildren<SectionProps>> = ({ title, children }) => (
  <Card>
    <StyledSection>
      {title && <H5 bold>{title}</H5>}
      {children}
    </StyledSection>
  </Card>
);

const FormContainer = styled(Form)`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

export type ConnectionFormMode = "create" | "edit" | "readonly";

export interface ConnectionFormProps {
  className?: string;
  successMessage?: React.ReactNode;

  /** Should be passed when connection is updated with withRefreshCatalog flag */
  canSubmitUntouchedForm?: boolean;
  additionalSchemaControl?: React.ReactNode;
}

export const ConnectionForm: React.FC<ConnectionFormProps> = ({
  className,
  successMessage,
  canSubmitUntouchedForm,
  additionalSchemaControl,
}) => {
  const { initialValues, formId, mode, onFormSubmit, errorMessage, onCancel } = useConnectionFormService();

  const [editingTransformation, toggleEditingTransformation] = useToggle(false);
  const { formatMessage } = useIntl();

  return (
    <Formik
      initialValues={initialValues}
      validationSchema={connectionValidationSchema}
      enableReinitialize
      onSubmit={onFormSubmit}
    >
      {({ isSubmitting, isValid, dirty, resetForm, values }) => (
        <FormContainer className={className}>
          <FormChangeTracker changed={dirty} formId={formId} />
          {mode === "create" && (
            <Section>
              <Field name="name">
                {({ field, meta }: FieldProps<string>) => (
                  <FlexRow>
                    <LeftFieldCol>
                      <ConnectorLabel
                        nextLine
                        error={!!meta.error && meta.touched}
                        label={
                          <LabelHeading bold>
                            <FormattedMessage id="form.connectionName" />
                          </LabelHeading>
                        }
                        message={formatMessage({
                          id: "form.connectionName.message",
                        })}
                      />
                    </LeftFieldCol>
                    <RightFieldCol>
                      <Input
                        {...field}
                        error={!!meta.error}
                        data-testid="connectionName"
                        placeholder={formatMessage({
                          id: "form.connectionName.placeholder",
                        })}
                      />
                    </RightFieldCol>
                  </FlexRow>
                )}
              </Field>
            </Section>
          )}
          <Section title={<FormattedMessage id="connection.transfer" />}>
            <ScheduleField />
          </Section>
          <Card>
            <StyledSection>
              <H5 bold>
                <FormattedMessage id="connection.streams" />
              </H5>
              <span style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
                <Field name="namespaceDefinition" component={NamespaceDefinitionField} />
              </span>
              {values.namespaceDefinition === NamespaceDefinitionType.customformat && (
                <Field name="namespaceFormat">
                  {({ field, meta }: FieldProps<string>) => (
                    <FlexRow>
                      <LeftFieldCol>
                        <NamespaceFormatLabel
                          nextLine
                          error={!!meta.error}
                          label={<FormattedMessage id="connectionForm.namespaceFormat.title" />}
                          message={<FormattedMessage id="connectionForm.namespaceFormat.subtitle" />}
                        />
                      </LeftFieldCol>
                      <RightFieldCol style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}>
                        <Input
                          {...field}
                          error={!!meta.error}
                          placeholder={formatMessage({
                            id: "connectionForm.namespaceFormat.placeholder",
                          })}
                        />
                      </RightFieldCol>
                    </FlexRow>
                  )}
                </Field>
              )}
              <Field name="prefix">
                {({ field }: FieldProps<string>) => (
                  <FlexRow>
                    <LeftFieldCol>
                      <ControlLabels
                        nextLine
                        label={formatMessage({
                          id: "form.prefix",
                        })}
                        message={formatMessage({
                          id: "form.prefix.message",
                        })}
                      />
                    </LeftFieldCol>
                    <RightFieldCol>
                      <Input
                        {...field}
                        type="text"
                        placeholder={formatMessage({
                          id: `form.prefix.placeholder`,
                        })}
                        data-testid="prefixInput"
                        style={{ pointerEvents: mode === "readonly" ? "none" : "auto" }}
                      />
                    </RightFieldCol>
                  </FlexRow>
                )}
              </Field>
            </StyledSection>
            <StyledSection>
              <Field
                name="syncCatalog.streams"
                additionalControl={additionalSchemaControl}
                component={SchemaField}
                isSubmitting={isSubmitting}
              />
            </StyledSection>
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
              errorMessage={errorMessage}
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
                errorMessage={errorMessage}
              />
            </>
          )}
        </FormContainer>
      )}
    </Formik>
  );
};
