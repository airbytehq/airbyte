import { Field, FieldProps, Formik } from "formik";
import { FormattedMessage, useIntl } from "react-intl";

import { LabeledInput, LoadingButton } from "components";

import { FieldError } from "../lib/errors/FieldError";
import { useAuthService } from "../services/auth/AuthService";
import { BottomBlock, FieldItem, Form } from "./auth/components/FormComponents";
import { FormTitle } from "./auth/components/FormTitle";

export const AcceptEmailInvite: React.FC = () => {
  const { formatMessage } = useIntl();
  const authService = useAuthService();

  return (
    <>
      <FormTitle bold>You've been invited!</FormTitle>
      <Formik
        initialValues={{
          email: "",
        }}
        onSubmit={async ({ email }, { setFieldError, setStatus }) => {
          try {
            await authService.signInWithEmailLink(email);
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
            <BottomBlock>
              <LoadingButton type="submit" isLoading={isSubmitting} data-testid="login.resetPassword">
                <FormattedMessage id="form.continue" />
              </LoadingButton>
              {status ?? <div className="message">{status}</div>}
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </>
  );
};
