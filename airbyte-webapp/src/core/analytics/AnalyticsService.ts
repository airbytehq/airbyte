import { Action, EventParams, Namespace, SegmentAnalytics } from "./types";

export class AnalyticsService {
  constructor(private context: Record<string, unknown>, private version?: string) {}

  private getSegmentAnalytics = (): SegmentAnalytics | undefined => window.analytics;

  alias = (newId: string): void => this.getSegmentAnalytics()?.alias?.(newId);

  page = (name: string): void => this.getSegmentAnalytics()?.page?.(name);

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
}
