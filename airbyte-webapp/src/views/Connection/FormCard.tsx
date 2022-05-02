import { Form, Formik, FormikConfig } from "formik";
import React from "react";
import { useIntl } from "react-intl";
import { useMutation } from "react-query";
import styled from "styled-components";

import { FormChangeTracker } from "components/FormChangeTracker";

import { createFormErrorMessage } from "utils/errorStatusMessage";
import { CollapsibleCardProps, CollapsibleCard } from "views/Connection/CollapsibleCard";
import EditControls from "views/Connection/ConnectionForm/components/EditControls";

const FormContainer = styled(Form)`
  padding: 22px 27px 15px 24px;
`;

export const FormCard: React.FC<
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  CollapsibleCardProps & { bottomSeparator?: boolean; form: FormikConfig<any> }
> = ({ children, form, bottomSeparator = true, ...props }) => {
  const { formatMessage } = useIntl();

  const { mutateAsync, error, reset, isSuccess } = useMutation<
    unknown,
    Error,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    any
  >(async ({ values, formikHelpers }) => form.onSubmit(values, formikHelpers));

  const errorMessage = error ? createFormErrorMessage(error) : null;

  return (
    <Formik {...form} onSubmit={(values, formikHelpers) => mutateAsync({ values, formikHelpers })}>
      {({ resetForm, isSubmitting, dirty, isValid }) => (
        <CollapsibleCard {...props}>
          <FormContainer>
            <FormChangeTracker changed={dirty} />
            {children}
            <div>
              <EditControls
                withLine={bottomSeparator}
                isSubmitting={isSubmitting}
                dirty={dirty}
                resetForm={() => {
                  resetForm();
                  reset();
                }}
                successMessage={isSuccess && formatMessage({ id: "form.changesSaved" })}
                errorMessage={
                  errorMessage ?? !isValid ? formatMessage({ id: "connectionForm.validation.error" }) : null
                }
              />
            </div>
          </FormContainer>
        </CollapsibleCard>
      )}
    </Formik>
  );
};
