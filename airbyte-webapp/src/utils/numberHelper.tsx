import { FormattedMessage } from "react-intl";

export const formatBytes = (bytes?: number) => {
  if (bytes && bytes < 0) {
    bytes = 0;
  }

  if (!bytes) {
    return <FormattedMessage id="sources.countBytes" values={{ count: bytes || 0 }} />;
  }

  const k = 1024;
  const dm = 2;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  const result = parseFloat((bytes / Math.pow(k, i)).toFixed(dm));

  return <FormattedMessage id={`sources.count${sizes[i]}`} values={{ count: result }} />;
};
