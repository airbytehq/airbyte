import { AirbyteRequestService } from "core/request/AirbyteRequestService";

class SourceAuthService extends AirbyteRequestService {
  get url(): string {
    return "source_oauths";
  }

  public getConsentUrl(body: any): Promise<any> {
    return this.fetch<any>(`${this.url}/get_consent_url`, body);
  }

  public completeOauth(body: any): Promise<any> {
    return this.fetch<any>(`${this.url}/complete_oauth`, body);
  }
}

export { SourceAuthService };
