import React from "react";

export interface ModalOptions<T> {
  title: React.ReactNode;
  content: React.ComponentType<ModalContentProps<T>>;
}

export type ModalResult<T> = { type: "canceled" } | { type: "closed"; reason: T };

interface ModalContentProps<T> {
  onClose: (reason: T) => void;
  onCancel: () => void;
}

export interface ModalServiceContextType {
  openModal: <ResultType>(options: ModalOptions<ResultType>) => Promise<ModalResult<ResultType>>;
  closeModal: () => void;
}
