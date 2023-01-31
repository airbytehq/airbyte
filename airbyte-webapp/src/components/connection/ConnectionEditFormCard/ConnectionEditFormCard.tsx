import { Form, Formik, FormikConfig, FormikHelpers } from "formik";
import React from "react";
import { useIntl } from "react-intl";
import { useMutation } from "react-query";

import { FormChangeTracker } from "components/common/FormChangeTracker";
import { CollapsibleCardProps, CollapsibleCard } from "components/ui/CollapsibleCard";

import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { generateMessageFromError } from "utils/errorStatusMessage";

import styles from "./ConnectionEditFormCard.module.scss";
import EditControls from "../ConnectionForm/EditControls";

interface FormCardProps<T> extends CollapsibleCardProps {
  form: FormikConfig<T>;
  submitDisabled?: boolean;
}

export const ConnectionEditFormCard = <T extends object>({
  children,
  form,
  submitDisabled,
  ...props
}: React.PropsWithChildren<FormCardProps<T>>) => {
  const { formatMessage } = useIntl();
  const { mode } = useConnectionFormService();

  const { mutateAsync, error, reset, isSuccess } = useMutation<
    void,
    Error,
    { values: T; formikHelpers: FormikHelpers<T> }
  >(async ({ values, formikHelpers }) => {
    await form.onSubmit(values, formikHelpers);
  });

  const errorMessage = error ? generateMessageFromError(error) : null;

  return (
    <Formik {...form} onSubmit={(values, formikHelpers) => mutateAsync({ values, formikHelpers })}>
      {({ resetForm, isSubmitting, dirty, isValid }) => (
        <CollapsibleCard {...props}>
          <Form className={styles.formCard}>
            <FormChangeTracker changed={dirty} />
            {children}
            <div className={styles.editControls}>
              {mode !== "readonly" && (
                <EditControls
                  isSubmitting={isSubmitting}
                  dirty={dirty}
                  submitDisabled={!isValid || submitDisabled}
                  resetForm={() => {
                    resetForm();
                    reset();
                  }}
                  successMessage={isSuccess && formatMessage({ id: "form.changesSaved" })}
                  errorMessage={
                    errorMessage ?? !isValid ? formatMessage({ id: "connectionForm.validation.error" }) : null
                  }
                />
              )}
            </div>
          </Form>
        </CollapsibleCard>
      )}
    </Formik>
  );
};
