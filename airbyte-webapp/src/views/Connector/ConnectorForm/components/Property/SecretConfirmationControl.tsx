import { useField, useFormikContext } from "formik";
import React, { useEffect, useRef, useState } from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Input } from "components/ui/Input";
import { SecretTextArea } from "components/ui/SecretTextArea";

import styles from "./SecretConfirmationControl.module.scss";

interface SecretConfirmationControlProps {
  showButtons?: boolean;
  name: string;
  multiline: boolean;
  disabled?: boolean;
  error?: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
}

const SecretConfirmationControl: React.FC<SecretConfirmationControlProps> = ({
  showButtons,
  disabled,
  multiline,
  name,
  error,
  onChange,
}) => {
  const [field, , helpers] = useField(name);
  const [previousValue, setPreviousValue] = useState<unknown>(undefined);
  const isEditInProgress = Boolean(previousValue);
  const controlRef = useRef<HTMLInputElement>(null);

  const { dirty, touched } = useFormikContext();

  const component =
    multiline && (isEditInProgress || !showButtons) ? (
      <SecretTextArea
        {...field}
        onChange={onChange}
        autoComplete="off"
        value={field.value ?? ""}
        rows={3}
        error={error}
        // eslint-disable-next-line jsx-a11y/no-autofocus
        autoFocus={showButtons && isEditInProgress}
        disabled={(showButtons && !isEditInProgress) || disabled}
      />
    ) : (
      <Input
        {...field}
        onChange={onChange}
        autoComplete="off"
        value={field.value ?? ""}
        type="password"
        error={error}
        ref={controlRef}
        disabled={(showButtons && !isEditInProgress) || disabled}
      />
    );

  useEffect(() => {
    if (!dirty && !touched && previousValue) {
      setPreviousValue(undefined);
    }
  }, [dirty, helpers, previousValue, touched]);

  if (!showButtons) {
    return <>{component}</>;
  }

  const handleStartEdit = () => {
    if (controlRef && controlRef.current) {
      controlRef.current?.removeAttribute?.("disabled");
      controlRef.current?.focus?.();
    }
    setPreviousValue(field.value);
    helpers.setValue("");
  };

  const onDone = () => {
    setPreviousValue(undefined);
  };

  const onCancel = () => {
    if (previousValue) {
      helpers.setValue(previousValue);
    }
    setPreviousValue(undefined);
  };

  return (
    <div className={styles.container}>
      {component}
      {isEditInProgress ? (
        <>
          <Button size="sm" onClick={onCancel} type="button" variant="secondary" disabled={disabled}>
            <FormattedMessage id="form.cancel" />
          </Button>
          <Button size="sm" onClick={onDone} type="button" disabled={disabled}>
            <FormattedMessage id="form.done" />
          </Button>
        </>
      ) : (
        <Button size="sm" onClick={handleStartEdit} type="button" variant="secondary" disabled={disabled}>
          <FormattedMessage id="form.edit" />
        </Button>
      )}
    </div>
  );
};

export default SecretConfirmationControl;
