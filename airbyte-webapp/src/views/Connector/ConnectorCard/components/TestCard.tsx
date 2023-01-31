import { faChevronDown, faChevronRight, faClose, faRefresh } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
import { FormattedMessage } from "react-intl";

import { JobLogs } from "components/JobItem/components/JobLogs";
import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";
import { FlexContainer, FlexItem } from "components/ui/Flex";
import { ProgressBar } from "components/ui/ProgressBar";
import { Text } from "components/ui/Text";

import { SynchronousJobRead } from "core/request/AirbyteClient";

import styles from "./TestCard.module.scss";
import TestingConnectionSuccess from "./TestingConnectionSuccess";
import { TestingConnectionError } from "../../ConnectorForm/components/TestingConnectionError";

interface IProps {
  formType: "source" | "destination";
  isValid: boolean;
  onRetestClick: () => void;
  onCancelTesting: () => void;
  isTestConnectionInProgress?: boolean;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  job?: SynchronousJobRead;
  isEditMode?: boolean;
  dirty: boolean;
  connectionTestSuccess: boolean;
}

const PROGRESS_BAR_TIME = 60 * 2;

export const TestCard: React.FC<IProps> = ({
  isTestConnectionInProgress,
  isValid,
  formType,
  onRetestClick,
  connectionTestSuccess,
  errorMessage,
  onCancelTesting,
  job,
  isEditMode,
  dirty,
}) => {
  const [logsVisible, setLogsVisible] = useState(false);

  const renderStatusMessage = () => {
    if (errorMessage) {
      return (
        <FlexContainer direction="column">
          <TestingConnectionError errorMessage={errorMessage} />
          {job && (
            <div>
              <Button
                variant="clear"
                type="button"
                icon={<FontAwesomeIcon icon={logsVisible ? faChevronDown : faChevronRight} />}
                onClick={() => {
                  setLogsVisible(!logsVisible);
                }}
              >
                <FormattedMessage id="connector.testLogs" />
              </Button>
              {logsVisible && <JobLogs job={job} jobIsFailed />}
            </div>
          )}
        </FlexContainer>
      );
    }
    if (connectionTestSuccess) {
      return <TestingConnectionSuccess />;
    }
    return null;
  };

  return (
    <Card className={styles.cardTest}>
      <FlexContainer direction="column">
        <FlexContainer alignItems="center">
          <FlexItem grow>
            <Text size="lg">
              <FormattedMessage id={`form.${formType}RetestTitle`} />
            </Text>
          </FlexItem>
          {isTestConnectionInProgress ? (
            <Button
              className={styles.button}
              icon={<FontAwesomeIcon icon={faClose} />}
              variant="secondary"
              type="button"
              onClick={() => onCancelTesting?.()}
            >
              <FormattedMessage id="form.cancel" />
            </Button>
          ) : (
            <Button
              type="button"
              onClick={onRetestClick}
              variant="secondary"
              icon={<FontAwesomeIcon icon={faRefresh} />}
              // disable if there are changes in edit mode because the retest API can currently only test the saved state
              disabled={!isValid || (isEditMode && dirty)}
            >
              <FormattedMessage id={!isEditMode ? "form.test" : `form.${formType}Retest`} />
            </Button>
          )}
        </FlexContainer>
        {isTestConnectionInProgress ? (
          <FlexContainer justifyContent="center">
            <ProgressBar runTime={PROGRESS_BAR_TIME} />
          </FlexContainer>
        ) : (
          renderStatusMessage()
        )}
      </FlexContainer>
    </Card>
  );
};
