declare global {
  interface Window {
    TRACKING_STRATEGY?: string;
    AIRBYTE_VERSION?: string;
    API_URL?: string;
    CLOUD?: string;
    REACT_APP_DATADOG_APPLICATION_ID: string;
    REACT_APP_DATADOG_CLIENT_TOKEN: string;
    REACT_APP_DATADOG_SITE: string;
    REACT_APP_DATADOG_SERVICE: string;
    REACT_APP_SENTRY_DSN?: string;
    REACT_APP_WEBAPP_TAG?: string;
    REACT_APP_INTERCOM_APP_ID?: string;
    REACT_APP_INTEGRATION_DOCS_URLS?: string;
    SEGMENT_TOKEN?: string;
    LAUNCHDARKLY_KEY?: string;
    analytics: SegmentAnalytics.AnalyticsJS;
    reveal: RevealProps;
  }
}

export interface RevealProps {
  id: string;
  name: string;
  legalName: string;
  domain: string;
  domainAliases: string[];
  site: {
    phoneNumbers: string[];
    emailAddresses: string[];
  };
  category: {
    sector: string;
    industryGroup: string;
    industry: string;
    subIndustry: string;
    sicCode: string;
    naicsCode: string;
  };
  tags: string[];
  description: string;
  foundedYear: number;
  location: string;
  timeZone: string;
  utcOffset: number;
  geo: {
    streetNumber: string;
    streetName: string;
    subPremise: string;
    city: string;
    postalCode: string;
    state: string;
    stateCode: string;
    country: string;
    countryCode: string;
    lat: number;
    lng: number;
  };
  logo: string;
  facebook: {
    handle: string;
  };
  linkedin: {
    handle: string;
  };
  twitter: {
    handle: string;
  };
  crunchbase: {
    handle: string;
  };
  emailProvider: boolean;
  type: string;
  ticker: string;
  identifiers: {
    usEIN: string;
  };
  phone: string;
  indexedAt: string;
  metrics: {
    alexaUsRank: number;
    alexaGlobalRank: number;
    employees: number;
    employeesRange: string;
    marketCap: string;
    raised: number;
    annualRevenue: string;
    estimatedAnnualRevenue: string;
    fiscalYearEnd: number;
  };
  tech: string[];
  techCategories: string[];
  parent: {
    domain: string;
  };
  ultimateParent: {
    domain: string;
  };
}

export interface Config {
  segment: { token: string; enabled: boolean };
  apiUrl: string;
  oauthRedirectUrl: string;
  healthCheckInterval: number;
  version?: string;
  integrationUrl: string;
  launchDarkly?: string;
}

export type DeepPartial<T> = {
  [P in keyof T]+?: DeepPartial<T[P]>;
};

export type ProviderAsync<T> = () => Promise<T>;
export type Provider<T> = () => T;

export type ValueProvider<T> = Array<ProviderAsync<DeepPartial<T>>>;

export type ConfigProvider<T extends Config = Config> = ProviderAsync<DeepPartial<T>>;
