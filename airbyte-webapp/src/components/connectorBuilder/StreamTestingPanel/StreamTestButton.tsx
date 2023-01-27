import { faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage } from "react-intl";

import { RotateIcon } from "components/icons/RotateIcon";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";

import styles from "./StreamTestButton.module.scss";
import { useBuilderErrors } from "../useBuilderErrors";

interface StreamTestButtonProps {
  readStream: () => void;
  hasTestInputJsonErrors: boolean;
  setTestInputOpen: (open: boolean) => void;
}

export const StreamTestButton: React.FC<StreamTestButtonProps> = ({
  readStream,
  hasTestInputJsonErrors,
  setTestInputOpen,
}) => {
  const { editorView, yamlIsValid } = useConnectorBuilderFormState();
  const { hasErrors, validateAndTouch } = useBuilderErrors();

  const handleClick = () => {
    if (hasTestInputJsonErrors) {
      setTestInputOpen(true);
      return;
    }
    if (editorView === "yaml") {
      readStream();
      return;
    }

    validateAndTouch(readStream);
  };

  let buttonDisabled = false;
  let showWarningIcon = false;
  let tooltipContent = undefined;

  if (editorView === "yaml" && !yamlIsValid) {
    buttonDisabled = true;
    showWarningIcon = true;
    tooltipContent = <FormattedMessage id="connectorBuilder.invalidYamlTest" />;
  }

  if ((editorView === "ui" && hasErrors(false)) || hasTestInputJsonErrors) {
    showWarningIcon = true;
    tooltipContent = <FormattedMessage id="connectorBuilder.configErrorsTest" />;
  }

  const testButton = (
    <Button
      className={styles.testButton}
      size="sm"
      onClick={handleClick}
      disabled={buttonDisabled}
      data-testid="read-stream"
      icon={
        showWarningIcon ? (
          <FontAwesomeIcon icon={faWarning} />
        ) : (
          <div>
            <RotateIcon width={styles.testIconHeight} height={styles.testIconHeight} />
          </div>
        )
      }
    >
      <Text className={styles.testButtonText} size="sm" bold>
        <FormattedMessage id="connectorBuilder.testButton" />
      </Text>
    </Button>
  );

  return tooltipContent !== undefined ? (
    <Tooltip control={testButton} containerClassName={styles.testButtonTooltipContainer}>
      {tooltipContent}
    </Tooltip>
  ) : (
    testButton
  );
};
