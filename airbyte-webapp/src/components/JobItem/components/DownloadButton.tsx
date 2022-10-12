import { faFileDownload } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import { useIntl } from "react-intl";

import { Button } from "components/ui/Button";

import { JobDebugInfoRead } from "core/request/AirbyteClient";
import { useCurrentWorkspaceId, useGetWorkspace } from "services/workspaces/WorkspacesService";
import { downloadFile, fileizeString } from "utils/file";

interface DownloadButtonProps {
  jobDebugInfo: JobDebugInfoRead;
  fileName: string;
}

const DownloadButton: React.FC<DownloadButtonProps> = ({ jobDebugInfo, fileName }) => {
  const { formatMessage } = useIntl();
  const { name } = useGetWorkspace(useCurrentWorkspaceId());

  const downloadFileWithLogs = () => {
    const file = new Blob([jobDebugInfo.attempts.flatMap((info) => info.logs.logLines).join("\n")], {
      type: "text/plain;charset=utf-8",
    });
    downloadFile(file, fileizeString(`${name}-${fileName}.txt`));
  };

  return (
    <Button
      onClick={downloadFileWithLogs}
      variant="secondary"
      title={formatMessage({
        id: "sources.downloadLogs",
      })}
      icon={<FontAwesomeIcon icon={faFileDownload} />}
    />
  );
};

export default DownloadButton;
