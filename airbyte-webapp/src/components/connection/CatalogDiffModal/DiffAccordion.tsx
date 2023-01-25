import { Disclosure } from "@headlessui/react";
import { useMemo } from "react";

import { StreamTransform } from "core/request/AirbyteClient";

import styles from "./DiffAccordion.module.scss";
import { DiffAccordionHeader } from "./DiffAccordionHeader";
import { DiffFieldTable } from "./DiffFieldTable";
import { getSortedDiff } from "./utils";

interface DiffAccordionProps {
  streamTransform: StreamTransform;
}

export const DiffAccordion: React.FC<DiffAccordionProps> = ({ streamTransform }) => {
  const { newItems, removedItems, changedItems } = useMemo(
    () => getSortedDiff(streamTransform.updateStream),
    [streamTransform.updateStream]
  );

  return (
    <div className={styles.accordionContainer}>
      <Disclosure>
        {({ open }) => (
          <>
            <Disclosure.Button
              className={styles.accordionButton}
              aria-label={`${open ? "collapse" : "expand"} list with changes in ${
                streamTransform.streamDescriptor.name
              } stream`}
              data-testid={`toggle-accordion-${streamTransform.streamDescriptor.name}-stream`}
            >
              <DiffAccordionHeader
                streamDescriptor={streamTransform.streamDescriptor}
                removedCount={removedItems.length}
                newCount={newItems.length}
                changedCount={changedItems.length}
                open={open}
              />
            </Disclosure.Button>
            <Disclosure.Panel className={styles.accordionPanel}>
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
