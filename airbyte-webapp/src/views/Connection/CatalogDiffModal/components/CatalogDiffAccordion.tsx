import { faAngleDown, faAngleRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Disclosure as Accordion } from "@headlessui/react";

import { AirbyteCatalog, StreamTransform } from "core/request/AirbyteClient";

import styles from "./CatalogDiffAccordion.module.scss";
import { DiffHeader } from "./DiffHeader";
import { ModificationIcon } from "./ModificationIcon";

interface CatalogDiffAccordionProps {
  data: StreamTransform; // stream transforms with type 'update_stream'
  catalog: AirbyteCatalog;
}

export const CatalogDiffAccordion: React.FC<CatalogDiffAccordionProps> = ({ data }) => {
  //do we already have a reusable accordion that accepts children? if so use that...
  //todo: this is basically the same set of filters as what happens at the root level with the streams... should that logic be exported/combined?

  // /* TODO:    1. Timebox trying out a Headless UI accordion here, otherwise can implement our own
  //             2. Accordion will have a header with the caret, the name, and the number of added/removed/udpated fields...
  //             3. maybe a cimpler way to pass those props?
  //   */

  const fieldTransforms = data.updateStream || [];
  const addedFields = fieldTransforms.filter((item) => item.transformType === "add_field");
  const removedFields = fieldTransforms.filter((item) => item.transformType === "remove_field");
  const updatedFields = fieldTransforms.filter((item) => item.transformType === "update_field_schema");

  return (
    <div className={styles.accordionContainer}>
      <Accordion>
        {({ open }) => (
          <>
            <Accordion.Button className={styles.accordionButton}>
              <ModificationIcon />{" "}
              {open ? <FontAwesomeIcon icon={faAngleDown} /> : <FontAwesomeIcon icon={faAngleRight} />}
              <div className={styles.nameCell}>{data.streamDescriptor.namespace}</div>
              <div className={styles.nameCell}>{data.streamDescriptor.name}</div>
            </Accordion.Button>
            <Accordion.Panel>
              {removedFields.length > 0 && (
                <div>
                  <DiffHeader diffCount={removedFields.length} diffVerb="removed" diffType="field" />
                  {/* <CatalogDiffFieldTable fieldTransforms={removedFields} /> */}
                </div>
              )}
              {addedFields.length > 0 && (
                <div>
                  <DiffHeader diffCount={addedFields.length} diffVerb="new" diffType="field" />
                  {/* <CatalogDiffFieldTable fieldTransforms={addedFields} /> */}
                </div>
              )}
              {updatedFields.length > 0 && (
                <div>
                  <DiffHeader diffCount={updatedFields.length} diffVerb="changed" diffType="field" />
                  {/* <CatalogDiffFieldTable fieldTransforms={updatedFields} /> */}
                </div>
              )}
            </Accordion.Panel>
          </>
        )}
      </Accordion>
    </div>
  );
};
