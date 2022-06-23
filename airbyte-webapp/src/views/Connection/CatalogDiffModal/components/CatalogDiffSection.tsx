import { AirbyteCatalog, StreamTransform } from "core/request/AirbyteClient";

import { CatalogDiffAccordion } from "./CatalogDiffAccordion";
import { CatalogDiffRow } from "./CatalogDiffRow";

interface CatalogDiffSectionProps {
  data: StreamTransform[];
  catalog: AirbyteCatalog;
}

export const CatalogDiffSection: React.FC<CatalogDiffSectionProps> = ({ data, catalog }) => {
  //note: do we have to send the catalog along for a field?
  //isChild will be used to demote headings within the accordion

  return (
    <>
      {/* generic header */}
      <div>{/* {data.length} {unit} {action} */}</div>
      {/* update stream should make an accordion, others should make a row */}
      {data.map((item) => {
        return item.transformType === "update_stream" ? (
          <CatalogDiffRow item={item} catalog={catalog} />
        ) : (
          <CatalogDiffAccordion data={item.updateStream} catalog={catalog} />
        );
      })}
    </>
  );
};
