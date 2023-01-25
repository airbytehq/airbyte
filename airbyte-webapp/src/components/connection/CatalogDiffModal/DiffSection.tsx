import { FormattedMessage } from "react-intl";

import { AirbyteCatalog, StreamDescriptor, StreamTransform } from "core/request/AirbyteClient";

import { DiffHeader } from "./DiffHeader";
import styles from "./DiffSection.module.scss";
import { StreamRow } from "./StreamRow";
import { DiffVerb } from "./types";

interface DiffSectionProps {
  streams: StreamTransform[];
  catalog?: AirbyteCatalog;
  diffVerb: DiffVerb;
}

const calculateSyncModeString = (catalog: AirbyteCatalog, streamDescriptor: StreamDescriptor) => {
  const streamConfig = catalog.streams.find(
    (catalogStream) =>
      catalogStream.stream?.namespace === streamDescriptor.namespace &&
      catalogStream.stream?.name === streamDescriptor.name
  )?.config;

  if (streamConfig?.syncMode && streamConfig.destinationSyncMode) {
    return `${streamConfig?.syncMode} | ${streamConfig?.destinationSyncMode}`;
  }
  return "";
};
export const DiffSection: React.FC<DiffSectionProps> = ({ streams, catalog, diffVerb }) => {
  return (
    <div className={styles.sectionContainer}>
      <div className={styles.sectionHeader}>
        <DiffHeader diffCount={streams.length} diffVerb={diffVerb} diffType="stream" />
      </div>
      <table aria-label={`${diffVerb} streams table`} className={styles.table}>
        <thead className={styles.sectionSubHeader}>
          <tr>
            <th>
              <FormattedMessage id="connection.updateSchema.namespace" />
            </th>
            <th>
              <FormattedMessage id="connection.updateSchema.streamName" />
            </th>
            <th />
          </tr>
        </thead>
        <tbody>
          {streams.map((stream) => {
            return (
              <StreamRow
                streamTransform={stream}
                syncMode={!catalog ? undefined : calculateSyncModeString(catalog, stream.streamDescriptor)}
                diffVerb={diffVerb}
                key={`${stream.streamDescriptor.namespace}.${stream.streamDescriptor.name}`}
              />
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
