import classnames from "classnames";
import { FormattedMessage } from "react-intl";

import { AirbyteCatalog, StreamTransform } from "core/request/AirbyteClient";

import { CatalogDiffAccordion } from "./CatalogDiffAccordion";
import styles from "./CatalogDiffSection.module.scss";
import { StreamRow } from "./StreamRow";

interface StreamSectionProps {
  data: StreamTransform[];
  catalog: AirbyteCatalog;
}

export const CatalogDiffSection: React.FC<StreamSectionProps> = ({ data, catalog }) => {
  //note: do we have to send the catalog along for a field?
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

  console.log(data[0].transformType);

  const subheaderStyles = classnames(styles.sectionSubHeader, {
    [styles.padLeft]: data[0].transformType === "update_stream",
  });

  return (
    <div className={styles.sectionContainer}>
      <div className={styles.sectionHeader}>
        {data.length}{" "}
        <FormattedMessage
          id={`connection.updateSchema.${diffVerb}`}
          values={{
            item: <FormattedMessage id={`connection.updateSchema.${diffType}`} values={{ count: data.length }} />,
          }}
        />
      </div>
      <table>
        <tr className={subheaderStyles}>
          <th>Namespace</th>
          <th> Stream name</th>
          <th />
        </tr>
        {data.map((item) => {
          return item.transformType === "update_stream" ? (
            <CatalogDiffAccordion data={item} catalog={catalog} />
          ) : (
            <StreamRow item={item} catalog={catalog} />
          );
        })}
      </table>
    </div>
  );
};
