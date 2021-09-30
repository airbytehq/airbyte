import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { DestinationGetConsentPayload } from "./types";

class DestinationAuthService extends AirbyteRequestService {
  get url(): string {
    return "destination_oauths";
  }

  public getConsentUrl(
    body: DestinationGetConsentPayload
  ): Promise<{ consentUrl: string }> {
    return this.fetch<{ consentUrl: string }>(
      `${this.url}/get_consent_url`,
      body
    );
  }

  public completeOauth(
    body: DestinationGetConsentPayload & {
      queryParams: Record<string, unknown>;
    }
  ): Promise<Record<string, unknown>> {
    return this.fetch<Record<string, unknown>>(
      `${this.url}/complete_oauth`,
      body
    );
  }
}

export { DestinationAuthService };
