import {
  completeDestinationOAuth,
  CompleteDestinationOAuthRequest,
  DestinationOauthConsentRequest,
  getDestinationOAuthConsent,
} from "../../request/GeneratedApi";

export class DestinationAuthService {
  public getConsentUrl(body: DestinationOauthConsentRequest) {
    return getDestinationOAuthConsent(body);
  }

  public completeOauth(body: CompleteDestinationOAuthRequest) {
    return completeDestinationOAuth(body);
  }
}
