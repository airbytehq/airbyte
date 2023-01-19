import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";
import styled from "styled-components";

import { Button } from "components/ui/Button";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { Input } from "components/ui/Input";

import { DEV_IMAGE_TAG } from "core/domain/connector/constants";

import { useUpdatingState } from "./ConnectorsViewContext";
import styles from "./VersionCell.module.scss";

interface VersionCellProps {
  version: string;
  currentVersion: string;
  id: string;
  onChange: ({ version, id }: { version: string; id: string }) => void;
  feedback?: "success" | string;
}

const VersionInput = styled(Input)`
  max-width: 145px;
  margin-right: 19px;
`;

const InputField = styled.div<{ showNote?: boolean }>`
  display: inline-block;
  position: relative;
  background: ${({ theme }) => theme.whiteColor};

  &:before {
    position: absolute;
    display: ${({ showNote }) => (showNote ? "block" : "none")};
    content: attr(data-before);
    color: ${({ theme }) => theme.greyColor40};
    top: 10px;
    right: 22px;
    z-index: 3;
  }

  &:focus-within:before {
    display: none;
  }
`;

const VersionCell: React.FC<VersionCellProps> = ({ id, version, onChange, feedback, currentVersion }) => {
  const { updatingAll, updatingDefinitionId } = useUpdatingState();
  const updatingCurrent = id === updatingDefinitionId;
  const { formatMessage } = useIntl();

  const renderFeedback = (dirty: boolean, feedback?: string) => {
    if (feedback && !dirty) {
      if (feedback === "success") {
        return <FormattedMessage id="form.savedChange" />;
      }
      return <span className={styles.errorMessage}>{feedback}</span>;
    }

    return null;
  };

  const isConnectorUpdatable = currentVersion !== version || currentVersion === DEV_IMAGE_TAG;

  return (
    <Formik
      initialValues={{
        version,
      }}
      onSubmit={(values) => onChange({ id, version: values.version })}
    >
      {({ isSubmitting, dirty }) => (
        <Form>
          <FlexContainer justifyContent="flex-end" alignItems="center" className={styles.versionCell}>
            <FlexItem>{renderFeedback(dirty, feedback)}</FlexItem>
            <Field name="version">
              {({ field }: FieldProps<string>) => (
                <InputField
                  showNote={version === field.value}
                  data-before={formatMessage({
                    id: "admin.latestNote",
                  })}
                >
                  <VersionInput {...field} type="text" autoComplete="off" />
                </InputField>
              )}
            </Field>
            <Button
              size="xs"
              isLoading={(updatingAll && isConnectorUpdatable) || updatingCurrent}
              type="submit"
              disabled={(isSubmitting || !dirty) && !isConnectorUpdatable}
            >
              <FormattedMessage id="form.change" />
            </Button>
          </FlexContainer>
        </Form>
      )}
    </Formik>
  );
};

export default VersionCell;
