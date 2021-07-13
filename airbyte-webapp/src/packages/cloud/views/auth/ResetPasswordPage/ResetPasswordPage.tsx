import React from "react";
import { Formik, FieldProps, Field } from "formik";
import * as yup from "yup";
import { FormattedMessage, useIntl } from "react-intl";

import { Form, FieldItem, BottomBlock } from "../components/FormComponents";
import LabeledInput from "components/LabeledInput";
import { Button } from "components/base";
import { Link } from "components/Link";
import { H1 } from "../../../components/Titles";

const ResetPasswordPageValidationSchema = yup.object().shape({
  email: yup.string().email("form.email.error").required("form.empty.error"),
});

const ResetPasswordPage: React.FC = () => {
  const formatMessage = useIntl().formatMessage;

  return (
    <div>
      <H1 bold danger>
        Reset your password
      </H1>

      <Formik
        initialValues={{
          email: "",
        }}
        validationSchema={ResetPasswordPageValidationSchema}
        onSubmit={() => console.log("ok")}
        validateOnBlur={true}
        validateOnChange={false}
      >
        {() => (
          <Form>
            <FieldItem>
              <Field name="email">
                {({ field, meta }: FieldProps<string>) => (
                  <LabeledInput
                    {...field}
                    label={<FormattedMessage id="form.yourEmail" />}
                    placeholder={formatMessage({
                      id: "form.email.placeholder",
                    })}
                    type="text"
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
              <>
                <Link to={"/login"} $light>
                  Back to Log in
                </Link>
                <Button type="submit">Reset your password</Button>
              </>
            </BottomBlock>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default ResetPasswordPage;
