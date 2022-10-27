import { renderHook } from "@testing-library/react-hooks";
import { useFormikContext } from "formik";

import { SourceDefinitionSpecificationRead } from "core/request/AirbyteClient";
import { FeatureItem, FeatureService } from "hooks/services/Feature";

import { useConnectorForm } from "./connectorFormContext";
import { useAuthentication as useAuthenticationHook } from "./useAuthentication";
import { noPredicateAdvancedAuth, predicateInsideConditional } from "./useAuthentication.mocks";
import { makeConnectionConfigurationPath } from "./utils";

jest.mock("./connectorFormContext");
jest.mock("formik", () => ({
  ...jest.requireActual("formik"),
  useFormikContext: jest.fn(),
}));

const mockConnectorForm = useConnectorForm as unknown as jest.Mock<Partial<ReturnType<typeof useConnectorForm>>>;
const mockFormikContext = useFormikContext as unknown as jest.Mock<Partial<ReturnType<typeof useFormikContext>>>;

interface MockParams {
  connector: Pick<SourceDefinitionSpecificationRead, "advancedAuth" | "authSpecification" | "connectionSpecification">;
  values: unknown;
  submitCount?: number;
  fieldMeta?: Record<string, { error?: string }>;
}

const mockContext = ({ connector, values, submitCount, fieldMeta = {} }: MockParams) => {
  mockFormikContext.mockReturnValue({
    values,
    submitCount: submitCount ?? 0,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    getFieldMeta: (field) => (fieldMeta[field] ?? {}) as any,
  });
  mockConnectorForm.mockReturnValue({
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    selectedConnector: { ...connector, sourceDefinitionId: "12345", jobInfo: {} as any },
  });
};

const useAuthentication = (withOauthFeature = true) => {
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const { result } = renderHook(() => useAuthenticationHook(), {
    wrapper: ({ children }) => (
      <FeatureService features={withOauthFeature ? [FeatureItem.AllowOAuthConnector] : []}>{children}</FeatureService>
    ),
  });
  return result.current;
};

describe("useAuthentication", () => {
  it("should return empty results for non OAuth connectors", () => {
    mockContext({ connector: {}, values: {} });
    const result = useAuthentication();
    expect(result.hiddenAuthFieldErrors).toEqual({});
    expect(result.shouldShowAuthButton("field")).toBe(false);
    expect(result.isHiddenAuthField("field")).toBe(false);
  });

  it("should not handle auth specifically if OAuth feature is disabled", () => {
    mockContext({
      connector: { advancedAuth: predicateInsideConditional },
      values: { connectionConfiguration: { credentials: { auth_type: "oauth2.0" } } },
    });
    const result = useAuthentication(false);
    expect(result.isHiddenAuthField(makeConnectionConfigurationPath(["credentials", "access_token"]))).toBe(false);
    expect(result.shouldShowAuthButton(makeConnectionConfigurationPath(["credentials", "auth_type"]))).toBe(false);
  });

  describe("for advancedAuth connectors", () => {
    describe("without a predicateKey", () => {
      it("should calculate hiddenAuthFields correctly", () => {
        mockContext({ connector: { advancedAuth: noPredicateAdvancedAuth }, values: {} });
        const result = useAuthentication();
        expect(result.isHiddenAuthField(makeConnectionConfigurationPath(["access_token"]))).toBe(true);
        expect(result.isHiddenAuthField(makeConnectionConfigurationPath(["client_id"]))).toBe(false);
        expect(result.isHiddenAuthField(makeConnectionConfigurationPath(["client_secret"]))).toBe(false);
      });

      it("should show the auth button on the root level", () => {
        mockContext({ connector: { advancedAuth: noPredicateAdvancedAuth }, values: {} });
        const result = useAuthentication();
        expect(result.shouldShowAuthButton(makeConnectionConfigurationPath())).toBe(true);
      });

      it("should not return authErrors before submitting", () => {
        const accessTokenField = makeConnectionConfigurationPath(["access_token"]);
        mockContext({
          connector: { advancedAuth: noPredicateAdvancedAuth },
          values: {},
          fieldMeta: { [accessTokenField]: { error: "form.empty.error" } },
          submitCount: 0,
        });
        const result = useAuthentication();
        expect(result.hiddenAuthFieldErrors).toEqual({});
      });

      it("should return existing authErrors if submitted once", () => {
        const accessTokenField = makeConnectionConfigurationPath(["access_token"]);
        mockContext({
          connector: { advancedAuth: noPredicateAdvancedAuth },
          values: {},
          fieldMeta: { [accessTokenField]: { error: "form.empty.error" } },
          submitCount: 1,
        });
        const result = useAuthentication();
        expect(result.hiddenAuthFieldErrors).toEqual({ [accessTokenField]: "form.empty.error" });
      });
    });

    describe("with predicateKey inside conditional", () => {
      it("should hide auth fields when predicate value matches", () => {
        mockContext({
          connector: { advancedAuth: predicateInsideConditional },
          values: { connectionConfiguration: { credentials: { auth_type: "oauth2.0" } } },
        });
        const result = useAuthentication();
        expect(result.isHiddenAuthField(makeConnectionConfigurationPath(["credentials", "access_token"]))).toBe(true);
        expect(result.isHiddenAuthField(makeConnectionConfigurationPath(["credentials", "client_id"]))).toBe(true);
        expect(result.isHiddenAuthField(makeConnectionConfigurationPath(["credentials", "client_secret"]))).toBe(true);
      });

      it("should not hide auth fields when predicate value is a mismatch", () => {
        mockContext({
          connector: { advancedAuth: predicateInsideConditional },
          values: { connectionConfiguration: { credentials: { auth_type: "token" } } },
        });
        const result = useAuthentication();
        expect(result.isHiddenAuthField(makeConnectionConfigurationPath(["credentials", "access_token"]))).toBe(false);
        expect(result.isHiddenAuthField(makeConnectionConfigurationPath(["credentials", "client_id"]))).toBe(false);
        expect(result.isHiddenAuthField(makeConnectionConfigurationPath(["credentials", "client_secret"]))).toBe(false);
      });

      it("should show the auth button inside the conditional if right option is selected", () => {
        mockContext({
          connector: { advancedAuth: predicateInsideConditional },
          values: { connectionConfiguration: { credentials: { auth_type: "oauth2.0" } } },
        });
        const result = useAuthentication();
        expect(result.shouldShowAuthButton(makeConnectionConfigurationPath(["credentials", "auth_type"]))).toBe(true);
      });

      it("shouldn't show the auth button if the wrong conditional option is selected", () => {
        mockContext({
          connector: { advancedAuth: predicateInsideConditional },
          values: { connectionConfiguration: { credentials: { auth_type: "token" } } },
        });
        const result = useAuthentication();
        expect(result.shouldShowAuthButton(makeConnectionConfigurationPath(["credentials", "auth_type"]))).toBe(false);
      });

      it("should not return authErrors before submitting", () => {
        const accessTokenField = makeConnectionConfigurationPath(["credentials", "access_token"]);
        const clientIdField = makeConnectionConfigurationPath(["credentials", "client_id"]);
        mockContext({
          connector: { advancedAuth: predicateInsideConditional },
          values: { connectionConfiguration: { credentials: { auth_type: "oauth2.0" } } },
          fieldMeta: { [accessTokenField]: { error: "form.empty.error" }, [clientIdField]: { error: "another.error" } },
          submitCount: 0,
        });
        const result = useAuthentication();
        expect(result.hiddenAuthFieldErrors).toEqual({});
      });

      it("should return authErrors when conditional has correct option selected", () => {
        const accessTokenField = makeConnectionConfigurationPath(["credentials", "access_token"]);
        const clientIdField = makeConnectionConfigurationPath(["credentials", "client_id"]);
        mockContext({
          connector: { advancedAuth: predicateInsideConditional },
          values: { connectionConfiguration: { credentials: { auth_type: "oauth2.0" } } },
          fieldMeta: { [accessTokenField]: { error: "form.empty.error" }, [clientIdField]: { error: "another.error" } },
          submitCount: 1,
        });
        const result = useAuthentication();
        expect(result.hiddenAuthFieldErrors).toEqual({
          [accessTokenField]: "form.empty.error",
          [clientIdField]: "another.error",
        });
      });

      it("should not return authErrors when conditional has the incorrect option selected", () => {
        const accessTokenField = makeConnectionConfigurationPath(["credentials", "access_token"]);
        const clientIdField = makeConnectionConfigurationPath(["credentials", "client_id"]);
        mockContext({
          connector: { advancedAuth: predicateInsideConditional },
          values: { connectionConfiguration: { credentials: { auth_type: "token" } } },
          fieldMeta: { [accessTokenField]: { error: "form.empty.error" }, [clientIdField]: { error: "another.error" } },
          submitCount: 1,
        });
        const result = useAuthentication();
        expect(result.hiddenAuthFieldErrors).toEqual({});
      });
    });
  });
});
