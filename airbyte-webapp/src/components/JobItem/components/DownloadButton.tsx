import { faFileDownload } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { useIntl } from "react-intl";

import { Button } from "components";

type IProps = {
  logs: string[];
  fileName: string;
};

const DownloadButton: React.FC<IProps> = ({ logs, fileName }) => {
  const formatMessage = useIntl().formatMessage;

  const downloadFileWithLogs = () => {
    const element = document.createElement("a");
    const file = new Blob([logs.join("\n")], {
      type: "text/plain;charset=utf-8",
    });
    element.href = URL.createObjectURL(file);
    element.download = `${fileName}.txt`;
    document.body.appendChild(element); // Required for this to work in FireFox
    element.click();
    document.body.removeChild(element);
  };

  return (
    <Button
      onClick={downloadFileWithLogs}
      secondary
      title={formatMessage({
        id: "sources.downloadLogs",
      })}
    >
      <FontAwesomeIcon icon={faFileDownload} />
    </Button>
  );
};

export default DownloadButton;
