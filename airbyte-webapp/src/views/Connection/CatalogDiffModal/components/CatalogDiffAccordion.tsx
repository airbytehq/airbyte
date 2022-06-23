import { AirbyteCatalog, FieldTransform } from "core/request/AirbyteClient";

import { CatalogDiffSection } from "./CatalogDiffSection";

interface CatalogDiffAccordionProps {
  data?: FieldTransform[]; // stream transforms with type 'update_stream'
  catalog: AirbyteCatalog;
}

export const CatalogDiffAccordion: React.FC<CatalogDiffAccordionProps> = ({ data, catalog }) => {
  //do we already have a reusable accordion that accepts children? if so use that...

  //todo: this is basically the same set of filters as what happens at the root level with the streams... should that logic be exported/combined?
  const addedFields = data.filter((item) => item.transformType === "add_field");
  const removedFields = data.filter((item) => item.transformType === "remove_field");
  const updatedFields = data.filter((item) => item.transformType === "update_field_schema");

  // /* TODO:    1. Timebox trying out a Headless UI accordion here, otherwise can implement our own
  //             2. Accordion will have a header with the caret, the name, and the number of added/removed/udpated fields...
  //             3. maybe a cimpler way to pass those props?
  //   */
  return (
    <AccordionComponent added={addedFields.length} removed={removedFields.length} updated={updatedFields.length}>
      {addedFields.length > 1 && <CatalogDiffSection data={addedFields} catalog={catalog} />}
      {removedFields.length > 1 && <CatalogDiffSection data={removedFields} catalog={catalog} />}
      {updatedFields.length > 1 && <CatalogDiffSection data={updatedFields} catalog={catalog} />}
    </AccordionComponent>
  );
};
