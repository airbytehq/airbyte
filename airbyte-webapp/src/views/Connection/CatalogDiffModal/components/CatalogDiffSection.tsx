import classnames from "classnames";

import { AirbyteCatalog, StreamTransform } from "core/request/AirbyteClient";

import { CatalogDiffAccordion } from "./CatalogDiffAccordion";
import styles from "./CatalogDiffSection.module.scss";
import { DiffHeader, DiffType, DiffVerb } from "./DiffHeader";
import { StreamRow } from "./StreamRow";

interface StreamSectionProps {
  data: StreamTransform[];
  catalog: AirbyteCatalog;
}

export const CatalogDiffSection: React.FC<StreamSectionProps> = ({ data, catalog }) => {
  //note: do we have to send the catalog along for a field?
  const diffVerb: DiffVerb = data[0].transformType.includes("add")
    ? "new"
    : data[0].transformType.includes("remove")
    ? "removed"
    : "changed";

  const diffType: DiffType = data[0].transformType.includes("stream") ? "stream" : "field";

  const subheaderStyles = classnames(styles.sectionSubHeader, {
    [styles.padLeft]: data[0].transformType === "update_stream",
  });

  console.log(subheaderStyles);

  if (!diffVerb || !diffType) {
    return null;
  }

  return (
    <div className={styles.sectionContainer}>
      <div className={styles.sectionHeader}>
        <DiffHeader diffCount={data.length} diffVerb={diffVerb} diffType={diffType} />
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
          {data.map((item) => {
            return item.transformType === "update_stream" ? (
              <tr key={`${item.streamDescriptor.namespace}.${item.streamDescriptor.name}`}>
                <td>
                  <CatalogDiffAccordion data={item} catalog={catalog} />
                </td>
              </tr>
            ) : (
              <StreamRow
                item={item}
                catalog={catalog}
                key={`${item.streamDescriptor.namespace}.${item.streamDescriptor.name}`}
              />
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
