import { FormattedMessage } from "react-intl";

export const createFormErrorMessage = (error: { status?: number; message?: string }): JSX.Element | string | null => {
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
