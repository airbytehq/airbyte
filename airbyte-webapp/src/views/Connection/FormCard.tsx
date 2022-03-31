import React from "react";
import { Form, Formik, FormikConfig } from "formik";
import { useMutation } from "react-query";
import { useIntl } from "react-intl";
import styled from "styled-components";

import EditControls from "views/Connection/ConnectionForm/components/EditControls";
import {
  CollapsibleCardProps,
  CollapsibleCard,
} from "views/Connection/CollapsibleCard";
import { createFormErrorMessage } from "utils/errorStatusMessage";

const FormContainer = styled(Form)`
  padding: 22px 27px 15px 24px;
`;

export const FormCard: React.FC<
  CollapsibleCardProps & {
    bottomSeparator?: boolean;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    form: FormikConfig<any>;
    readOnly?: boolean;
  }
> = ({ children, form, readOnly, bottomSeparator = true, ...props }) => {
  const { formatMessage } = useIntl();

  const { mutateAsync, error, reset, isSuccess } = useMutation<
    unknown,
    Error,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    any
  >(async ({ values, formikHelpers }) => form.onSubmit(values, formikHelpers));

  const errorMessage = error ? createFormErrorMessage(error) : null;

  return (
    <Formik
      {...form}
      onSubmit={(values, formikHelpers) =>
        mutateAsync({ values, formikHelpers })
      }
    >
      {({ resetForm, isSubmitting, dirty, isValid }) => (
        <CollapsibleCard {...props}>
          <FormContainer>
            {children}
            <div>
              <EditControls
                readOnly={readOnly}
                withLine={bottomSeparator}
                isSubmitting={isSubmitting}
                dirty={dirty}
                resetForm={() => {
                  resetForm();
                  reset();
                }}
                successMessage={
                  isSuccess && formatMessage({ id: "form.changesSaved" })
                }
                errorMessage={
                  errorMessage ?? !isValid
                    ? formatMessage({ id: "connectionForm.validation.error" })
                    : null
                }
              />
            </div>
          </FormContainer>
        </CollapsibleCard>
      )}
    </Formik>
  );
};
