import React from "react";

import { ModalProps } from "components/Modal/Modal";

export interface ModalOptions<T> {
  title: ModalProps["title"];
  size?: ModalProps["size"];
  preventCancel?: boolean;
  content: React.ComponentType<ModalContentProps<T>>;
}

export type ModalResult<T> = { type: "canceled" } | { type: "closed"; reason: T };

interface ModalContentProps<T> {
  onClose: (reason: T) => void;
  onCancel: () => void;
}

export interface ModalServiceContext {
  openModal: <ResultType>(options: ModalOptions<ResultType>) => Promise<ModalResult<ResultType>>;
  closeModal: () => void;
}
