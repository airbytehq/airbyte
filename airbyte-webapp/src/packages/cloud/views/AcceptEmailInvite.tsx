import { Formik } from "formik";
import { FormattedMessage, useIntl } from "react-intl";
import * as yup from "yup";

import HeadTitle from "components/HeadTitle";

import { FieldError } from "../lib/errors/FieldError";
import { useAuthService } from "../services/auth/AuthService";
import { EmailLinkErrorCodes } from "../services/auth/types";
import { FieldItem, Form } from "./auth/components/FormComponents";
import { FormTitle } from "./auth/components/FormTitle";
import {
  Disclaimer,
  EmailField,
  NameField,
  NewsField,
  PasswordField,
  SignupButton,
  SignupFormStatusMessage,
} from "./auth/SignupPage/components/SignupForm";

const ValidationSchema = yup.object().shape({
  name: yup.string().required("form.empty.error"),
  email: yup.string().email("form.email.error").required("form.empty.error"),
  password: yup.string().min(12, "signup.password.minLength").required("form.empty.error"),
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
        news: true,
      }}
      validationSchema={ValidationSchema}
      onSubmit={async ({ name, email, password, news }, { setFieldError, setStatus }) => {
        try {
          await authService.signUpWithEmailLink({ name, email, password, news });
        } catch (err) {
          if (err instanceof FieldError) {
            setFieldError(err.field, err.message);
          } else {
            setStatus(
              formatMessage({
                id: [EmailLinkErrorCodes.LINK_EXPIRED, EmailLinkErrorCodes.LINK_INVALID].includes(err.message)
                  ? `login.${err.message}`
                  : "errorView.unknownError",
              })
            );
          }
        }
      }}
    >
      {({ isSubmitting, status, isValid }) => (
        <Form>
          <FieldItem>
            <NameField />
          </FieldItem>
          <FieldItem>
            <EmailField label={<FormattedMessage id="login.inviteEmail" />} />
          </FieldItem>
          <FieldItem>
            <PasswordField label={<FormattedMessage id="login.createPassword" />} />
          </FieldItem>
          <FieldItem>
            <NewsField />
          </FieldItem>
          <SignupButton
            isLoading={isSubmitting}
            disabled={!isValid}
            buttonMessageId="login.activateAccess.submitButton"
          />
          {status && <SignupFormStatusMessage>{status}</SignupFormStatusMessage>}
          <Disclaimer />
        </Form>
      )}
    </Formik>
  );

  return (
    <>
      <HeadTitle titles={[{ id: "login.inviteTitle" }]} />
      <FormTitle>
        <FormattedMessage id="login.inviteTitle" />
      </FormTitle>
      {formElement}
    </>
  );
};
