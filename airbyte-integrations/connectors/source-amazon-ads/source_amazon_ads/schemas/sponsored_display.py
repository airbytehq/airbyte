#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from decimal import Decimal
from typing import Dict, List, Optional

from .common import CatalogModel, Targeting


class DisplayCampaign(CatalogModel):
    campaignId: Decimal
    name: str
    budgetType: str
    budget: Decimal
    startDate: str
    endDate: str = None
    costType: str
    state: str
    portfolioId: int = None
    tactic: str
    deliveryProfile: str


class DisplayAdGroup(CatalogModel):
    name: str
    campaignId: Decimal
    adGroupId: Decimal
    defaultBid: Decimal
    bidOptimization: str
    state: str
    tactic: str
    creativeType: str


class DisplayProductAds(CatalogModel):
    state: str
    adId: Decimal
    campaignId: Decimal
    adGroupId: Decimal
    asin: str
    sku: str


class DisplayTargeting(Targeting):
    campaignId: Decimal
    expression: List[Dict[str, str]]
    resolvedExpression: List[Dict[str, str]]


class DisplayCreativesHeadlineCreativeProperties(CatalogModel):
    headline: Optional[str] = None


class DisplayCreativesCreativePropertiesCroppingCoordinates(CatalogModel):
    top: Decimal
    left: Decimal
    width: Decimal
    height: Decimal


class DisplayCreativesLogoCustomImageCreativeProperties(CatalogModel):
    assetId: str
    assetVersion: str
    croppingCoordinates: Optional[DisplayCreativesCreativePropertiesCroppingCoordinates] = None


class DisplayCreativesLogoCreativeProperties(CatalogModel):
    brandLogo: Optional[DisplayCreativesLogoCustomImageCreativeProperties] = None


class DisplayCreativesCustomImageCreativeProperties(CatalogModel):
    rectCustomImage: Optional[DisplayCreativesLogoCustomImageCreativeProperties] = None
    squareCustomImage: Optional[DisplayCreativesLogoCustomImageCreativeProperties] = None


class DisplayCreativesVideoCreativePropertiesVideo(CatalogModel):
    assetId: str
    assetVersion: str


class DisplayCreativesVideoCreativeProperties(CatalogModel):
    video: Optional[DisplayCreativesVideoCreativePropertiesVideo] = None


class DisplayCreativesProperties(CatalogModel):
    HeadlineCreativeProperties: Optional[Dict[str, str]] = None
    LogoCreativeProperties: Optional[DisplayCreativesLogoCreativeProperties] = None
    CustomImageCreativeProperties: Optional[DisplayCreativesCustomImageCreativeProperties] = None
    VideoCreativeProperties: Optional[DisplayCreativesVideoCreativeProperties] = None


class DisplayCreatives(CatalogModel):
    adGroupId: Decimal
    creativeId: Decimal
    creativeType: str
    properties: Optional[DisplayCreativesProperties] = None
    moderationStatus: str


class DisplayBudgetRuleDetailsPerformanceMeasureCondition(CatalogModel):
    metricName: str
    comparisonOperator: str
    threshold: Decimal


class DisplayBudgetRuleDetailsRecurrence(CatalogModel):
    type: str
    daysOfWeek: List[str] = None
    threshold: Decimal


class DisplayBudgetRuleDetailsBudgetIncreaseBy(CatalogModel):
    type: str
    value: Decimal


class DisplayBudgetRuleDetailsDurationEventTypeRuleDuration(CatalogModel):
    eventId: str
    endDate: str
    eventName: str
    startDate: str


class DisplayBudgetRuleDetailsDurationDateRangeTypeRuleDuration(CatalogModel):
    endDate: Optional[str]
    startDate: str


class DisplayBudgetRuleDetailsDuration(CatalogModel):
    eventTypeRuleDuration: Optional[DisplayBudgetRuleDetailsDurationEventTypeRuleDuration] = None
    dateRangeTypeRuleDuration: Optional[DisplayBudgetRuleDetailsDurationDateRangeTypeRuleDuration] = None


class DisplayBudgetRuleDetails(CatalogModel):
    name: str
    ruleType: str = None
    duration: Optional[DisplayBudgetRuleDetailsDuration] = None
    budgetIncreaseBy: Optional[DisplayBudgetRuleDetailsBudgetIncreaseBy] = None
    recurrence: Optional[DisplayBudgetRuleDetailsRecurrence] = None
    performanceMeasureCondition: Optional[DisplayBudgetRuleDetailsPerformanceMeasureCondition] = None


class DisplayBudgetRules(CatalogModel):
    ruleId: str
    ruleStatus: str
    ruleState: str
    lastUpdatedDate: Optional[Decimal]
    createdDate: Decimal
    ruleDetails: DisplayBudgetRuleDetails = None
    ruleStatusDetails: Dict[str, str] = None
