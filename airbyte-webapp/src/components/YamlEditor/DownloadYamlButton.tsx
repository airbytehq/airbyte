import { faDownload, faWarning } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Tooltip } from "components/ui/Tooltip";

import { downloadFile } from "utils/file";

interface DownloadYamlButtonProps {
  className?: string;
  yaml: string;
  yamlIsValid: boolean;
}

export const DownloadYamlButton: React.FC<DownloadYamlButtonProps> = ({ className, yaml, yamlIsValid }) => {
  const downloadYaml = () => {
    const file = new Blob([yaml], { type: "text/plain;charset=utf-8" });
    // TODO: pull name from connector name input or generate from yaml contents
    downloadFile(file, "connector_builder.yaml");
  };

  const downloadButton = (
    <Button
      className={className}
      onClick={downloadYaml}
      disabled={!yamlIsValid}
      icon={yamlIsValid ? <FontAwesomeIcon icon={faDownload} /> : <FontAwesomeIcon icon={faWarning} />}
    >
      <FormattedMessage id="connectorBuilder.downloadYaml" />
    </Button>
  );

  return yamlIsValid ? (
    downloadButton
  ) : (
    <Tooltip control={downloadButton} placement="left">
      <FormattedMessage id="connectorBuilder.invalidYamlDownload" />
    </Tooltip>
  );
};
