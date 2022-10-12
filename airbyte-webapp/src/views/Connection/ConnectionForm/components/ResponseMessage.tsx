import classnames from "classnames";

import { Text } from "components/ui/Text";

import styles from "./ResponseMessage.module.scss";

interface ResponseMessageProps {
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  dirty: boolean;
}
export const ResponseMessage: React.FC<ResponseMessageProps> = ({ successMessage, errorMessage, dirty }) => {
  const messageStyle = classnames(styles.message, {
    [styles.success]: successMessage,
    [styles.error]: errorMessage,
  });
  if (errorMessage) {
    return (
      <Text as="div" size="lg" className={messageStyle}>
        {errorMessage}
      </Text>
    );
  }

  if (successMessage && !dirty) {
    return (
      <Text as="div" size="lg" className={messageStyle} data-id="success-result">
        {successMessage}
      </Text>
    );
  }
  return null;
};
