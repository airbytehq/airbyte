import decimal
from typing import Dict, Any, Type, Optional

# import Percentage as Percentage
import pydantic
from pydantic import BaseModel, Field, Extra
import json
from airbyte_cdk.sources.utils.schema_helpers import expand_refs
from pydantic.types import Decimal


# from airbyte_cdk.sources.utils.schema_models import BaseSchemaModel
class BaseSchemaModel(BaseModel):
    """
    Base class for all schema models. It has some extra schema postprocessing.
    Can be used in combination with AllOptional metaclass
    """

    class Config:
        extra = Extra.allow

        @classmethod
        def schema_extra(cls, schema: Dict[str, Any], model: Type[BaseModel]) -> None:
            """Modify generated jsonschema, remove "title", "description" and "required" fields.

            Pydantic doesn't treat Union[None, Any] type correctly when generate jsonschema,
            so we can't set field as nullable (i.e. field that can have either null and non-null values),
            We generate this jsonschema value manually.

            :param schema: generated jsonschema
            :param model:
            """
            schema.pop("title", None)
            schema.pop("description", None)
            schema.pop("required", None)
            for name, prop in schema.get("properties", {}).items():
                prop.pop("title", None)
                prop.pop("description", None)
                allow_none = model.__fields__[name].allow_none
                if allow_none:
                    if "type" in prop:
                        prop["type"] = ["null", prop["type"]]
                    elif "$ref" in prop:
                        ref = prop.pop("$ref")
                        prop["oneOf"] = [{"type": "null"}, {"$ref": ref}]




class campaign(BaseSchemaModel):
    CTR:Optional[float]=None
    mashupAddToCartClickCVR14d:Optional[float]=None
    ecpvc:Optional[Decimal]=None
    subscriptionButtonViews14d:Optional[int]=None
    widgetLoadCPA14d:Optional[Decimal]=None
    orderBudget:Optional[Decimal]=None
    playTrailers14d:Optional[int]=None
    atc14d:Optional[int]=None
    rentals14d:Optional[int]=None
    addToWatchlist14d:Optional[int]=None
    purchaseRate14d:Optional[float]=None
    brandStoreEngagement1CVR:Optional[float]=None
    videoDownloadsClicks14d:Optional[int]=None
    application14d:Optional[int]=None
    clickOnRedirectCPA14d:Optional[Decimal]=None
    brandStoreEngagement2:Optional[int]=None
    brandStoreEngagement1:Optional[int]=None
    brandStoreEngagement4:Optional[int]=None
    surveyFinishClicks14d:Optional[int]=None
    brandStoreEngagement3:Optional[int]=None
    brandStoreEngagement6:Optional[int]=None
    emailLoad14d:Optional[int]=None
    brandStoreEngagement5:Optional[int]=None
    brandStoreEngagement2Clicks:Optional[int]=None
    mashupBackupImage:Optional[int]=None
    eCPAtc14d:Optional[Decimal]=None
    brandStoreEngagement7:Optional[int]=None
    mashupClickToPageCPA:Optional[Decimal]=None
    brandStoreEngagement3CPA:Optional[Decimal]=None
    storeLocatorPage14d:Optional[int]=None
    invalidImpressions:Optional[int]=None
    grossImpressions:Optional[int]=None
    submitButtonClicks14d:Optional[int]=None
    dropDownSelectionClicks14d:Optional[int]=None
    referralClicks14d:Optional[int]=None
    videoStreamsViews14d:Optional[int]=None
    videoCompletionRate:Optional[float]=None
    registrationForm14d:Optional[int]=None
    bannerInteractionClicks14d:Optional[int]=None
    signUpPageCVR14d:Optional[float]=None
    mashupSubscribeAndSaveCVR14d:Optional[float]=None
    purchaseButtonCVR14d:Optional[float]=None
    brandStoreEngagement6CVR:Optional[float]=None
    videoFirstQuartile:Optional[int]=None
    mashupBackupImageViews:Optional[int]=None
    homepageVisit14d:Optional[int]=None
    eCPDVP14d:Optional[Decimal]=None
    messageSentViews14d:Optional[int]=None
    rentalRate14d:Optional[float]=None
    videoMute:Optional[int]=None
    brandStoreEngagement3Clicks:Optional[int]=None
    mashupClipCouponClickCPA14d:Optional[Decimal]=None
    ecpvd14d:Optional[Decimal]=None
    gameLoadCVR14d:Optional[float]=None
    mashupClickToPageClicks:Optional[int]=None
    mashupAddToCartCPA14d:Optional[Decimal]=None
    newToBrandPurchaseRate14d:Optional[float]=None
    videoStart:Optional[int]=None
    eCPDPV14d:Optional[Decimal]=None
    signUpViews14d:Optional[int]=None
    surveyFinishCVR14d:Optional[float]=None
    mashupBackupImageClicks:Optional[int]=None
    downloadedVideoPlays14d:Optional[int]=None
    emailLoadCPA14d:Optional[Decimal]=None
    atlr14d:Optional[float]=None
    orderName:str
    videoCompletedViews:Optional[int]=None
    mobileAppFirstStarts14d:Optional[int]=None
    submitButtonViews14d:Optional[int]=None
    gameInteraction14d:Optional[int]=None
    applicationCPA14d:Optional[Decimal]=None
    amazonAudienceFee:Optional[Decimal]=None
    videoDownloadRate14d:Optional[float]=None
    subscriptionButtonCPA14d:Optional[Decimal]=None
    widgetLoadClicks14d:Optional[int]=None
    acceptCPA14d:Optional[Decimal]=None
    mashupAddToWishlistClicks14d:Optional[int]=None
    mashupShopNowClickClicks14d:Optional[int]=None
    creativeType:Optional[str]=None
    referralCPA14d:Optional[Decimal]=None
    signUpCVR14d:Optional[float]=None
    successPageViews14d:Optional[int]=None
    homepageVisitCPA14d:Optional[Decimal]=None
    purchasesViews14d:Optional[int]=None
    widgetInteraction14d:Optional[int]=None
    registrationFormClicks14d:Optional[int]=None
    videoComplete:Optional[int]=None
    offAmazonPurchasesClicks14d:Optional[int]=None
    downloadedVideoPlaysClicks14d:Optional[int]=None
    videoPause:Optional[int]=None
    referralCVR14d:Optional[float]=None
    purchaseButtonViews14d:Optional[int]=None
    mashupAddToCartClicks14d:Optional[int]=None
    atcClicks14d:Optional[int]=None
    subscriptionButtonClicks14d:Optional[int]=None
    declineClicks14d:Optional[int]=None
    invalidClickThroughs:Optional[int]=None
    bannerInteractionCVR14d:Optional[float]=None
    surveyStartCVR14d:Optional[float]=None
    dpvr14d:Optional[float]=None
    mashupAddToWishlist14d:Optional[int]=None
    thankYouPage14d:Optional[int]=None
    brandSearchClicks14d:Optional[int]=None
    mashupAddToWishlistCVR14d:Optional[float]=None
    rentalsClicks14d:Optional[int]=None
    subscribe14d:Optional[int]=None
    bannerInteraction14d:Optional[int]=None
    brandStoreEngagement4Clicks:Optional[int]=None
    storeLocatorPageCPA14d:Optional[Decimal]=None
    newSubscribeAndSave14d:Optional[int]=None
    subscriptionButton14d:Optional[int]=None
    widgetInteractionCPA14d:Optional[Decimal]=None
    subscribeViews14d:Optional[int]=None
    applicationCVR14d:Optional[float]=None
    playTrailerRate14d:Optional[float]=None
    brandStoreEngagement6Views:Optional[int]=None
    marketingLandingPageClicks14d:Optional[int]=None
    mashupBackupImageCVR:Optional[float]=None
    offAmazonPurchaseRate14d:Optional[float]=None
    mashupAddToWishlistCPA14d:Optional[Decimal]=None
    orderExternalId:Optional[int]=None
    brandStoreEngagement2CVR:Optional[float]=None
    surveyFinishViews14d:Optional[int]=None
    surveyStartCPA14d:Optional[Decimal]=None
    dropDownSelectionViews14d:Optional[int]=None
    registrationConfirmPageClicks14d:Optional[int]=None
    addToWatchlistCVR14d:Optional[float]=None
    mashupShopNowClickViews14d:Optional[int]=None
    totalCost:Optional[Decimal]=None
    emailInteractionCVR14d:Optional[float]=None
    offAmazonPurchasesViews14d:Optional[int]=None
    addToWatchlistViews14d:Optional[int]=None
    brandStoreEngagement4CPA:Optional[Decimal]=None
    addedToShoppingCartCVR14d:Optional[float]=None
    orderEndDate:Optional[int]=None
    dropDownSelection14d:Optional[int]=None
    brandStoreEngagement1Views:Optional[int]=None
    mashupClipCouponClickCVR14d:Optional[float]=None
    emailLoadCVR14d:Optional[float]=None
    surveyStart14d:Optional[int]=None
    dpvViews14d:Optional[int]=None
    brandStoreEngagement7Clicks:Optional[int]=None
    atlViews14d:Optional[int]=None
    mashupSubscribeAndSaveClick14d:Optional[int]=None
    addedToShoppingCart14d:Optional[int]=None
    newToBrandECPP14d:Optional[Decimal]=None
    eCPM:Optional[Decimal]=None
    messageSentClicks14d:Optional[int]=None
    brandStoreEngagement7CVR:Optional[float]=None
    mobileAppFirstStartsCPA14d:Optional[Decimal]=None
    gameInteractionViews14d:Optional[int]=None
    subscribeClicks14d:Optional[int]=None
    downloadedVideoPlayRate14d:Optional[float]=None
    brandStoreEngagement7Views:Optional[int]=None
    eCPC:Optional[Decimal]=None
    widgetLoad14d:Optional[int]=None
    eCPPT14d:Optional[Decimal]=None
    marketingLandingPageViews14d:Optional[int]=None
    playTrailersViews14d:Optional[int]=None
    offAmazonViews14d:Optional[int]=None
    pRPVViews14d:Optional[int]=None
    videoCompletedCPA:Optional[Decimal]=None
    lineItemStartDate:Optional[int]=None
    newSubscribeAndSaveRate14d:Optional[float]=None
    declineCVR14d:Optional[float]=None
    entityId:Optional[str]=None
    widgetInteractionCVR14d:Optional[float]=None
    mobileAppFirstStartClicks14d:Optional[int]=None
    bannerInteractionViews14d:Optional[int]=None
    creativeID:Optional[int]=None
    newSubscribeAndSaveViews14d:Optional[int]=None
    acceptClicks14d:Optional[int]=None
    addToWatchlistCPA14d:Optional[Decimal]=None
    pRPVClicks14d:Optional[int]=None
    rentalsViews14d:Optional[int]=None
    advertiserTimezone:Optional[str]=None
    storeLocatorPageCVR14d:Optional[float]=None
    storeLocatorPageViews14d:Optional[float]=None
    invalidClickThroughsRate:Optional[float]=None
    homepageVisitCVR14d:Optional[float]=None
    brandStoreEngagement6Clicks:Optional[int]=None
    clickOnRedirectCVR14d:Optional[float]=None
    widgetLoadCVR14d:Optional[float]=None
    signUpCPA14d:Optional[Decimal]=None
    orderId:Optional[int]=None
    applicationClicks14d:Optional[int]=None
    lineItemName:Optional[str]=None
    mashupAddToCart14d:Optional[int]=None
    submitButton14d:Optional[int]=None
    brandStoreEngagement5Clicks:Optional[int]=None
    clickOnRedirectClicks14d:Optional[int]=None
    grossClickThroughs:Optional[int]=None
    eCPVS14d:Optional[Decimal]=None
    purchasesClicks14d:Optional[int]=None
    emailLoadClicks14d:Optional[int]=None
    brandStoreEngagement6CPA:Optional[Decimal]=None
    videoDownloadsViews14d:Optional[int]=None
    pRPV14d:Optional[int]=None
    thankYouPageCPA14d:Optional[Decimal]=None
    thankYouPageClicks14d:Optional[int]=None
    purchaseButtonCPA14d:Optional[Decimal]=None
    emailLoadViews14d:Optional[int]=None
    gameLoadViews14d:Optional[int]=None
    amazonPlatformFee:Optional[Decimal]=None
    registrationFormCVR14d:Optional[float]=None
    signUpPageCPA14d:Optional[Decimal]=None
    declineCPA14d:Optional[Decimal]=None
    videoStartedCVR:Optional[float]=None
    messageSent14d:Optional[int]=None
    creativeAdId:Optional[int]=None
    mashupClipCouponClick14d:Optional[int]=None
    creativeName:Optional[str]=None
    widgetInteractionViews14d:Optional[int]=None
    homepageVisitViews14d:Optional[int]=None
    videoStartedClicks:Optional[int]=None
    dpvClicks14d:Optional[int]=None
    videoResume:Optional[int]=None
    playerTrailersClicks14d:Optional[int]=None
    clickOnRedirect14d:Optional[int]=None
    emailInteractionClicks14d:Optional[int]=None
    emailInteractionViews14d:Optional[int]=None
    registrationConfirmPageCVR14d:Optional[float]=None
    signUp14d:Optional[int]=None
    downloadedVideoPlaysViews14d:Optional[int]=None
    acceptCVR14d:Optional[float]=None
    surveyFinish14d:Optional[int]=None
    surveyFinishCPA14d:Optional[Decimal]=None
    purchaseButtonClicks14d:Optional[int]=None
    clickThroughs:Optional[int]=None
    addedToShoppingCartClicks14d:Optional[int]=None
    signUpPageClicks14d:Optional[int]=None
    mashupAddToWishlistViews14d:Optional[int]=None
    brandSearchCPA14d:Optional[Decimal]=None
    mashupClickToPageViews:Optional[int]=None
    videoCompleted:Optional[int]=None
    videoStreamsRate14d:Optional[float]=None
    mobileAppFirstStartCVR14d:Optional[float]=None
    eCPP14d:Optional[Decimal]=None
    newSubscribeAndSaveClicks14d:Optional[int]=None
    mashupClipCouponClickClicks14d:Optional[int]=None
    mashupSubscribeAndSave14d:Optional[int]=None
    referralViews14d:Optional[int]=None
    addedToShoppingCartCPA14d:Optional[Decimal]=None
    offAmazonClicks14d:Optional[int]=None
    brandStoreEngagement3CVR:Optional[float]=None
    submitButtonCPA14d:Optional[Decimal]=None
    accept14d:Optional[int]=None
    videoStreamsClicks14d:Optional[int]=None
    brandStoreEngagement5CPA:Optional[Decimal]=None
    videoEndClicks:Optional[int]=None
    lineItemId:Optional[int]=None
    referral14d:Optional[int]=None
    widgetInteractionClicks14d:Optional[int]=None
    impressions:Optional[int]=None
    advertiserId:Optional[int]=None
    acceptViews14d:Optional[int]=None
    bannerInteractionCPA14d:Optional[Decimal]=None
    brandStoreEngagement2Views:Optional[int]=None
    atl14d:Optional[int]=None
    signUpPageViews14d:Optional[int]=None
    mashupClickToPageCVR:Optional[float]=None
    atlClicks14d:Optional[int]=None
    mashupSubscribeAndSaveCPA14d:Optional[Decimal]=None
    brandStoreEngagement5Views:Optional[int]=None
    newToBrandPurchasesClicks14d:Optional[int]=None
    marketingLandingPage14d:Optional[int]=None
    signUpClicks14d:Optional[int]=None
    offAmazonCVR14d:Optional[float]=None
    mobileAppFirstStartViews14d:Optional[int]=None
    date:Optional[int]=None
    signUpPage14d:Optional[int]=None
    eCPnewSubscribeAndSave14d:Optional[Decimal]=None
    applicationViews14d:Optional[int]=None
    brandStoreEngagement4Views:Optional[int]=None
    newToBrandPurchases14d:Optional[int]=None
    messageSentCPA14d:Optional[Decimal]=None
    messageSentCVR14d:Optional[float]=None
    mashupAddToCartViews14d:Optional[int]=None
    videoMidpoint:Optional[int]=None
    emailInteractionCPA14d:Optional[Decimal]=None
    subscribeCPA14d:Optional[Decimal]=None
    offAmazonPurchases14d:Optional[int]=None
    brandStoreEngagement2CPA:Optional[Decimal]=None
    storeLocatorPageClicks14d:Optional[int]=None
    mashupSubscribeAndSaveClickViews14d:Optional[int]=None
    gameLoadClicks14d:Optional[int]=None
    videoStartedViews:Optional[int]=None
    thankYouPageViews14d:Optional[int]=None
    marketingLandingPageCVR14d:Optional[float]=None
    subscribeCVR14d:Optional[float]=None
    marketingLandingPageCPA14d:Optional[Decimal]=None
    videoStreams14d:Optional[int]=None
    mashupBackupImageCPA:Optional[Decimal]=None
    brandStoreEngagement5CVR:Optional[float]=None
    widgetLoadViews14d:Optional[int]=None
    dropDownSelectionCPA14d:Optional[Decimal]=None
    successPageCPA14d:Optional[Decimal]=None
    ecpr14d:Optional[Decimal]=None
    lineItemBudget:Optional[Decimal]=None
    subscriptionButtonCVR14d:Optional[float]=None
    videoStarted:Optional[int]=None
    orderCurrency:str
    surveyStartClicks14d:Optional[int]=None
    decline14d:Optional[int]=None
    videoCompletedCVR:Optional[float]=None
    atcr14d:Optional[float]=None
    gameInteractionClicks14d:Optional[int]=None
    creativeSize:Optional[str]=None
    clickOnRedirectViews14d:Optional[int]=None
    lineItemEndDate:Optional[int]=None
    invalidImpressionRate:Optional[float]=None
    brandStoreEngagement3Views:Optional[int]=None
    brandStoreEngagement7CPA:Optional[Decimal]=None
    gameInteractionCPA14d:Optional[Decimal]=None
    videoUnmute:Optional[int]=None
    brandSearchViews14d:Optional[int]=None
    gameLoad14d:Optional[int]=None
    atcViews14d:Optional[int]=None
    brandStoreEngagement1Clicks:Optional[int]=None
    registrationConfirmPageViews14d:Optional[int]=None
    surveyStartViews14d:Optional[int]=None
    addedToShoppingCartViews14d:Optional[int]=None
    mashupShopNowClickCPA14d:Optional[Decimal]=None
    brandSearch14d:Optional[int]=None
    mashupClickToPage:Optional[int]=None
    addToWatchlistClicks14d:Optional[int]=None
    lineItemExternalId:Optional[str]=None
    supplyCost:Optional[Decimal]=None
    submitButtonCVR14d:Optional[float]=None
    offAmazonCPA14d:Optional[Decimal]=None
    videoStartedCPA:Optional[Decimal]=None
    advertiserName:str
    videoThirdQuartile:Optional[int]=None
    successPageClicks14d:Optional[int]=None
    registrationConfirmPageCPA14d:Optional[Decimal]=None
    mashupShopNowClickCVR14d:Optional[float]=None
    registrationConfirmPage14d:Optional[int]=None
    mashupClipCouponClickViews14d:Optional[int]=None
    brandSearchRate14d:Optional[float]=None
    declineViews14d:Optional[int]=None
    orderStartDate:Optional[int]=None
    advertiserCountry:str
    dropDownSelectionCVR14d:Optional[float]=None
    pRPVr14d:Optional[float]=None
    homepageVisitClicks14d:Optional[int]=None
    mashupShopNowClick14d:Optional[int]=None
    registrationFormCPA14d:Optional[Decimal]=None
    offAmazonECPP14d:Optional[Decimal]=None
    offAmazonConversions14d:Optional[int]=None
    videoDownloads14d:Optional[int]=None
    eCPPRPV14d:Optional[Decimal]=None
    emailInteraction14d:Optional[int]=None
    registrationFormViews14d:Optional[int]=None
    brandStoreEngagement1CPA:Optional[Decimal]=None
    successPageCVR14d:Optional[float]=None
    purchases14d:Optional[int]=None
    gameLoadCPA14d:Optional[Decimal]=None
    percentOfPurchasesNewToBrand14d:Optional[float]=None
    dpv14d:Optional[int]=None
    purchaseButton14d:Optional[int]=None
    newToBrandPurchasesViews14d:Optional[int]=None
    successPage14d:Optional[int]=None
    gameInteractionCVR14d:Optional[float]=None
    eCPAtl14d:Optional[Decimal]=None
    thankYouPageCVR14d:Optional[float]=None
    brandStoreEngagement4CVR:Optional[float]=None


