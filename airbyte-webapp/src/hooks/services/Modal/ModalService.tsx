import React, { useContext, useMemo, useRef, useState } from "react";
import { firstValueFrom, Subject } from "rxjs";

import { Modal } from "components";

import { ModalOptions, ModalResult, ModalServiceContextType } from "./types";

const ModalServiceContext = React.createContext<ModalServiceContextType | undefined>(undefined);

export const ModalServiceProvider: React.FC = ({ children }) => {
  const [modalOptions, setModalOptions] = useState<ModalOptions>();
  const promiseRef = useRef<Subject<ModalResult>>();

  const service: ModalServiceContextType = useMemo(
    () => ({
      openModal: (options) => {
        promiseRef.current = new Subject();
        setModalOptions(options);

        return firstValueFrom(promiseRef.current).then((reason) => {
          setModalOptions(undefined);
          promiseRef.current = undefined;
          return reason;
        });
      },
      closeModal: () => {
        promiseRef.current?.next({ type: "canceled" });
      },
    }),
    []
  );

  return (
    <ModalServiceContext.Provider value={service}>
      {children}
      {modalOptions && (
        <Modal title={modalOptions.title} onClose={() => promiseRef.current?.next({ type: "canceled" })}>
          <modalOptions.content
            onCancel={() => promiseRef.current?.next({ type: "canceled" })}
            onClose={(reason: unknown) => promiseRef.current?.next({ type: "closed", reason })}
          />
        </Modal>
      )}
    </ModalServiceContext.Provider>
  );
};

export const useModalService = () => {
  const context = useContext(ModalServiceContext);
  if (!context) {
    throw new Error("Can't use ModalService outside ModalServiceProvider");
  }
  return context;
};
