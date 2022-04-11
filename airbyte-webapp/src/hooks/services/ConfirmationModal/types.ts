import React from "react";

export interface ConfirmationModalOptions {
  submitButtonText: React.ReactNode;
  title: React.ReactNode;
  text: React.ReactNode;
  onSubmit: () => Promise<void>;
}

export interface ConfirmationModalServiceApi {
  openConfirmationModal: (confirmationModal: ConfirmationModalOptions) => void;
  closeConfirmationModal: () => void;
}

export interface ConfirmationModalState {
  isOpen: boolean;
  confirmationModal: ConfirmationModalOptions | null;
}
