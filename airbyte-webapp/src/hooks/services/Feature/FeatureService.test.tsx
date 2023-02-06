import { render } from "@testing-library/react";
import { renderHook } from "@testing-library/react-hooks";
import React, { useEffect } from "react";

import { FeatureService, IfFeatureEnabled, useFeature, useFeatureService } from "./FeatureService";
import { FeatureItem, FeatureSet } from "./types";

const wrapper: React.FC<React.PropsWithChildren<unknown>> = ({ children }) => (
  <FeatureService features={[FeatureItem.AllowDBTCloudIntegration, FeatureItem.AllowSync]}>{children}</FeatureService>
);

type FeatureOverwrite = FeatureItem[] | FeatureSet | undefined;

interface FeatureOverwrites {
  workspace?: FeatureOverwrite;
  user?: FeatureOverwrite;
  overwrite?: FeatureOverwrite;
}

/**
 * Test utility method to wrap setting all the different level of features, rerender
 * with a different set of features and getting the merged feature set.
 */
const getFeatures = (initialProps: FeatureOverwrites) => {
  return renderHook(
    ({ overwrite, user, workspace }: React.PropsWithChildren<FeatureOverwrites>) => {
      const { features, setWorkspaceFeatures, setUserFeatures, setFeatureOverwrites } = useFeatureService();
      useEffect(() => {
        setWorkspaceFeatures(workspace);
      }, [setWorkspaceFeatures, workspace]);
      useEffect(() => {
        setUserFeatures(user);
      }, [setUserFeatures, user]);
      useEffect(() => {
        setFeatureOverwrites(overwrite);
      }, [overwrite, setFeatureOverwrites]);
      return features;
    },
    { wrapper, initialProps }
  );
};

describe("Feature Service", () => {
  describe("FeatureService", () => {
    it("should allow setting default features", () => {
      const getFeature = (feature: FeatureItem) => renderHook(() => useFeature(feature), { wrapper }).result.current;
      expect(getFeature(FeatureItem.AllowDBTCloudIntegration)).toBe(true);
      expect(getFeature(FeatureItem.AllowCustomDBT)).toBe(false);
      expect(getFeature(FeatureItem.AllowSync)).toBe(true);
      expect(getFeature(FeatureItem.AllowUpdateConnectors)).toBe(false);
    });

    it("workspace features should merge correctly with default features", () => {
      expect(
        getFeatures({
          workspace: [FeatureItem.AllowCustomDBT, FeatureItem.AllowUploadCustomImage],
        }).result.current.sort()
      ).toEqual([
        FeatureItem.AllowCustomDBT,
        FeatureItem.AllowDBTCloudIntegration,
        FeatureItem.AllowSync,
        FeatureItem.AllowUploadCustomImage,
      ]);
    });

    it("workspace features can disable default features", () => {
      expect(
        getFeatures({
          workspace: {
            [FeatureItem.AllowCustomDBT]: true,
            [FeatureItem.AllowDBTCloudIntegration]: false,
          } as FeatureSet,
        }).result.current.sort()
      ).toEqual([FeatureItem.AllowCustomDBT, FeatureItem.AllowSync]);
    });

    it("user features should merge correctly with workspace and default features", () => {
      expect(
        getFeatures({
          workspace: [FeatureItem.AllowCustomDBT, FeatureItem.AllowUploadCustomImage],
          user: [FeatureItem.AllowOAuthConnector],
        }).result.current.sort()
      ).toEqual([
        FeatureItem.AllowCustomDBT,
        FeatureItem.AllowDBTCloudIntegration,
        FeatureItem.AllowOAuthConnector,
        FeatureItem.AllowSync,
        FeatureItem.AllowUploadCustomImage,
      ]);
    });

    it("user features can disable workspace and default features", () => {
      expect(
        getFeatures({
          workspace: [FeatureItem.AllowCustomDBT, FeatureItem.AllowUploadCustomImage],
          user: {
            [FeatureItem.AllowOAuthConnector]: true,
            [FeatureItem.AllowUploadCustomImage]: false,
            [FeatureItem.AllowDBTCloudIntegration]: false,
          } as FeatureSet,
        }).result.current.sort()
      ).toEqual([FeatureItem.AllowCustomDBT, FeatureItem.AllowOAuthConnector, FeatureItem.AllowSync]);
    });

    it("user features can re-enable feature that are disabled per workspace", () => {
      expect(
        getFeatures({
          workspace: { [FeatureItem.AllowCustomDBT]: true, [FeatureItem.AllowSync]: false } as FeatureSet,
          user: [FeatureItem.AllowOAuthConnector, FeatureItem.AllowSync],
        }).result.current.sort()
      ).toEqual([
        FeatureItem.AllowCustomDBT,
        FeatureItem.AllowDBTCloudIntegration,
        FeatureItem.AllowOAuthConnector,
        FeatureItem.AllowSync,
      ]);
    });

    it("overwrite features can overwrite workspace and user features", () => {
      expect(
        getFeatures({
          workspace: { [FeatureItem.AllowCustomDBT]: true, [FeatureItem.AllowSync]: false } as FeatureSet,
          user: {
            [FeatureItem.AllowOAuthConnector]: true,
            [FeatureItem.AllowSync]: true,
            [FeatureItem.AllowDBTCloudIntegration]: false,
          } as FeatureSet,
          overwrite: [FeatureItem.AllowUploadCustomImage, FeatureItem.AllowDBTCloudIntegration],
        }).result.current.sort()
      ).toEqual([
        FeatureItem.AllowCustomDBT,
        FeatureItem.AllowDBTCloudIntegration,
        FeatureItem.AllowOAuthConnector,
        FeatureItem.AllowSync,
        FeatureItem.AllowUploadCustomImage,
      ]);
    });

    it("workspace features can be cleared again", () => {
      const { result, rerender } = getFeatures({
        workspace: { [FeatureItem.AllowCustomDBT]: true, [FeatureItem.AllowSync]: false } as FeatureSet,
      });
      expect(result.current.sort()).toEqual([FeatureItem.AllowCustomDBT, FeatureItem.AllowDBTCloudIntegration]);
      rerender({ workspace: undefined });
      expect(result.current.sort()).toEqual([FeatureItem.AllowDBTCloudIntegration, FeatureItem.AllowSync]);
    });

    it("user features can be cleared again", () => {
      const { result, rerender } = getFeatures({
        user: { [FeatureItem.AllowCustomDBT]: true, [FeatureItem.AllowSync]: false } as FeatureSet,
      });
      expect(result.current.sort()).toEqual([FeatureItem.AllowCustomDBT, FeatureItem.AllowDBTCloudIntegration]);
      rerender({ user: undefined });
      expect(result.current.sort()).toEqual([FeatureItem.AllowDBTCloudIntegration, FeatureItem.AllowSync]);
    });

    it("overwritten features can be cleared again", () => {
      const { result, rerender } = getFeatures({
        overwrite: { [FeatureItem.AllowCustomDBT]: true, [FeatureItem.AllowSync]: false } as FeatureSet,
      });
      expect(result.current.sort()).toEqual([FeatureItem.AllowCustomDBT, FeatureItem.AllowDBTCloudIntegration]);
      rerender({ overwrite: undefined });
      expect(result.current.sort()).toEqual([FeatureItem.AllowDBTCloudIntegration, FeatureItem.AllowSync]);
    });

    describe("env variable overwrites", () => {
      beforeEach(() => {
        process.env.REACT_APP_FEATURE_ALLOW_SYNC = "false";
        process.env.REACT_APP_FEATURE_ALLOW_CHANGE_DATA_GEOGRAPHIES = "true";
      });

      afterEach(() => {
        (process.env.NODE_ENV as string) = "test";
        process.env.REACT_APP_FEATURE_ALLOW_SYNC = undefined;
        process.env.REACT_APP_FEATURE_ALLOW_CHANGE_DATA_GEOGRAPHIES = undefined;
      });

      it("should allow overwriting it in dev", () => {
        (process.env.NODE_ENV as string) = "development";
        const getFeature = (feature: FeatureItem) => renderHook(() => useFeature(feature), { wrapper }).result.current;
        expect(getFeature(FeatureItem.AllowSync)).toBe(false);
        expect(getFeature(FeatureItem.AllowChangeDataGeographies)).toBe(true);
      });

      it("should not overwrite in a non dev environment", () => {
        (process.env.NODE_ENV as string) = "production";
        const getFeature = (feature: FeatureItem) => renderHook(() => useFeature(feature), { wrapper }).result.current;
        expect(getFeature(FeatureItem.AllowSync)).toBe(true);
        expect(getFeature(FeatureItem.AllowChangeDataGeographies)).toBe(false);
      });
    });
  });

  describe("IfFeatureEnabled", () => {
    it("renders its children if the given feature is enabled", () => {
      const { getByTestId } = render(
        <IfFeatureEnabled feature={FeatureItem.AllowDBTCloudIntegration}>
          <span data-testid="content" />
        </IfFeatureEnabled>,
        { wrapper }
      );
      expect(getByTestId("content")).toBeTruthy();
    });

    it("does not render its children if the given feature is disabled", () => {
      const { queryByTestId } = render(
        <IfFeatureEnabled feature={FeatureItem.AllowOAuthConnector}>
          <span data-testid="content" />
        </IfFeatureEnabled>,
        { wrapper }
      );
      expect(queryByTestId("content")).toBeFalsy();
    });

    it("allows changing features and rerenders correctly", () => {
      const { queryByTestId, rerender } = render(
        <FeatureService features={[FeatureItem.AllowDBTCloudIntegration]}>
          <IfFeatureEnabled feature={FeatureItem.AllowOAuthConnector}>
            <span data-testid="content" />
          </IfFeatureEnabled>
        </FeatureService>
      );
      expect(queryByTestId("content")).toBeFalsy();
      rerender(
        <FeatureService features={[FeatureItem.AllowOAuthConnector]}>
          <IfFeatureEnabled feature={FeatureItem.AllowOAuthConnector}>
            <span data-testid="content" />
          </IfFeatureEnabled>
        </FeatureService>
      );
      expect(queryByTestId("content")).toBeTruthy();
    });
  });
});
