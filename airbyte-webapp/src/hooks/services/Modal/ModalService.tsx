import React, { useContext, useMemo, useRef, useState } from "react";
import { firstValueFrom, Subject } from "rxjs";

import { Modal } from "components/ui/Modal";

import { ModalOptions, ModalResult, ModalServiceContext } from "./types";

export class ModalCancel extends Error {}

const modalServiceContext = React.createContext<ModalServiceContext | undefined>(undefined);

export const ModalServiceProvider: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => {
  // The any here is due to the fact, that every call to open a modal might come in with
  // a different type, thus we can't type this with unknown or a generic.
  // The consuming code of this service though is properly typed, so that this `any` stays
  // encapsulated within this component.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [modalOptions, setModalOptions] = useState<ModalOptions<any>>();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const resultSubjectRef = useRef<Subject<ModalResult<any>>>();

  const service: ModalServiceContext = useMemo(
    () => ({
      openModal: (options) => {
        resultSubjectRef.current = new Subject();
        setModalOptions(options);

        return firstValueFrom(resultSubjectRef.current).then((reason) => {
          setModalOptions(undefined);
          resultSubjectRef.current = undefined;
          return reason;
        });
      },
      closeModal: () => {
        resultSubjectRef.current?.next({ type: "canceled" });
      },
    }),
    []
  );

  return (
    <modalServiceContext.Provider value={service}>
      {children}
      {modalOptions && (
        <Modal
          title={modalOptions.title}
          size={modalOptions.size}
          testId={modalOptions.testId}
          onClose={modalOptions.preventCancel ? undefined : () => resultSubjectRef.current?.next({ type: "canceled" })}
        >
          <modalOptions.content
            onCancel={() => resultSubjectRef.current?.next({ type: "canceled" })}
            onClose={(reason) => resultSubjectRef.current?.next({ type: "closed", reason })}
          />
        </Modal>
      )}
    </modalServiceContext.Provider>
  );
};

export const useModalService = () => {
  const context = useContext(modalServiceContext);
  if (!context) {
    throw new Error("Can't use ModalService outside ModalServiceProvider");
  }
  return context;
};
