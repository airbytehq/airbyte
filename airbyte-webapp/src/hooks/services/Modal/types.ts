import React from "react";

export interface ModalOptions {
  title: React.ReactNode;
  content: React.ComponentType<ModalContentProps>;
}

export type ModalResult = { type: "canceled" } | { type: "closed"; reason: unknown };

interface ModalContentProps {
  onClose: (reason: unknown) => void;
  onCancel: () => void;
}

export interface ModalServiceContextType {
  openModal: (options: ModalOptions) => Promise<ModalResult>;
  closeModal: () => void;
}
