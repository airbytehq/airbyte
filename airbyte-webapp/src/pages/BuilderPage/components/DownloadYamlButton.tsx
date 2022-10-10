import { useIntl } from "react-intl";

import { Button } from "components/ui/Button";

import { downloadFile } from "utils/file";

interface DownloadYamlButtonProps {
  yaml: string;
  className?: string;
}

export const DownloadYamlButton: React.FC<DownloadYamlButtonProps> = ({ yaml, className }) => {
  const { formatMessage } = useIntl();

  const downloadYaml = () => {
    console.log(yaml);
    const file = new Blob([yaml], { type: "text/plain;charset=utf-8" });
    downloadFile(file, "connector_builder.yaml");
  };

  return (
    <Button className={className} onClick={downloadYaml}>
      {formatMessage({ id: "builder.downloadYaml" })}
    </Button>
  );
};
