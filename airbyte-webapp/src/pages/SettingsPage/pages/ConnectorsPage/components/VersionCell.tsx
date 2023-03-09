import { Field, FieldProps, Form, Formik } from "formik";
import React from "react";
import { FormattedMessage, useIntl } from "react-intl";

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
}

const VersionCell: React.FC<VersionCellProps> = ({ id, version, onChange, currentVersion }) => {
  const { updatingAll, updatingDefinitionId, feedbackList } = useUpdatingState();
  const feedback = feedbackList[id];
  const updatingCurrent = id === updatingDefinitionId;
  const { formatMessage } = useIntl();

  const renderFeedback = (dirty: boolean, feedback?: string) => {
    if (feedback === "success" && !dirty) {
      return <FormattedMessage id="form.savedChange" />;
    }
    if (feedback && feedback !== "success") {
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
                <div
                  className={styles.inputField}
                  data-before={
                    feedback !== "success"
                      ? formatMessage({
                          id: "admin.latestNote",
                        })
                      : undefined
                  }
                >
                  <Input {...field} className={styles.versionInput} type="text" autoComplete="off" />
                </div>
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
