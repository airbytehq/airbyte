import { Form, useFormikContext } from "formik";
import React, { ReactNode } from "react";

import { Card } from "components/ui/Card";
import { FlexContainer } from "components/ui/Flex";

import { FormBlock } from "core/form/types";

import { FormSection } from "./components/Sections/FormSection";
import { useConnectorForm } from "./connectorFormContext";
import styles from "./FormRoot.module.scss";
import { ConnectorFormValues } from "./types";

export interface BaseFormRootProps {
  formFields: FormBlock;
  connectionTestSuccess?: boolean;
  isTestConnectionInProgress?: boolean;
  bodyClassName?: string;
  headerBlock?: ReactNode;
  castValues: (values: ConnectorFormValues) => ConnectorFormValues;
  renderFooter?: (formProps: {
    dirty: boolean;
    isSubmitting: boolean;
    isValid: boolean;
    resetConnectorForm: () => void;
    isEditMode?: boolean;
    formType: "source" | "destination";
    getValues: () => ConnectorFormValues;
  }) => ReactNode;
}

interface CardFormRootProps extends BaseFormRootProps {
  renderWithCard: true;
  title?: React.ReactNode;
  description?: React.ReactNode;
  full?: boolean;
}

interface BareFormRootProps extends BaseFormRootProps {
  renderWithCard?: false;
}

export const FormRoot: React.FC<CardFormRootProps | BareFormRootProps> = ({
  isTestConnectionInProgress = false,
  formFields,
  bodyClassName,
  headerBlock,
  renderFooter,
  castValues,
  ...props
}) => {
  const { dirty, isSubmitting, isValid, values } = useFormikContext<ConnectorFormValues>();
  const { resetConnectorForm, isEditMode, formType } = useConnectorForm();

  const formBody = (
    <>
      {headerBlock}
      <div className={bodyClassName}>
        <FormSection blocks={formFields} disabled={isSubmitting || isTestConnectionInProgress} />
      </div>
    </>
  );

  return (
    <Form>
      <FlexContainer direction="column" gap="xl">
        {props.renderWithCard ? (
          <Card title={props.title} description={props.description} fullWidth={props.full}>
            <div className={styles.cardForm}>{formBody}</div>
          </Card>
        ) : (
          formBody
        )}
        {renderFooter &&
          renderFooter({
            dirty,
            isSubmitting,
            isValid,
            resetConnectorForm,
            isEditMode,
            formType,
            getValues: () => castValues(values),
          })}
      </FlexContainer>
    </Form>
  );
};
