import { FormattedMessage, useIntl } from "react-intl";

import { StreamTransform } from "core/request/AirbyteClient";

import { DiffAccordion } from "./DiffAccordion";
import { DiffHeader } from "./DiffHeader";
import styles from "./FieldSection.module.scss";
import { DiffVerb } from "./types";

interface FieldSectionProps {
  streams: StreamTransform[];
  diffVerb: DiffVerb;
}

export const FieldSection: React.FC<FieldSectionProps> = ({ streams, diffVerb }) => {
  const { formatMessage } = useIntl();
  return (
    <div className={styles.sectionContainer}>
      <div className={styles.fieldHeader}>
        <DiffHeader diffCount={streams.length} diffVerb={diffVerb} diffType="stream" />
      </div>
      <div className={styles.fieldSubHeader}>
        <div id={formatMessage({ id: "connection.updateSchema.namespace" })}>
          <FormattedMessage id="connection.updateSchema.namespace" />
        </div>
        <div id={formatMessage({ id: "connection.updateSchema.streamName" })}>
          <FormattedMessage id="connection.updateSchema.streamName" />
        </div>
        <div />
      </div>
      <div className={styles.fieldRowsContainer}>
        {streams.length > 0 && (
          <ul
            aria-label={formatMessage(
              { id: "connection.updateSchema.changed" },
              {
                value: streams.length,
                item: formatMessage({ id: "connection.updateSchema.stream" }, { count: streams.length }),
              }
            )}
          >
            {streams.map((stream) => {
              return (
                <li key={`${stream.streamDescriptor.namespace}.${stream.streamDescriptor.name}`}>
                  <DiffAccordion streamTransform={stream} />
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
};
