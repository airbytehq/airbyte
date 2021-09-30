import { AirbyteRequestService } from "core/request/AirbyteRequestService";
import { SourceGetConsentPayload } from "./types";

class SourceAuthService extends AirbyteRequestService {
  get url(): string {
    return "source_oauths";
  }

  public getConsentUrl(
    body: SourceGetConsentPayload
  ): Promise<{ consentUrl: string }> {
    return this.fetch<{ consentUrl: string }>(
      `${this.url}/get_consent_url`,
      body
    );
  }

  public completeOauth(
    body: SourceGetConsentPayload & {
      queryParams: Record<string, unknown>;
    }
  ): Promise<Record<string, unknown>> {
    return this.fetch<Record<string, unknown>>(
      `${this.url}/complete_oauth`,
      body
    );
  }
}

export { SourceAuthService };
