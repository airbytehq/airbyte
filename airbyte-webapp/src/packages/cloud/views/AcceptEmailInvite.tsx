import { Field, FieldProps, Formik } from "formik";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import { H1, LabeledInput, LoadingButton } from "components";
import HeadTitle from "components/HeadTitle";

import { FieldError } from "../lib/errors/FieldError";
import { useAuthService } from "../services/auth/AuthService";
import { BottomBlock, FieldItem, Form } from "./auth/components/FormComponents";

const ValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().min(12, "signup.password.minLength").required("form.empty.error"),
  name: yup.string().required("form.empty.error"),
});

export const AcceptEmailInvite: React.FC = () => {
  const { formatMessage } = useIntl();
  const authService = useAuthService();

  const formElement = (
    <Formik
      initialValues={{
        name: "",
        email: "",
        password: "",
      }}
      validationSchema={ValidationSchema}
      onSubmit={async ({ name, email, password }, { setFieldError, setStatus }) => {
        try {
          await authService.signUpWithEmailLink({ name, email, password });
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
            <LoadingButton type="submit" isLoading={isSubmitting} data-testid="login.signup">
              <FormattedMessage id="login.signup" />
            </LoadingButton>
            {status ?? <div className="message">{status}</div>}
          </BottomBlock>
        </Form>
      )}
    </Formik>
  );

  return (
    <>
      <HeadTitle titles={[{ id: "login.inviteTitle" }]} />
      <H1 bold>
        <FormattedMessage id="login.inviteTitle" />
      </H1>
      {formElement}
    </>
  );
};
