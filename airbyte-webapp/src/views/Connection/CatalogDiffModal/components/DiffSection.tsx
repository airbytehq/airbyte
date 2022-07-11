import classnames from "classnames";

import { StreamTransform } from "core/request/AirbyteClient";

import { DiffAccordion } from "./DiffAccordion";
import { DiffHeader, DiffType, DiffVerb } from "./DiffHeader";
import styles from "./DiffSection.module.scss";
import { StreamRow } from "./StreamRow";

interface DiffSectionProps {
  streams: StreamTransform[];
}

export const DiffSection: React.FC<DiffSectionProps> = ({ streams }) => {
  const diffVerb: DiffVerb = streams[0].transformType.includes("add")
    ? "new"
    : streams[0].transformType.includes("remove")
    ? "removed"
    : "changed";

  const diffType: DiffType = streams[0].transformType.includes("stream") ? "stream" : "field";

  const subheaderStyles = classnames(styles.sectionSubHeader, {
    [styles.padLeft]: streams[0].transformType === "update_stream",
  });

  if (!diffVerb || !diffType) {
    return null;
  }

  return (
    <div className={styles.sectionContainer}>
      <div className={styles.sectionHeader}>
        <DiffHeader diffCount={streams.length} diffVerb={diffVerb} diffType={diffType} />
      </div>
      <table>
        <thead className={subheaderStyles}>
          <tr>
            <th>Namespace</th>
            <th>Stream name</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {streams.map((stream) => {
            return stream.transformType === "update_stream" ? (
              <DiffAccordion
                key={`${stream.streamDescriptor.namespace}.${stream.streamDescriptor.name}`}
                data={stream}
              />
            ) : (
              <StreamRow stream={stream} key={`${stream.streamDescriptor.namespace}.${stream.streamDescriptor.name}`} />
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
