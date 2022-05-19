import { Field, FieldProps, Formik } from "formik";
import { FormattedMessage, useIntl } from "react-intl";
import { useCounter } from "react-use";
import * as yup from "yup";

import { LabeledInput, LoadingButton } from "components";

import { FieldError } from "../lib/errors/FieldError";
import { useAuthService } from "../services/auth/AuthService";
import { BottomBlock, FieldItem, Form } from "./auth/components/FormComponents";

interface StepProps {
  onStepComplete: () => void;
}

const ValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().min(12, "signup.password.minLength").required("form.empty.error"),
  name: yup.string().required("form.empty.error"),
});

export const EnterEmailStep: React.FC<StepProps> = () => {
  const { formatMessage } = useIntl();
  const authService = useAuthService();

  return (
    <Formik
      initialValues={{
        name: "",
        email: "",
        password: "",
      }}
      validationSchema={ValidationSchema}
      onSubmit={async ({ email, password }, { setFieldError, setStatus }) => {
        try {
          await authService.signUpWithEmailLink({ name: "", email, password });
        } catch (err) {
          if (err instanceof FieldError) {
            setFieldError(err.field, err.message);
          } else {
            setStatus(err.message);
          }
        }
      }}
    >
      {({ isSubmitting, status }) => (
        <Form>
          <FieldItem>
            <Field name="name">
              {({ field, meta }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label={<FormattedMessage id="login.fullName" />}
                  placeholder={formatMessage({
                    id: "login.fullName.placeholder",
                  })}
                  type="text"
                  error={!!meta.error && meta.touched}
                  message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                />
              )}
            </Field>
          </FieldItem>
          <FieldItem>
            <Field name="email">
              {({ field, meta }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label={<FormattedMessage id="login.inviteEmail" />}
                  placeholder={formatMessage({
                    id: "login.yourEmail.placeholder",
                  })}
                  type="email"
                  error={!!meta.error && meta.touched}
                  message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                />
              )}
            </Field>
          </FieldItem>
          <FieldItem>
            <Field name="password">
              {({ field, meta }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label={<FormattedMessage id="login.createPassword" />}
                  placeholder={formatMessage({
                    id: "login.password.placeholder",
                  })}
                  type="password"
                  error={!!meta.error && meta.touched}
                  message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                />
              )}
            </Field>
          </FieldItem>
          <BottomBlock>
            <LoadingButton type="submit" isLoading={isSubmitting} data-testid="login.resetPassword">
              <FormattedMessage id="login.signup" />
            </LoadingButton>
            {status ?? <div className="message">{status}</div>}
          </BottomBlock>
        </Form>
      )}
    </Formik>
  );
};

export const CreatePasswordStep: React.FC = () => {
  const { formatMessage } = useIntl();
  const authService = useAuthService();

  return (
    <Formik
      initialValues={{
        password: "",
      }}
      onSubmit={async ({ password }, { setFieldError, setStatus }) => {
        try {
          await authService.setPassword(password);
        } catch (err) {
          if (err instanceof FieldError) {
            setFieldError(err.field, err.message);
          } else {
            setStatus(err.message);
          }
        }
      }}
    >
      {({ isSubmitting, status }) => (
        <Form>
          <FieldItem>
            <Field name="password">
              {({ field, meta }: FieldProps<string>) => (
                <LabeledInput
                  {...field}
                  label={<FormattedMessage id="login.createPassword" />}
                  placeholder={formatMessage({
                    id: "login.password.placeholder",
                  })}
                  type="password"
                  error={!!meta.error && meta.touched}
                  message={meta.touched && meta.error && formatMessage({ id: meta.error })}
                />
              )}
            </Field>
          </FieldItem>
          <BottomBlock>
            <LoadingButton type="submit" isLoading={isSubmitting} data-testid="login.resetPassword">
              <FormattedMessage id="login.signup" />
            </LoadingButton>
            {status ?? <div className="message">{status}</div>}
          </BottomBlock>
        </Form>
      )}
    </Formik>
  );
};

const STEPS = [EnterEmailStep, CreatePasswordStep];

export const AcceptEmailInvite: React.FC = () => {
  const [step, { inc }] = useCounter();

  const onStepComplete = () => {
    if (step < STEPS.length) {
      inc();
    }
  };

  const StepComponent = STEPS[step];

  return <StepComponent onStepComplete={onStepComplete} />;
};
