import { useField, useFormikContext } from "formik";
import React, { useEffect, useRef, useState } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components/ui/Button";
import { Input } from "components/ui/Input";
import { SecretTextArea } from "components/ui/SecretTextArea";

const ComponentContainer = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

interface SecretConfirmationControlProps {
  showButtons?: boolean;
  name: string;
  multiline: boolean;
  disabled?: boolean;
  error?: boolean;
}

const SecretConfirmationControl: React.FC<SecretConfirmationControlProps> = ({
  showButtons,
  disabled,
  multiline,
  name,
  error,
}) => {
  const [field, , helpers] = useField(name);
  const [previousValue, setPreviousValue] = useState<unknown>(undefined);
  const isEditInProgress = Boolean(previousValue);
  const controlRef = useRef<HTMLElement>(null);

  const { dirty, touched } = useFormikContext();

  const component =
    multiline && (isEditInProgress || !showButtons) ? (
      <SecretTextArea
        {...field}
        autoComplete="off"
        value={field.value ?? ""}
        rows={3}
        disabled={disabled}
        error={error}
      />
    ) : (
      <Input
        {...field}
        autoComplete="off"
        value={field.value ?? ""}
        type="password"
        disabled={disabled}
        error={error}
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
    <ComponentContainer>
      {React.cloneElement(component, {
        ref: controlRef,
        autoFocus: isEditInProgress,
        disabled: !isEditInProgress || disabled,
      })}
      {isEditInProgress ? (
        <>
          <Button size="xs" onClick={onDone} type="button" disabled={disabled}>
            <FormattedMessage id="form.done" />
          </Button>
          <Button size="xs" onClick={onCancel} type="button" variant="secondary" disabled={disabled}>
            <FormattedMessage id="form.cancel" />
          </Button>
        </>
      ) : (
        <Button size="xs" onClick={handleStartEdit} type="button" disabled={disabled}>
          <FormattedMessage id="form.edit" />
        </Button>
      )}
    </ComponentContainer>
  );
};

export default SecretConfirmationControl;
