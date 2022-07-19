import { faAngleDown, faAngleRight } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Disclosure } from "@headlessui/react";
import classnames from "classnames";
import { useMemo } from "react";
import { useIntl } from "react-intl";

import { ImageBlock } from "components";

import { StreamTransform } from "core/request/AirbyteClient";

import { ModificationIcon } from "../../../../components/icons/ModificationIcon";
import { getSortedDiff } from "../utils/utils";
import styles from "./DiffAccordion.module.scss";
import { DiffFieldTable } from "./DiffFieldTable";

interface DiffAccordionProps {
  streamTransform: StreamTransform;
}

export const DiffAccordion: React.FC<DiffAccordionProps> = ({ streamTransform }) => {
  const { formatMessage } = useIntl();

  const { newItems, removedItems, changedItems } = useMemo(
    () => getSortedDiff(streamTransform.updateStream),
    [streamTransform.updateStream]
  );

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
              <div
                className={nameCellStyle}
                aria-labelledby={formatMessage({ id: "connection.updateSchema.streamName" })}
              >
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
              {removedItems.length > 0 && <DiffFieldTable fieldTransforms={removedItems} diffVerb="removed" />}
              {newItems.length > 0 && <DiffFieldTable fieldTransforms={newItems} diffVerb="new" />}
              {changedItems.length > 0 && <DiffFieldTable fieldTransforms={changedItems} diffVerb="changed" />}
            </Disclosure.Panel>
          </>
        )}
      </Disclosure>
    </div>
  );
};
