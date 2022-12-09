import { faDownload, faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Tooltip } from "components/ui/Tooltip";

import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { downloadFile } from "utils/file";

import { useBuilderErrors } from "../useBuilderErrors";
import styles from "./DownloadYamlButton.module.scss";

interface DownloadYamlButtonProps {
  className?: string;
  yaml: string;
  yamlIsValid: boolean;
}

export const DownloadYamlButton: React.FC<DownloadYamlButtonProps> = ({ className, yaml, yamlIsValid }) => {
  const { editorView } = useConnectorBuilderState();
  const { hasErrors, validateAndTouch } = useBuilderErrors();

  const downloadYaml = () => {
    const file = new Blob([yaml], { type: "text/plain;charset=utf-8" });
    // TODO: pull name from connector name input or generate from yaml contents
    downloadFile(file, "connector_builder.yaml");
  };

  const handleClick = () => {
    if (editorView === "yaml") {
      downloadYaml();
      return;
    }

    validateAndTouch(downloadYaml);
  };

  let buttonDisabled = false;
  let tooltipContent = null;

  if (editorView === "yaml" && !yamlIsValid) {
    buttonDisabled = true;
    tooltipContent = <FormattedMessage id="connectorBuilder.invalidYamlDownload" />;
  }

  if (editorView === "ui" && hasErrors()) {
    buttonDisabled = true;
    tooltipContent = <FormattedMessage id="connectorBuilder.configErrorsDownload" />;
  }

  const downloadButton = (
    <Button
      className={styles.button}
      onClick={handleClick}
      disabled={buttonDisabled}
      icon={buttonDisabled ? <FontAwesomeIcon icon={faWarning} /> : <FontAwesomeIcon icon={faDownload} />}
    >
      <FormattedMessage id="connectorBuilder.downloadYaml" />
    </Button>
  );

  return (
    <div className={className}>
      {buttonDisabled ? (
        <Tooltip control={downloadButton} placement="left">
          {tooltipContent}
        </Tooltip>
      ) : (
        downloadButton
      )}
    </div>
  );
};
