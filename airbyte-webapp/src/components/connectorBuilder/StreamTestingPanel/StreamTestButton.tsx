import { faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useFormikContext } from "formik";
import { FormattedMessage } from "react-intl";

import { RotateIcon } from "components/icons/RotateIcon";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderFormValues } from "../types";
import { useBuilderErrors } from "../useBuilderErrors";
import styles from "./StreamTestButton.module.scss";

interface StreamTestButtonProps {
  selectedStreamName: string;
  readStream: () => void;
}

export const StreamTestButton: React.FC<StreamTestButtonProps> = ({ selectedStreamName, readStream }) => {
  const { editorView, yamlIsValid } = useConnectorBuilderState();
  const { values } = useFormikContext<BuilderFormValues>();
  const { hasErrors, validateAndTouch } = useBuilderErrors();

  const selectedStreamNum = values.streams.findIndex((stream) => stream.name === selectedStreamName);

  const handleClick = () => {
    if (editorView === "yaml") {
      readStream();
      return;
    }

    validateAndTouch(readStream, selectedStreamNum);
  };

  let buttonDisabled = false;
  let tooltipContent = null;

  if (editorView === "yaml" && !yamlIsValid) {
    buttonDisabled = true;
    tooltipContent = <FormattedMessage id="connectorBuilder.invalidYamlTest" />;
  }

  if (editorView === "ui" && hasErrors(selectedStreamNum)) {
    buttonDisabled = true;
    tooltipContent = <FormattedMessage id="connectorBuilder.configErrorsTest" />;
  }

  const testButton = (
    <Button
      className={styles.testButton}
      size="sm"
      onClick={handleClick}
      disabled={buttonDisabled}
      icon={
        buttonDisabled ? (
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

  return buttonDisabled ? (
    <Tooltip control={testButton} containerClassName={styles.testButtonTooltipContainer}>
      {tooltipContent}
    </Tooltip>
  ) : (
    testButton
  );
};
