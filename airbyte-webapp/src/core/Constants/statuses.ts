export const PAYMENT_STATUS = {
  Free_Trial: "Free trial",
  Subscription: "Subscription",
  Cancel_Subscription: "Cancel subscription",
  Pause_Subscription: "Pause subscription",
  Renewal_Failed: "Renewal failed",
};

export const DASPIRE_PAYMENT_STATUS = Object.values(PAYMENT_STATUS);

export const getPaymentStatus = (status: number): string => {
  return DASPIRE_PAYMENT_STATUS[status - 1];
};
