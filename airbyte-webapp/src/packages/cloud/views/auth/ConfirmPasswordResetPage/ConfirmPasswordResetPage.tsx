import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import { Field, FieldProps, Formik } from "formik";
import * as yup from "yup";

import { LabeledInput, Link, LoadingButton } from "components";
import useRouterHook from "hooks/useRouter";

import { Routes } from "packages/cloud/routes";
import { useAuthService } from "packages/cloud/services/auth/AuthService";
import { FormTitle } from "../components/FormTitle";

import { BottomBlock, FieldItem, Form } from "../components/FormComponents";

const ResetPasswordPageValidationSchema = yup.object().shape({
  newPassword: yup.string().required("form.empty.error"),
});

const ResetPasswordConfirmPage: React.FC = () => {
  const { confirmPasswordReset } = useAuthService();
  const { push, query } = useRouterHook<{ oobCode: string }>();
  const formatMessage = useIntl().formatMessage;

  return (
    <div>
      <FormTitle bold>
        <FormattedMessage id="login.resetPassword" />
      </FormTitle>

      <Formik
        initialValues={{
          newPassword: "",
        }}
        validationSchema={ResetPasswordPageValidationSchema}
        onSubmit={async ({ newPassword }) => {
          await confirmPasswordReset(query.oobCode, newPassword);
          push(Routes.Login);
        }}
        validateOnBlur={true}
        validateOnChange={false}
      >
        {({ isSubmitting }) => (
          <Form>
            <FieldItem>
              <Field name="newPassword">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label={
                      <FormattedMessage id="confirmRestPassword.yourNewPassword" />
                    }
                    placeholder={formatMessage({
                      id: "confirmRestPassword.yourNewPassword.placeholder",
                    })}
                    type="password"
                    error={!!meta.error && meta.touched}
                    message={
                      meta.touched &&
                      meta.error &&
                      formatMessage({ id: meta.error })
                    }
                  />
                )}
              </Field>
            </FieldItem>
            <BottomBlock>
              <Link to={Routes.Login} $light>
                <FormattedMessage id="login.backLogin" />
              </Link>
              <LoadingButton type="submit" isLoading={isSubmitting}>
                <FormattedMessage id="login.resetPassword" />
              </LoadingButton>
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export { ResetPasswordConfirmPage };
