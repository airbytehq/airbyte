import { faSyncAlt } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Field, FieldProps, Form } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { Button, Card, ControlLabels, H5, Input } from "components";

import { NamespaceDefinitionType } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { ValuesProps } from "hooks/services/useConnectionHook";

import { NamespaceDefinitionField } from "./components/NamespaceDefinitionField";
import ScheduleField from "./components/ScheduleField";
import SchemaField from "./components/SyncCatalogField";
import { FormikConnectionFormValues } from "./formConfig";

interface SectionProps {
  title?: React.ReactNode;
}

const TryArrow = styled(FontAwesomeIcon)`
  margin: 0 10px -1px 0;
  font-size: 14px;
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

export const LabelHeading = styled(H5)`
  line-height: 16px;
  display: inline;
`;

export const ConnectorLabel = styled(ControlLabels)`
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

export const FormContainer = styled(Form)`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

export const Section: React.FC<React.PropsWithChildren<SectionProps>> = ({ title, children }) => (
  <Card>
    <StyledSection>
      {title && <H5 bold>{title}</H5>}
      {children}
    </StyledSection>
  </Card>
);

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

  return (
    <FormContainer className={className}>
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
            component={SchemaField}
            isSubmitting={isSubmitting}
            additionalControl={
              <Button onClick={refreshSchema} type="button" secondary>
                <TryArrow icon={faSyncAlt} />
                <FormattedMessage id="connection.updateSchema" />
              </Button>
            }
          />
        </StyledSection>
      </Card>
    </FormContainer>
  );
};
