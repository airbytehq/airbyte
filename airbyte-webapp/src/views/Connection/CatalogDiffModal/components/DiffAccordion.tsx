import { faAngleDown, faAngleRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Disclosure, Transition } from "@headlessui/react";
import classnames from "classnames";

import { ImageBlock } from "components";

import { StreamTransform } from "core/request/AirbyteClient";

import styles from "./DiffAccordion.module.scss";
import { DiffFieldTable } from "./DiffFieldTable";
import { ModificationIcon } from "./ModificationIcon";

interface DiffAccordionProps {
  data: StreamTransform; // stream transforms with type 'update_stream'
}

export const DiffAccordion: React.FC<DiffAccordionProps> = ({ data }) => {
  const fieldTransforms = data.updateStream;

  if (!fieldTransforms) {
    return null;
  }

  const addedFields = fieldTransforms.filter((item) => item.transformType === "add_field");
  const removedFields = fieldTransforms.filter((item) => item.transformType === "remove_field");
  const updatedFields = fieldTransforms.filter((item) => item.transformType === "update_field_schema");

  // eslint-disable-next-line css-modules/no-undef-class
  const nameCellStyle = classnames(styles.nameCell, styles.row);

  return (
    <tr>
      <td>
        <div className={styles.accordionContainer}>
          <Disclosure>
            {({ open }) => (
              <>
                <Disclosure.Button className={styles.accordionButton}>
                  <ModificationIcon />
                  <div className={nameCellStyle}>
                    {open ? <FontAwesomeIcon icon={faAngleDown} /> : <FontAwesomeIcon icon={faAngleRight} />}
                    {data.streamDescriptor.namespace}
                  </div>
                  <div className={nameCellStyle}>{data.streamDescriptor.name}</div>
                  <div className={styles.iconBlock}>
                    {removedFields.length > 0 && <ImageBlock num={removedFields.length} color="red" light />}
                    {addedFields.length > 0 && <ImageBlock num={addedFields.length} color="green" light />}
                    {updatedFields.length > 0 && <ImageBlock num={updatedFields.length} color="blue" light />}
                  </div>
                </Disclosure.Button>
                {/* TODO: can't get transition to play nicely... */}
                <Transition
                  show={open}
                  enter="transition duration-100 ease-out"
                  enterFrom="transform scale-95 opacity-0"
                  enterTo="transform scale-100 opacity-100"
                  leave="transition duration-75 ease-out"
                  leaveFrom="transform scale-100 opacity-100"
                  leaveTo="transform scale-95 opacity-0"
                >
                  <Disclosure.Panel static>
                    {removedFields.length > 0 && (
                      <div>
                        <DiffFieldTable fieldTransforms={removedFields} diffVerb="removed" />
                      </div>
                    )}
                    {addedFields.length > 0 && (
                      <div>
                        <DiffFieldTable fieldTransforms={addedFields} diffVerb="new" />
                      </div>
                    )}
                    {updatedFields.length > 0 && (
                      <div>
                        <DiffFieldTable fieldTransforms={updatedFields} diffVerb="changed" />
                      </div>
                    )}
                  </Disclosure.Panel>
                </Transition>
              </>
            )}
          </Disclosure>
        </div>
      </td>
    </tr>
  );
};
