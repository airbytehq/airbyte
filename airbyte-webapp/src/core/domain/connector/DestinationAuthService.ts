import { AirbyteRequestService } from "../../request/AirbyteRequestService";
import {
  completeDestinationOAuth,
  CompleteDestinationOAuthRequest,
  DestinationOauthConsentRequest,
  getDestinationOAuthConsent,
} from "../../request/GeneratedApi";

export class DestinationAuthService extends AirbyteRequestService {
  public getConsentUrl(body: DestinationOauthConsentRequest) {
    return getDestinationOAuthConsent(body, this.requestOptions);
  }

  public completeOauth(body: CompleteDestinationOAuthRequest) {
    return completeDestinationOAuth(body, this.requestOptions);
  }
}
