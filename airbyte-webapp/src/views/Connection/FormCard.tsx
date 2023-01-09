import { Form, Formik, FormikConfig, FormikHelpers } from "formik";
import React from "react";
import { useIntl } from "react-intl";
import { useMutation } from "react-query";

import { FormChangeTracker } from "components/common/FormChangeTracker";

import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { generateMessageFromError } from "utils/errorStatusMessage";
import { CollapsibleCardProps, CollapsibleCard } from "views/Connection/CollapsibleCard";
import EditControls from "views/Connection/ConnectionForm/components/EditControls";

import styles from "./FormCard.module.scss";

interface FormCardProps<T> extends CollapsibleCardProps {
  bottomSeparator?: boolean;
  form: FormikConfig<T>;
  submitDisabled?: boolean;
}

export const FormCard = <T extends object>({
  children,
  form,
  bottomSeparator = true,
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
    form.onSubmit(values, formikHelpers);
  });

  const errorMessage = error ? generateMessageFromError(error) : null;

  return (
    <Formik {...form} onSubmit={(values, formikHelpers) => mutateAsync({ values, formikHelpers })}>
      {({ resetForm, isSubmitting, dirty, isValid }) => (
        <CollapsibleCard {...props}>
          <Form className={styles.formCard}>
            <FormChangeTracker changed={dirty} />
            {children}
            <div>
              {mode !== "readonly" && (
                <EditControls
                  withLine={bottomSeparator}
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
