import { FormattedMessage, useIntl } from "react-intl";

import { StreamTransform } from "core/request/AirbyteClient";

import { DiffVerb } from "../CatalogDiffModal";
import { DiffAccordion } from "./DiffAccordion";
import { DiffHeader } from "./DiffHeader";
import styles from "./FieldSection.module.scss";

interface FieldSectionProps {
  streams: StreamTransform[];
  diffVerb: DiffVerb;
}

export const FieldSection: React.FC<FieldSectionProps> = ({ streams, diffVerb }) => {
  const { formatMessage } = useIntl();
  return (
    // eslint-disable-next-line css-modules/no-undef-class
    <div className={styles.sectionContainer}>
      {/* eslint-disable-next-line css-modules/no-undef-class */}
      <div className={styles.sectionHeader}>
        <DiffHeader diffCount={streams.length} diffVerb={diffVerb} diffType="field" />
        <div className={styles.fieldSubHeader}>
          <div id={formatMessage({ id: "connection.updateSchema.namespace" })}>
            <FormattedMessage id="connection.updateSchema.namespace" />
          </div>
          <div id={formatMessage({ id: "connection.updateSchema.name" })}>
            <FormattedMessage id="connection.updateSchema.name" />
          </div>
          <div />
        </div>
        <ul>
          {streams.map((stream) => {
            return (
              <li key={`${stream.streamDescriptor.namespace}.${stream.streamDescriptor.name}`}>
                <DiffAccordion streamTransform={stream} />
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
};
