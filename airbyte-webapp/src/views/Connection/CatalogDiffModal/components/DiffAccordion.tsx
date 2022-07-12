import { faAngleDown, faAngleRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Disclosure } from "@headlessui/react";
import classnames from "classnames";
import { useIntl } from "react-intl";

import { ImageBlock } from "components";

import { StreamTransform } from "core/request/AirbyteClient";

import { diffReducer } from "../CatalogDiffModal";
import styles from "./DiffAccordion.module.scss";
import { DiffFieldTable } from "./DiffFieldTable";
import { ModificationIcon } from "./ModificationIcon";

interface DiffAccordionProps {
  streamTransform: StreamTransform;
}

export const DiffAccordion: React.FC<DiffAccordionProps> = ({ streamTransform }) => {
  const { formatMessage } = useIntl();

  if (!streamTransform.updateStream) {
    return null;
  }

  console.log(streamTransform.updateStream);
  const { newItems, removedItems, changedItems } = diffReducer(streamTransform.updateStream);

  // eslint-disable-next-line css-modules/no-undef-class
  const nameCellStyle = classnames(styles.nameCell, styles.row);
  // eslint-disable-next-line css-modules/no-undef-class
  const namespaceCellStyles = classnames(styles.nameCell, styles.row, styles.namespace);

  return (
    <div className={styles.accordionContainer}>
      <Disclosure>
        {({ open }) => (
          <>
            <Disclosure.Button className={styles.accordionButton}>
              <ModificationIcon />
              <div
                className={namespaceCellStyles}
                aria-labelledby={formatMessage({ id: "connection.updateSchema.namespace" })}
              >
                {open ? <FontAwesomeIcon icon={faAngleDown} /> : <FontAwesomeIcon icon={faAngleRight} />}
                {streamTransform.streamDescriptor.namespace}
              </div>
              <div className={nameCellStyle} aria-labelledby={formatMessage({ id: "connection.updateSchema.name" })}>
                {streamTransform.streamDescriptor.name}
              </div>
              <div className={styles.iconBlock}>
                {removedItems.length > 0 && (
                  <ImageBlock
                    num={removedItems.length}
                    color="red"
                    light
                    ariaLabel={`${removedItems.length} ${formatMessage(
                      {
                        id: "connection.updateSchema.removed",
                      },
                      {
                        item: formatMessage({ id: "field" }, { values: { count: removedItems.length } }),
                      }
                    )}`}
                  />
                )}
                {newItems.length > 0 && (
                  <ImageBlock
                    num={newItems.length}
                    color="green"
                    light
                    ariaLabel={`${newItems.length} ${formatMessage(
                      {
                        id: "connection.updateSchema.new",
                      },
                      {
                        item: formatMessage({ id: "field" }, { values: { count: newItems.length } }),
                      }
                    )}`}
                  />
                )}
                {changedItems.length > 0 && (
                  <ImageBlock
                    num={changedItems.length}
                    color="blue"
                    light
                    ariaLabel={`${changedItems.length} ${formatMessage(
                      {
                        id: "connection.updateSchema.changed",
                      },
                      {
                        item: formatMessage({ id: "field" }, { values: { count: changedItems.length } }),
                      }
                    )}`}
                  />
                )}
              </div>
            </Disclosure.Button>
            <Disclosure.Panel>
              {removedItems.length > 0 && (
                <div>
                  <DiffFieldTable fieldTransforms={removedItems} diffVerb="removed" />
                </div>
              )}
              {newItems.length > 0 && (
                <div>
                  <DiffFieldTable fieldTransforms={newItems} diffVerb="new" />
                </div>
              )}
              {changedItems.length > 0 && (
                <div>
                  <DiffFieldTable fieldTransforms={changedItems} diffVerb="changed" />
                </div>
              )}
            </Disclosure.Panel>
          </>
        )}
      </Disclosure>
    </div>
  );
};
