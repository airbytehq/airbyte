import { FormattedMessage } from "react-intl";

import { AirbyteCatalog, StreamTransform } from "core/request/AirbyteClient";

import { DiffVerb } from "../CatalogDiffModal";
import { DiffHeader } from "./DiffHeader";
import styles from "./DiffSection.module.scss";
import { StreamRow } from "./StreamRow";

interface DiffSectionProps {
  streams: StreamTransform[];
  catalog?: AirbyteCatalog;
  diffVerb: DiffVerb;
}

export const DiffSection: React.FC<DiffSectionProps> = ({ streams, catalog, diffVerb }) => {
  return (
    <div className={styles.sectionContainer}>
      <div className={styles.sectionHeader}>
        <DiffHeader diffCount={streams.length} diffVerb={diffVerb} diffType="stream" />
      </div>
      <table>
        <thead className={styles.sectionSubHeader}>
          <tr>
            <th>
              <FormattedMessage id="connection.updateSchema.namespace" />
            </th>
            <th>
              <FormattedMessage id="connection.updateSchema.name" />
            </th>
            <th />
          </tr>
        </thead>
        <tbody>
          {streams.map((stream) => {
            let syncModeString;

            if (catalog) {
              const streamConfig = catalog.streams.find(
                (catalogStream) =>
                  catalogStream.stream?.namespace === stream.streamDescriptor.namespace &&
                  catalogStream.stream?.name === stream.streamDescriptor.name
              )?.config;

              streamConfig?.syncMode &&
                streamConfig.destinationSyncMode &&
                (syncModeString = `${streamConfig?.syncMode} | ${streamConfig?.destinationSyncMode}`);
            }

            return (
              <StreamRow
                streamTransform={stream}
                syncMode={syncModeString}
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
