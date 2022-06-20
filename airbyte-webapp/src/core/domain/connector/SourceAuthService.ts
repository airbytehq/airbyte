import {
  completeSourceOAuth,
  CompleteSourceOauthRequest,
  getSourceOAuthConsent,
  SourceOauthConsentRequest,
} from "../../request/AirbyteClient";
import { AirbyteRequestService } from "../../request/AirbyteRequestService";

export class SourceAuthService extends AirbyteRequestService {
  public getConsentUrl(body: SourceOauthConsentRequest) {
    return getSourceOAuthConsent(body, this.requestOptions);
  }

  public completeOauth(body: CompleteSourceOauthRequest) {
    return completeSourceOAuth(body, this.requestOptions);
  }
}
