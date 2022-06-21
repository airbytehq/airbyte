import { AirbyteCatalog, FieldTransform } from "core/request/AirbyteClient";

import { CatalogDiffModalSection } from "./CatalogDiffModalSection";

interface CatalogDiffModalAccordionProps {
  data: FieldTransform[];
  catalog: AirbyteCatalog;
}

export const CatalogDiffModalAccordion: React.FC<CatalogDiffModalAccordionProps> = ({ data, catalog }) => {
  //do we already have a reusable accordion that accepts children? if so use that...

  //todo: this is basically the same set of filters as what happens at the root level with the streams... should that logic be exported/combined?
  const addedFields = data.filter((item) => item.transformType === "add_field");
  const removedFields = data.filter((item) => item.transformType === "remove_field");
  const updatedFields = data.filter((item) => item.transformType === "update_field_schema");

  // /* TODO:    1. if we already have an accordion use that and add custom classes
  //             2. Accordion will have a header with the caret, the name, and the number of added/removed/udpated fields...
  //             3. probably a smarter way to pass those props?
  //   */
  return (
    <AccordionComponent added={addedFields.length} removed={removedFields.length} updated={updatedFields.length}>
      {addedFields.length > 1 && <CatalogDiffModalSection data={addedFields} catalog={catalog} isChild />}
      {removedFields.length > 1 && <CatalogDiffModalSection data={removedFields} catalog={catalog} isChild />}
      {updatedFields.length > 1 && <CatalogDiffModalSection data={updatedFields} catalog={catalog} isChild />}
    </AccordionComponent>
  );
};
