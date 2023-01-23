import { Form, useFormikContext } from "formik";
import React, { ReactNode } from "react";

import { Card } from "components/ui/Card";
import { FlexContainer } from "components/ui/Flex";

import { FormBlock } from "core/form/types";

import { FormSection } from "./components/Sections/FormSection";
import { useConnectorForm } from "./connectorFormContext";
import styles from "./FormRoot.module.scss";
import { ConnectorFormValues } from "./types";

interface FormRootProps {
  title?: React.ReactNode;
  description?: React.ReactNode;
  full?: boolean;
  formFields: FormBlock;
  connectionTestSuccess?: boolean;
  isTestConnectionInProgress?: boolean;
  onRetest?: () => void;
  onStopTestingConnector?: () => void;
  submitLabel?: string;
  footerClassName?: string;
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
  renderWithCard?: boolean;
  /**
   * Called in case the user cancels the form - if not provided, no cancel button is rendered
   */
  onCancel?: () => void;
  /**
   * Called in case the user reset the form - if not provided, no reset button is rendered
   */
  onReset?: () => void;
}

export const FormRoot: React.FC<FormRootProps> = ({
  isTestConnectionInProgress = false,
  formFields,
  bodyClassName,
  headerBlock,
  renderFooter,
  title,
  description,
  renderWithCard,
  castValues,
  full,
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
        {renderWithCard ? (
          <Card title={title} description={description} fullWidth={full}>
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
