import classnames from "classnames";
import React from "react";
import { FormattedMessage } from "react-intl";

import { Button, LoadingButton } from "components";
import { Text } from "components/base/Text";

import styles from "./EditControls.module.scss";

interface EditControlProps {
  isSubmitting: boolean;
  dirty: boolean;
  submitDisabled?: boolean;
  resetForm: () => void;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  enableControls?: boolean;
  withLine?: boolean;
}

const EditControls: React.FC<EditControlProps> = ({
  isSubmitting,
  dirty,
  submitDisabled,
  resetForm,
  successMessage,
  errorMessage,
  enableControls,
  withLine,
}) => {
  const showStatusMessage = () => {
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
        <Text as="div" size="lg" className={messageStyle}>
          {successMessage}
        </Text>
      );
    }
    return null;
  };

  return (
    <>
      {withLine && <div className={styles.line} />}
      <div className={styles.content}>
        {showStatusMessage()}
        <div>
          <Button type="button" secondary disabled={isSubmitting || (!dirty && !enableControls)} onClick={resetForm}>
            <FormattedMessage id="form.cancel" />
          </Button>
          <LoadingButton
            className={styles.controlButton}
            type="submit"
            isLoading={isSubmitting}
            disabled={submitDisabled || isSubmitting || (!dirty && !enableControls)}
          >
            <FormattedMessage id="form.saveChanges" />
          </LoadingButton>
        </div>
      </div>
    </>
  );
};

export default EditControls;
