export const PAYMENT_STATUS = {
  Free_Trial: "Free trial",
  Subscription: "Subscription",
  Cancel_Subscription: "Cancel subscription",
  Pause_Subscription: "Pause subscription",
  Renewal_Failed: "Renewal failed",
};
export const CHINESE_PAYMENT_STATUS = {
  Free_Trial: "免费试用",
  Subscription: "订阅",
  Cancel_Subscription: "取消订阅",
  Pause_Subscription: "暂停订阅",
  Renewal_Failed: "续期失败",
};
export const DASPIRE_PAYMENT_STATUS = Object.values(PAYMENT_STATUS);
export const DASPIRE_CHINESE_PAYMENT_STATUS = Object.values(CHINESE_PAYMENT_STATUS);
export const getPaymentStatus = (status: number): string => {
  return DASPIRE_PAYMENT_STATUS[status - 1];
};
export const getChinesePaymentStatus = (status: number): string => {
  return DASPIRE_CHINESE_PAYMENT_STATUS[status - 1];
};
