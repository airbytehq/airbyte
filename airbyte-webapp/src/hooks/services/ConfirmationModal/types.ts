import React from "react";

export interface ConfirmationModal {
  submitButtonText: React.ReactNode;
  title: React.ReactNode;
  text: React.ReactNode;
  onSubmit: () => Promise<void>;
}

export interface ConfirmationModalServiceApi {
  openConfirmationModal: (confirmationModal: ConfirmationModal) => void;
  closeConfirmationModal: () => void;
}

export interface ConfirmationModalState {
  isOpen: boolean;
  confirmationModal: ConfirmationModal | null;
}
