import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import {
  userPlan,
  createSubscription,
  getUpgradeSubscription,
  upgradeSubscription,
  pauseSubscription,
  failedPaymentDetails,
  updatePaymentMethod,
} from "../../request/DaspireClient";
import { GetUpgradeSubscriptionParams } from "./Payment";

export class PaymentService extends AirbyteRequestService {
  public userPlanDetail() {
    return userPlan(this.requestOptions);
  }

  public createSubscriptionUrl(productItemId: string) {
    return createSubscription(productItemId, this.requestOptions);
  }

  public getUpgradeSubscription(params: GetUpgradeSubscriptionParams) {
    return getUpgradeSubscription(params, this.requestOptions);
  }

  public upgradeSubscription() {
    return upgradeSubscription(this.requestOptions);
  }

  public pauseSubscription() {
    return pauseSubscription(this.requestOptions);
  }

  public failedPaymentDetails() {
    return failedPaymentDetails(this.requestOptions);
  }

  public updatePaymentMethod(paymentOrderId: string) {
    return updatePaymentMethod(paymentOrderId, this.requestOptions);
  }
}
