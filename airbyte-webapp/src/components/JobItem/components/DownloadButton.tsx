import { faFileDownload } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { useIntl } from "react-intl";

import { Button } from "components";

import { JobDebugInfoRead } from "core/request/AirbyteClient";

import { ButtonType } from "../../base/Button/types";

interface DownloadButtonProps {
  jobDebugInfo: JobDebugInfoRead;
  fileName: string;
}

const DownloadButton: React.FC<DownloadButtonProps> = ({ jobDebugInfo, fileName }) => {
  const { formatMessage } = useIntl();

  const downloadFileWithLogs = () => {
    const element = document.createElement("a");
    const file = new Blob([jobDebugInfo.attempts.flatMap((info) => info.logs.logLines).join("\n")], {
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
      buttonType={ButtonType.Secondary}
      title={formatMessage({
        id: "sources.downloadLogs",
      })}
      icon={<FontAwesomeIcon icon={faFileDownload} />}
    />
  );
};

export default DownloadButton;
