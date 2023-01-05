import { yupResolver } from "@hookform/resolvers/yup";
import React, { useEffect, useMemo } from "react";
import { useForm, Controller } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";
import * as yup from "yup";

import { Label, LabeledInput, LabeledSwitch } from "components";
import { Row, Cell } from "components/SimpleTableComponents";
import { Button } from "components/ui/Button";
import { InfoTooltip } from "components/ui/Tooltip";

import { useAdvancedModeSetting } from "hooks/services/useAdvancedModeSetting";

import styles from "./AccountForm.module.scss";

const InputRow = styled(Row)`
  height: auto;
`;

const EmailForm = styled.form`
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
  const defaultValues = useMemo(() => ({ email, advancedMode: isAdvancedMode }), [email, isAdvancedMode]);
  const {
    handleSubmit,
    control,
    reset,
    // What you get from the render prop in formik
    formState: { isSubmitting, isDirty, isValid },
  } = useForm({
    // This is what validateOnBlur is doing
    mode: "onBlur",
    // same as formik
    defaultValues,
    // validationSchema prop
    resolver: yupResolver(accountValidationSchema),
  });

  // This is what enableReinitalize is doing
  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  return (
    <EmailForm
      onSubmit={handleSubmit((data) => {
        onSubmit(data);
        setAdvancedMode(data.advancedMode);
        reset();
      })}
    >
      <InputRow className={styles.formItem}>
        <Cell flex={3}>
          {/* This is what "Field" is in formik - you can get the "control" variable from the useFormContext hook in a nested place (form needs to be wrapped with FormProvider in this case) */}
          <Controller
            name="email"
            control={control}
            render={({ field, fieldState }) => (
              <LabeledInput
                {...field}
                placeholder={formatMessage({
                  id: "form.email.placeholder",
                })}
                error={!!fieldState.error && fieldState.isTouched}
                message={
                  !!fieldState.error && fieldState.isTouched ? <FormattedMessage id={fieldState.error.message} /> : ""
                }
                label={<FormattedMessage id="form.yourEmail" />}
              />
            )}
          />
        </Cell>
      </InputRow>
      <div className={styles.formItem}>
        <Label>
          <FormattedMessage id="form.advancedMode.label" />
        </Label>
        <Controller
          name="advancedMode"
          control={control}
          render={({ field }) => (
            <LabeledSwitch
              label={<AdvancedModeSwitchLabel />}
              checked={field.value}
              onChange={() => field.onChange(!field.value)}
            />
          )}
        />
      </div>
      <div className={styles.submit}>
        <Button isLoading={isSubmitting} type="submit" disabled={!isDirty || !isValid}>
          <FormattedMessage id="form.saveChanges" />
        </Button>
      </div>
      {!isDirty &&
        (successMessage ? <Success>{successMessage}</Success> : errorMessage ? <Error>{errorMessage}</Error> : null)}
    </EmailForm>
  );
};

export default AccountForm;
