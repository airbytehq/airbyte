import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";

import styles from "./EditControls.module.scss";
import { ResponseMessage } from "./ResponseMessage";

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
  return (
    <>
      {withLine && <div className={styles.line} />}
      <div className={styles.content}>
        <ResponseMessage dirty={dirty} successMessage={successMessage} errorMessage={errorMessage} />
        <div className={styles.buttonsContainer}>
          <Button
            type="button"
            variant="secondary"
            disabled={isSubmitting || (!dirty && !enableControls)}
            onClick={resetForm}
          >
            <FormattedMessage id="form.cancel" />
          </Button>
          <Button
            className={styles.controlButton}
            type="submit"
            isLoading={isSubmitting}
            disabled={submitDisabled || isSubmitting || (!dirty && !enableControls)}
          >
            <FormattedMessage id="form.saveChanges" />
          </Button>
        </div>
      </div>
    </>
  );
};

export default EditControls;
