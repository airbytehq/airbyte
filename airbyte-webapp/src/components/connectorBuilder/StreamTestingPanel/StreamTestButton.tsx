import { faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import flatten from "flat";
import { useFormikContext } from "formik";
import { FormattedMessage } from "react-intl";

import { RotateIcon } from "components/icons/RotateIcon";
import { Button } from "components/ui/Button";
import { Text } from "components/ui/Text";
import { Tooltip } from "components/ui/Tooltip";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";

import { BuilderFormValues } from "../Builder/types";
import styles from "./StreamTestButton.module.scss";

interface StreamTestButtonProps {
  selectedStreamName: string;
  readStream: () => void;
}

export const StreamTestButton: React.FC<StreamTestButtonProps> = ({ selectedStreamName, readStream }) => {
  const { editorView, yamlIsValid } = useConnectorBuilderState();
  const { values, errors, setFieldTouched } = useFormikContext<BuilderFormValues>();

  const selectedStreamNum = values.streams.findIndex((stream) => stream.name === selectedStreamName);

  let buttonDisabled = false;
  let tooltipContent = null;

  if (editorView === "yaml" && !yamlIsValid) {
    buttonDisabled = true;
    tooltipContent = <FormattedMessage id="connectorBuilder.invalidYamlTest" />;
  }

  const formErrorKeys = Object.keys(errors);
  if (editorView === "ui" && formErrorKeys.length > 0) {
    buttonDisabled = true;
    tooltipContent = <FormattedMessage id="connectorBuilder.configErrorsTest" />;
  }

  const handleClick = () => {
    if (editorView === "yaml") {
      readStream();
      return;
    }

    const pathsToTouch = Object.keys(flatten(values.global)).map((path) => `global.${path}`);
    if (selectedStreamNum >= 0) {
      pathsToTouch.push(
        ...Object.keys(flatten(values.streams[selectedStreamNum])).map(
          (path) => `streams[${selectedStreamNum}].${path}`
        )
      );
    }
    console.log("pathsToTouch", pathsToTouch);

    for (const path of pathsToTouch) {
      setFieldTouched(path);
    }

    console.log("errors", errors);
  };

  const testButton = (
    <Button
      className={styles.testButton}
      size="sm"
      onClick={handleClick}
      disabled={buttonDisabled}
      icon={
        !buttonDisabled ? (
          <div>
            <RotateIcon width={styles.testIconHeight} height={styles.testIconHeight} />
          </div>
        ) : (
          <FontAwesomeIcon icon={faWarning} />
        )
      }
    >
      <Text className={styles.testButtonText} size="sm" bold>
        <FormattedMessage id="connectorBuilder.testButton" />
      </Text>
    </Button>
  );

  return !buttonDisabled ? (
    testButton
  ) : (
    <Tooltip control={testButton} containerClassName={styles.testButtonTooltipContainer}>
      {tooltipContent}
    </Tooltip>
  );
};
