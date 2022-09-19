import { Disclosure } from "@headlessui/react";
import { useMemo } from "react";

import { StreamTransform } from "core/request/AirbyteClient";

import { getSortedDiff } from "../utils";
import styles from "./DiffAccordion.module.scss";
import { DiffAccordionHeader } from "./DiffAccordionHeader";
import { DiffFieldTable } from "./DiffFieldTable";

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
            <Disclosure.Button className={styles.accordionButton} aria-label="toggle accordion">
              <DiffAccordionHeader
                streamDescriptor={streamTransform.streamDescriptor}
                removedCount={removedItems.length}
                newCount={newItems.length}
                changedCount={changedItems.length}
                open={open}
              />
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
