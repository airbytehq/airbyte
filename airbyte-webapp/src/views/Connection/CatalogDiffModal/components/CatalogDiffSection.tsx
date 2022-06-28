import { FormattedMessage } from "react-intl";

import { AirbyteCatalog, StreamTransform } from "core/request/AirbyteClient";

import { CatalogDiffAccordion } from "./CatalogDiffAccordion";
import styles from "./CatalogDiffSection.module.scss";
import { StreamRow } from "./StreamRow";

interface CatalogDiffSectionProps {
  data: StreamTransform[];
  catalog: AirbyteCatalog;
}

export const CatalogDiffSection: React.FC<CatalogDiffSectionProps> = ({ data, catalog }) => {
  //note: do we have to send the catalog along for a field?
  //isChild will be used to demote headings within the accordion
  console.log("section");
  const diffVerb = data[0].transformType.includes("add")
    ? "new"
    : data[0].transformType.includes("remove")
    ? "removed"
    : data[0].transformType.includes("update")
    ? "changed"
    : undefined;

  const diffType = data[0].transformType.includes("stream")
    ? "stream"
    : data[0].transformType.includes("field")
    ? "field"
    : undefined;
  return (
    <div className={styles.sectionContainer}>
      {/* header: {number} {descriptor} {object} */}
      <div className={styles.sectionHeader}>
        {data.length}{" "}
        <FormattedMessage
          id={`connection.updateSchema.${diffVerb}`}
          values={{
            item: <FormattedMessage id={`connection.updateSchema.${diffType}`} values={{ count: data.length }} />,
          }}
        />
      </div>
      {/* update stream should make an accordion, others should make a row */}
      {data.map((item) => {
        return item.transformType === "update_stream" ? (
          <CatalogDiffAccordion data={item.updateStream} catalog={catalog} />
        ) : (
          <StreamRow item={item} catalog={catalog} />
        );
      })}
    </div>
  );
};
