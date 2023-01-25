import { faDownload, faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Tooltip } from "components/ui/Tooltip";

import { useConnectorBuilderFormState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { downloadFile } from "utils/file";

import styles from "./DownloadYamlButton.module.scss";
import { useBuilderErrors } from "./useBuilderErrors";

interface DownloadYamlButtonProps {
  className?: string;
  yaml: string;
  yamlIsValid: boolean;
}

export const DownloadYamlButton: React.FC<DownloadYamlButtonProps> = ({ className, yaml, yamlIsValid }) => {
  const { editorView } = useConnectorBuilderFormState();
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
  let showWarningIcon = false;
  let tooltipContent = undefined;

  if (editorView === "yaml" && !yamlIsValid) {
    buttonDisabled = true;
    showWarningIcon = true;
    tooltipContent = <FormattedMessage id="connectorBuilder.invalidYamlDownload" />;
  }

  if (editorView === "ui" && hasErrors(true)) {
    showWarningIcon = true;
    tooltipContent = <FormattedMessage id="connectorBuilder.configErrorsDownload" />;
  }

  const downloadButton = (
    <Button
      full
      onClick={handleClick}
      disabled={buttonDisabled}
      icon={showWarningIcon ? <FontAwesomeIcon icon={faWarning} /> : <FontAwesomeIcon icon={faDownload} />}
    >
      <FormattedMessage id="connectorBuilder.downloadYaml" />
    </Button>
  );

  return (
    <div className={className}>
      {tooltipContent !== undefined ? (
        <Tooltip
          control={downloadButton}
          placement={editorView === "yaml" ? "left" : "top"}
          containerClassName={styles.tooltipContainer}
        >
          {tooltipContent}
        </Tooltip>
      ) : (
        downloadButton
      )}
    </div>
  );
};
