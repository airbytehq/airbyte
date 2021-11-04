import { SegmentAnalytics } from "./types";

export type AdditionalAnalyticsTraits = {
  userId?: string;
  workspaceId?: string;
};

export class AnalyticsService {
  constructor(
    private additionalAnalyticsTraits: AdditionalAnalyticsTraits,
    private version?: string
  ) {}

  private getSegmentAnalytics = (): SegmentAnalytics | undefined =>
    window.analytics;

  alias = (newId: string): void => this.getSegmentAnalytics()?.alias?.(newId);

  page = (name: string): void => this.getSegmentAnalytics()?.page?.(name);

  reset = (): void => this.getSegmentAnalytics()?.reset?.();

  track = (name: string, properties: Record<string, unknown>): void =>
    this.getSegmentAnalytics()?.track?.(name, {
      ...this.additionalAnalyticsTraits,
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
