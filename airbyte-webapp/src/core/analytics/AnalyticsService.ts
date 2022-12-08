import { Action, EventParams, Namespace } from "./types";

type Context = Record<string, unknown>;

export class AnalyticsService {
  private context: Context = {};

  constructor(private version?: string) {}

  private getSegmentAnalytics = (): SegmentAnalytics.AnalyticsJS | undefined => window.analytics;

  public setContext(context: Context) {
    this.context = {
      ...this.context,
      ...context,
    };
  }

  public removeFromContext(...keys: string[]) {
    keys.forEach((key) => delete this.context[key]);
  }

  alias = (newId: string): void => this.getSegmentAnalytics()?.alias?.(newId);

  page = (name: string): void => this.getSegmentAnalytics()?.page?.(name, { ...this.context });

  reset = (): void => this.getSegmentAnalytics()?.reset?.();

  track = (namespace: Namespace, action: Action, params: EventParams & { actionDescription?: string }) => {
    this.getSegmentAnalytics()?.track(`Airbyte.UI.${namespace}.${action}`, {
      ...params,
      ...this.context,
      airbyte_version: this.version,
      environment: this.version === "dev" ? "dev" : "prod",
    });
  };

  identify = (userId: string, traits: Record<string, unknown> = {}): void => {
    this.getSegmentAnalytics()?.identify?.(userId, traits);
  };

  group = (organisationId: string, traits: Record<string, unknown> = {}): void =>
    this.getSegmentAnalytics()?.group?.(organisationId, traits);
  setAnonymousId = (anonymousId: string) => this.getSegmentAnalytics()?.setAnonymousId(anonymousId);
}
