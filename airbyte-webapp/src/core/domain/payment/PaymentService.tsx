import { GetUpgradeSubscriptionParams } from "./Payment";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import {
  userPlan,
  createSubscription,
  getUpgradeSubscription,
  upgradeSubscription,
  pauseSubscription,
  failedPaymentDetails,
  updatePaymentMethod,
  cloudRegions,
  instanceSelected,
  cloudPackages,
} from "../../request/DaspireClient";

export class PaymentService extends AirbyteRequestService {
  public userPlanDetail() {
    return userPlan(this.requestOptions);
  }
  public cloudRegion() {
    return cloudRegions(this.requestOptions);
  }
  public cloudPackage() {
    return cloudPackages(this.requestOptions);
  }
  public instanceSelect(cloudItemId: string) {
    return instanceSelected(cloudItemId, this.requestOptions);
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
