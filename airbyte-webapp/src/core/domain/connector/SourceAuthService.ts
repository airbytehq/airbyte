import {
  completeSourceOAuth,
  CompleteSourceOauthRequest,
  getSourceOAuthConsent,
  SourceOauthConsentRequest,
} from "../../request/GeneratedApi";

export class SourceAuthService {
  public getConsentUrl(body: SourceOauthConsentRequest) {
    return getSourceOAuthConsent(body);
  }

  public completeOauth(body: CompleteSourceOauthRequest) {
    return completeSourceOAuth(body);
  }
}
