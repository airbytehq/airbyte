import { AirbyteCatalog, FieldTransform, StreamTransform } from "core/request/AirbyteClient";

import { CatalogDiffRow } from "./CatalogDiffRow";

interface CatalogDiffSectionProps {
  data: StreamTransform[] | FieldTransform[];
  catalog: AirbyteCatalog;
  isChild?: boolean;
}

export const CatalogDiffSection: React.FC<CatalogDiffSectionProps> = ({ data, catalog, isChild }) => {
  //note: do we have to send the catalog along for a field?
  //isChild will be used to demote headings within the accordion

  return (
    <>
      {data.map((item) => {
        return <CatalogDiffRow item={item} catalog={catalog} />;
      })}
    </>
  );
};
