import { Form, useFormikContext } from "formik";
import React from "react";

import { Spinner } from "components/ui/Spinner";

import { FormBlock } from "core/form/types";

import { FormSection } from "./components/Sections/FormSection";
import ShowLoadingMessage from "./components/ShowLoadingMessage";
import styles from "./FormRoot.module.scss";
import { useServiceForm } from "./serviceFormContext";
import { ServiceFormValues } from "./types";

interface FormRootProps {
  formFields: FormBlock;
  isTestConnectionInProgress?: boolean;
}

export const FormRoot: React.FC<FormRootProps> = ({ isTestConnectionInProgress = false, formFields }) => {
  const { isSubmitting } = useFormikContext<ServiceFormValues>();
  const { isLoadingSchema, selectedService } = useServiceForm();

  return (
    <Form>
      <FormSection blocks={formFields} disabled={isSubmitting || isTestConnectionInProgress} />
      {isLoadingSchema && (
        <div className={styles.loaderContainer}>
          <Spinner />
          <div className={styles.loadingMessage}>
            <ShowLoadingMessage connector={selectedService?.name} />
          </div>
        </div>
      )}
    </Form>
  );
};
