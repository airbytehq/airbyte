export const STATUSES = {
  Free_Trial: "Free trial",
  Subscription: "Subscription",
  Cancel_Subscription: "Cancel subscription",
  Pause_Subscription: "Pause subscription",
};

export const DASPIRE_STATUSES = Object.values(STATUSES);

export const getStatusAgainstStatusNumber = (status: number): string => {
  return DASPIRE_STATUSES[status - 1];
};
