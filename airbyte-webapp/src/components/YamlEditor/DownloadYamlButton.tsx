import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";

import { downloadFile } from "utils/file";

interface DownloadYamlButtonProps {
  yaml: string;
  className?: string;
}

export const DownloadYamlButton: React.FC<DownloadYamlButtonProps> = ({ yaml, className }) => {
  const downloadYaml = () => {
    const file = new Blob([yaml], { type: "text/plain;charset=utf-8" });
    // TODO: pull name from connector name input or generate from yaml contents
    downloadFile(file, "connector_builder.yaml");
  };

  return (
    <Button className={className} onClick={downloadYaml}>
      <FormattedMessage id="connectorBuilder.downloadYaml" />
    </Button>
  );
};
