import React, { useEffect, useCallback } from "react";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";
import useRouter from "hooks/useRouter";
import { RoutePaths } from "pages/routePaths";

interface IProps {
  statusCode?: number;
}

const UpdateStatusError: React.FC<IProps> = ({ statusCode }) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const { push } = useRouter();

  const onChangeStatusError = useCallback(() => {
    if (statusCode === 705 || statusCode === 707 || statusCode === 708) {
      let modalText = "connection.unable.freeTrial.modal.text";
      if (statusCode === 707) {
        modalText = "connection.unable.limit.modal.text";
      } else if (statusCode === 708) {
        modalText = "connection.unable.expired.modal.text";
      }
      openConfirmationModal({
        title: "connection.unable.modal.title",
        text: modalText,
        submitButtonText: "connection.unable.modal.confirm",
        cancelButtonText: "connection.unable.modal.cancel",
        buttonReverse: true,
        onSubmit: () => {
          closeConfirmationModal();
          push(`/${RoutePaths.Settings}/${RoutePaths.PlanAndBilling}`);
        },
      });
    }
  }, [statusCode, closeConfirmationModal, push, openConfirmationModal]);

  useEffect(() => {
    onChangeStatusError();
  }, [statusCode, onChangeStatusError]);

  return null;
};

export { UpdateStatusError };
