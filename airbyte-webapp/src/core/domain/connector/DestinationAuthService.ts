import {
  completeDestinationOAuth,
  CompleteDestinationOAuthRequest,
  DestinationOauthConsentRequest,
  getDestinationOAuthConsent,
} from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class DestinationAuthService extends AirbyteRequestService {
  public getConsentUrl(body: DestinationOauthConsentRequest) {
    return getDestinationOAuthConsent(body, this.requestOptions);
  }

  public completeOauth(body: CompleteDestinationOAuthRequest) {
    return completeDestinationOAuth(body, this.requestOptions);
  }
}
