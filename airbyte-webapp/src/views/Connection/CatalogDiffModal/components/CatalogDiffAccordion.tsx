import { faAngleDown, faAngleRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Disclosure as Accordion } from "@headlessui/react";

import { AirbyteCatalog, StreamTransform } from "core/request/AirbyteClient";

import styles from "./CatalogDiffAccordion.module.scss";
import { ModificationIcon } from "./ModificationIcon";

interface CatalogDiffAccordionProps {
  data: StreamTransform; // stream transforms with type 'update_stream'
  catalog: AirbyteCatalog;
}

export const CatalogDiffAccordion: React.FC<CatalogDiffAccordionProps> = ({ data }) => {
  //do we already have a reusable accordion that accepts children? if so use that...
  console.log(data);
  //todo: this is basically the same set of filters as what happens at the root level with the streams... should that logic be exported/combined?

  // /* TODO:    1. Timebox trying out a Headless UI accordion here, otherwise can implement our own
  //             2. Accordion will have a header with the caret, the name, and the number of added/removed/udpated fields...
  //             3. maybe a cimpler way to pass those props?
  //   */

  const fieldTransforms = data.updateStream;
  const addedFields = fieldTransforms?.filter((item) => item.transformType === "add_field");
  const removedFields = fieldTransforms?.filter((item) => item.transformType === "remove_field");
  const updatedFields = fieldTransforms?.filter((item) => item.transformType === "update_field_schema");

  return (
    <div className={styles.accordionContainer}>
      <Accordion>
        {({ open }) => (
          <>
            <Accordion.Button className={styles.accordionButton}>
              <ModificationIcon />{" "}
              {open ? <FontAwesomeIcon icon={faAngleDown} /> : <FontAwesomeIcon icon={faAngleRight} />}
              <td className={styles.nameCell}>{data.streamDescriptor.namespace}</td>
              <td className={styles.nameCell}>{data.streamDescriptor.name}</td>
            </Accordion.Button>
            <Accordion.Panel>howdy</Accordion.Panel>
          </>
        )}
      </Accordion>
    </div>
    // <AccordionComponent added={addedFields.length} removed={removedFields.length} updated={updatedFields.length}>
    //   {addedFields.length > 1 && <CatalogDiffSection data={addedFields} catalog={catalog} />}
    //   {removedFields.length > 1 && <CatalogDiffSection data={removedFields} catalog={catalog} />}
    //   {updatedFields.length > 1 && <CatalogDiffSection data={updatedFields} catalog={catalog} />}
    // </AccordionComponent>
  );
};
