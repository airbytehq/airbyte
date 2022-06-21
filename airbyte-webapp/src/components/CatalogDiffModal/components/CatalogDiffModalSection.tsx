import { AirbyteCatalog, FieldTransform, StreamTransform } from "core/request/AirbyteClient";

import { CatalogDiffModalAccordion } from "./CatalogDiffModalAccordion";
import { CatalogDiffModalRow } from "./CatalogDiffModalRow";

interface CatalogDiffModalSectionProps {
  data: StreamTransform[] | FieldTransform[];
  catalog: AirbyteCatalog;
  isChild?: boolean;
}

export const CatalogDiffModalSection: React.FC<CatalogDiffModalSectionProps> = ({ data, catalog, isChild }) => {
  //note: do we have to send the catalog along for a field?
  //isChild will be used to demote headings within the accordion

  return (
    <>
      {data.map((item) => {
        Array.isArray(item) ? (
          //if the item is an array, this is a section of field transformations and we should create
          //the accordion.
          <CatalogDiffModalAccordion data={item} catalog={catalog} />
        ) : (
          // otherwise just generate the normal row for this item
          //`item` may be a stream or a field here.
          <CatalogDiffModalRow item={item} catalog={catalog} />
        );
      })}
    </>
  );
};
