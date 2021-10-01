import { SegmentAnalytics } from "./types";

export class AnalyticsService {
  constructor(private userId?: string, private version?: string) {}

  private getSegmentAnalytics = (): SegmentAnalytics | undefined =>
    window.analytics;

  alias = (newId: string): void => this.getSegmentAnalytics()?.alias?.(newId);

  page = (name: string): void => this.getSegmentAnalytics()?.page?.(name);

  reset = (): void => this.getSegmentAnalytics()?.reset?.();

  track = (name: string, properties: Record<string, unknown>): void =>
    this.getSegmentAnalytics()?.track?.(name, {
      user_id: this.userId,
      ...properties,
      airbyte_version: this.version,
      environment: this.version === "dev" ? "dev" : "prod",
    });

  identify = (userId: string, traits: Record<string, unknown> = {}): void => {
    this.getSegmentAnalytics()?.identify?.(userId, traits);
  };

  group = (
    organisationId: string,
    traits: Record<string, unknown> = {}
  ): void => this.getSegmentAnalytics()?.group?.(organisationId, traits);
}
