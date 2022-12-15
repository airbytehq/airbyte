import { FormattedMessage } from "react-intl";

export class FormError extends Error {
  status?: number;
}

export const generateMessageFromError = (error: FormError): JSX.Element | string | null => {
  if (error.message) {
    return error.message;
  }

  if (!error.status || error.status === 0) {
    return null;
  }

  return error.status === 400 ? (
    <FormattedMessage id="form.validationError" />
  ) : (
    <FormattedMessage id="form.someError" />
  );
};
