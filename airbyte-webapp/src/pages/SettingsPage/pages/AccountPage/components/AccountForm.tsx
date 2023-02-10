import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { LabeledInput } from "components";
import { Row, Cell } from "components/SimpleTableComponents";
import { Button } from "components/ui/Button";

import styles from "./AccountForm.module.scss";

const InputRow = styled(Row)`
  height: auto;
`;

const EmailForm = styled(Form)`
  position: relative;
`;

const Response = styled.div`
  font-size: 13px;
  color: ${({ theme }) => theme.successColor};
  position: absolute;
  bottom: -19px;
`;

const Error = styled(Response)`
  color: ${({ theme }) => theme.dangerColor};
`;

const Success = styled.div`
  color: ${({ theme }) => theme.successColor};
`;

const accountValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
});

interface AccountFormProps {
  email: string;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  onSubmit: (data: { email: string }) => void;
}

const AccountForm: React.FC<AccountFormProps> = ({ email, onSubmit, successMessage, errorMessage }) => {
  const { formatMessage } = useIntl();

  return (
    <Formik
      initialValues={{ email }}
      validateOnBlur
      validateOnChange={false}
      validationSchema={accountValidationSchema}
      enableReinitialize
      onSubmit={(data) => {
        onSubmit(data);
      }}
    >
      {({ isSubmitting, dirty, values }) => (
        <EmailForm>
          <InputRow className={styles.formItem}>
            <Cell flex={3}>
              <Field name="email">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    placeholder={formatMessage({
                      id: "form.email.placeholder",
                    })}
                    error={!!meta.error && meta.touched}
                    message={!!meta.error && meta.touched ? <FormattedMessage id={meta.error} /> : ""}
                    label={<FormattedMessage id="form.yourEmail" />}
                  />
                )}
              </Field>
            </Cell>
          </InputRow>
          <div className={styles.submit}>
            <Button isLoading={isSubmitting} type="submit" disabled={!dirty || !values.email}>
              <FormattedMessage id="form.saveChanges" />
            </Button>
          </div>
          {!dirty &&
            (successMessage ? (
              <Success>{successMessage}</Success>
            ) : errorMessage ? (
              <Error>{errorMessage}</Error>
            ) : null)}
        </EmailForm>
      )}
    </Formik>
  );
};

export default AccountForm;
