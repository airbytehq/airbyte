import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { Label, LabeledInput, LabeledSwitch, LoadingButton } from "components";
import { InfoTooltip } from "components/base/Tooltip";
import { Row, Cell } from "components/SimpleTableComponents";

import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";

import styles from "./AccountForm.module.scss";

const InputRow = styled(Row)`
  height: auto;
`;

// const ButtonCell = styled(Cell)`
//   &:last-child {
//     text-align: left;
//   }
//   padding-left: 11px;
//   height: 9px;
// `;

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

const AdvancedModeSwitchLabel = () => (
  <>
    <FormattedMessage id="form.advancedMode.switchLabel" />
    <InfoTooltip>
      <FormattedMessage id="form.advancedMode.tooltip" />
    </InfoTooltip>
  </>
);

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
  const [isAdvancedMode, setAdvancedMode] = useAdvancedModeSetting();

  return (
    <Formik
      initialValues={{ email, advancedMode: isAdvancedMode }}
      validateOnBlur
      validateOnChange={false}
      validationSchema={accountValidationSchema}
      enableReinitialize
      onSubmit={(data) => {
        onSubmit(data);
        setAdvancedMode(data.advancedMode);
      }}
    >
      {({ isSubmitting, dirty, values, setFieldValue }) => (
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
          <div className={styles.formItem}>
            <Label>
              <FormattedMessage id="form.advancedMode.label" />
            </Label>
            <Field name="advancedMode">
              {({ field }: FieldProps<boolean>) => (
                <LabeledSwitch
                  label={<AdvancedModeSwitchLabel />}
                  checked={field.value}
                  onChange={() => setFieldValue(field.name, !field.value)}
                />
              )}
            </Field>
          </div>
          <div className={styles.submit}>
            <LoadingButton isLoading={isSubmitting} type="submit" disabled={!dirty || !values.email}>
              <FormattedMessage id="form.saveChanges" />
            </LoadingButton>
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
