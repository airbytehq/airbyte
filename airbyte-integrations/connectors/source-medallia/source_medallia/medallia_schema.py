import sgqlc.types
import sgqlc.types.datetime
import sgqlc.types.relay


medallia_schema = sgqlc.types.Schema()


# Unexport Node/PageInfo, let schema re-declare them
medallia_schema -= sgqlc.types.relay.Node
medallia_schema -= sgqlc.types.relay.PageInfo


__docformat__ = 'markdown'


########################################################################
# Scalars and Enumerations
########################################################################
class ActionPlanFilterField(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `CREATOR`
    * `OWNER`
    * `UNIT`
    * `STATUS`
    * `CREATION_DATE`
    * `RULE_TOPIC`
    * `DATA_TOPIC`
    * `AGGREGATED_ACTION`
    * `DRIVER`
    * `SURVEY_ID`
    * `UNIT_GROUP`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AGGREGATED_ACTION', 'CREATION_DATE', 'CREATOR', 'DATA_TOPIC', 'DRIVER', 'OWNER', 'RULE_TOPIC', 'STATUS', 'SURVEY_ID', 'UNIT', 'UNIT_GROUP')


class ActionPlanOrderProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `TITLE`
    * `CREATION_DATE`
    * `STATUS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CREATION_DATE', 'STATUS', 'TITLE')


class ActionPlanStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `APPROVED`
    * `IN_PROGRESS`
    * `COMPLETED`
    * `CANCELLED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'CANCELLED', 'COMPLETED', 'IN_PROGRESS')


class ActionPlanTaskOrderProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NAME`
    * `DUE_DATE`
    * `LAST_UPDATE_DATE`
    * `COMPLETION_DATE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COMPLETION_DATE', 'DUE_DATE', 'LAST_UPDATE_DATE', 'NAME')


class ActionPlanUserQualifier(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `EMAIL`
    * `USER_ID`
    * `PRIMARY_ROLE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('EMAIL', 'PRIMARY_ROLE', 'USER_ID')


class ActivitySource(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `SOCIAL`
    * `RESPONSE`
    * `NOTE`
    * `ALERT`
    * `SUBSCRIPTION`
    * `OTHER`
    * `ATTACHMENT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ALERT', 'ATTACHMENT', 'NOTE', 'OTHER', 'RESPONSE', 'SOCIAL', 'SUBSCRIPTION')


class ActivityType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `IN_QUEUE`
    * `DELIVERED`
    * `FAILED`
    * `DISABLED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('DELIVERED', 'DISABLED', 'FAILED', 'IN_QUEUE')


class AggregateDefinitionScalar(sgqlc.types.Scalar):
    __schema__ = medallia_schema


class AggregateRankSortFieldBy(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `LABEL`
    * `KEY`
    '''
    __schema__ = medallia_schema
    __choices__ = ('KEY', 'LABEL')


class AggregatedActionVisibility(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `HIDDEN`
    * `SHOWN`
    '''
    __schema__ = medallia_schema
    __choices__ = ('HIDDEN', 'SHOWN')


class AggregatedActionsProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `DATE_CREATED`
    * `SUGGESTIONS_COUNT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('DATE_CREATED', 'SUGGESTIONS_COUNT')


class AggregationTableLayoutSubAxis(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ROWS`
    * `COLUMNS`
    * `VALUES`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COLUMNS', 'ROWS', 'VALUES')


class AggregationTableTASplitAxisTopicRole(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `MAIN`
    * `COOCCURRING`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COOCCURRING', 'MAIN')


class ApplicationTarget(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `WEB`
    * `MOBILE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('MOBILE', 'WEB')


class ApplicationTypeEnum(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `EXPERIENCE_PROGRAMS`
    * `AD_HOC`
    * `EMPLOYEE_PROGRAMS`
    * `ACTION_PLANS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ACTION_PLANS', 'AD_HOC', 'EMPLOYEE_PROGRAMS', 'EXPERIENCE_PROGRAMS')


class AskNowAttribute(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `STARTDATE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('STARTDATE',)


class AskNowTestStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ACTIVE`
    * `INACTIVE`
    * `DRAFT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ACTIVE', 'DRAFT', 'INACTIVE')


class AskNowTestVersion(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `V_2`
    * `V_3`
    '''
    __schema__ = medallia_schema
    __choices__ = ('V_2', 'V_3')


class AssessmentEventType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `AUTO_RELEASED`
    * `SUBMITTED`
    * `SAVED`
    * `RELEASED`
    * `ASSESSMENT_ACKNOWLEDGED`
    * `COMMENT_ACKNOWLEDGED`
    * `AUTO_SUBMITTED`
    * `PENDING_APPROVAL`
    * `APPROVED`
    * `REJECTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'ASSESSMENT_ACKNOWLEDGED', 'AUTO_RELEASED', 'AUTO_SUBMITTED', 'COMMENT_ACKNOWLEDGED', 'PENDING_APPROVAL', 'REJECTED', 'RELEASED', 'SAVED', 'SUBMITTED')


class AssessmentStageType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `SELF_ASSESSMENT`
    * `MANAGER_ASSESSMENT`
    * `PERFORMANCE_RATING`
    * `RELEASE_MANAGER_ASSESSMENT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('MANAGER_ASSESSMENT', 'PERFORMANCE_RATING', 'RELEASE_MANAGER_ASSESSMENT', 'SELF_ASSESSMENT')


class AssessmentWaveParticipationProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `EMPLOYEE_NAME`
    * `SELF_ASSESSMENT_STATUS`
    * `MANAGER_ASSESSMENT_STATUS`
    * `MANAGER_PERFORMANCE_RATING`
    * `MANAGER_NAME`
    '''
    __schema__ = medallia_schema
    __choices__ = ('EMPLOYEE_NAME', 'MANAGER_ASSESSMENT_STATUS', 'MANAGER_NAME', 'MANAGER_PERFORMANCE_RATING', 'SELF_ASSESSMENT_STATUS')


class AsyncTaskOrderProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `CREATOR`
    * `TASK_TYPE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CREATOR', 'TASK_TYPE')


class AsyncTaskType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `FEEDBACK_EXPORT`
    * `INVITATIONS_EXPORT`
    * `STATS_EXPORT`
    * `AGGREGATION_TABLE_EXPORT`
    * `AGGREGATION_TABLE_LIST_EXPORT`
    * `PHRASES_EXPORT`
    * `CONTACT_SEGMENT_EXPORT`
    * `REPORT_EXPORT`
    * `PERSONALIZED_ALERT`
    * `FORWARD_RESPONSE`
    * `NEW_RESPONSES`
    * `DATASET_EXPORT`
    * `XSTATS_WORKBENCH`
    * `DESCRIBE_XSTATS_ANALYSIS`
    * `CORRELATION_XSTATS_ANALYSIS`
    * `REGRESSION_XSTATS_ANALYSIS`
    * `MEDALLIA_BENCHMARKS_EXPORT_UPLOAD`
    * `MEDALLIA_BENCHMARKS_EXPORT_PREVIEW`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AGGREGATION_TABLE_EXPORT', 'AGGREGATION_TABLE_LIST_EXPORT', 'CONTACT_SEGMENT_EXPORT', 'CORRELATION_XSTATS_ANALYSIS', 'DATASET_EXPORT', 'DESCRIBE_XSTATS_ANALYSIS', 'FEEDBACK_EXPORT', 'FORWARD_RESPONSE', 'INVITATIONS_EXPORT', 'MEDALLIA_BENCHMARKS_EXPORT_PREVIEW', 'MEDALLIA_BENCHMARKS_EXPORT_UPLOAD', 'NEW_RESPONSES', 'PERSONALIZED_ALERT', 'PHRASES_EXPORT', 'REGRESSION_XSTATS_ANALYSIS', 'REPORT_EXPORT', 'STATS_EXPORT', 'XSTATS_WORKBENCH')


class Axis(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `COLUMNS`
    * `ROWS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COLUMNS', 'ROWS')


Boolean = sgqlc.types.Boolean

class CaseStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `COMPLETED`
    * `INCOMPLETE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COMPLETED', 'INCOMPLETE')


class CellStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NO_SAMPLES`
    * `HIDDEN`
    * `AVAILABLE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AVAILABLE', 'HIDDEN', 'NO_SAMPLES')


class ClosedLoopMessageValidationError(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `MESSAGE_CONTENT_INCOMPLETE_PLACEHOLDERS`
    * `CONVERSATION_THREAD_UNAVAILABLE`
    * `PARTICIPANT_OPTED_OUT`
    * `BLACKOUT_DATE`
    * `OTHER_ACTIVE_CONVERSATION`
    '''
    __schema__ = medallia_schema
    __choices__ = ('BLACKOUT_DATE', 'CONVERSATION_THREAD_UNAVAILABLE', 'MESSAGE_CONTENT_INCOMPLETE_PLACEHOLDERS', 'OTHER_ACTIVE_CONVERSATION', 'PARTICIPANT_OPTED_OUT')


class ClosedLoopThreadStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_OPEN`
    * `OPEN`
    * `CLOSED`
    * `EXPIRED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CLOSED', 'EXPIRED', 'NOT_OPEN', 'OPEN')


class CommentTaggingsStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `TAGGING_PENDING`
    * `TAGGED`
    * `TAGGING_FAILED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('TAGGED', 'TAGGING_FAILED', 'TAGGING_PENDING')


class ContactSegmentAction(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `RUN`
    * `CANCEL`
    * `RESTART`
    * `REFRESH`
    * `DELETE_DATA`
    * `DELETE`
    * `START_EXPORT`
    * `CANCEL_EXPORT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CANCEL', 'CANCEL_EXPORT', 'DELETE', 'DELETE_DATA', 'REFRESH', 'RESTART', 'RUN', 'START_EXPORT')


class ContactSegmentOrderProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NAME`
    * `LAST_EXECUTION_TIME`
    '''
    __schema__ = medallia_schema
    __choices__ = ('LAST_EXECUTION_TIME', 'NAME')


class ContactSegmentStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `DEFINED`
    * `BUILDING`
    * `REFRESHING`
    * `READY`
    * `EXPORTING`
    * `FAILED`
    * `CANCELLING`
    '''
    __schema__ = medallia_schema
    __choices__ = ('BUILDING', 'CANCELLING', 'DEFINED', 'EXPORTING', 'FAILED', 'READY', 'REFRESHING')


class ContactSegmentType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `STANDARD`
    * `CUSTOM`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CUSTOM', 'STANDARD')


class ContactSortableAttribute(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `LASTNAME`
    * `FIRSTNAME`
    '''
    __schema__ = medallia_schema
    __choices__ = ('FIRSTNAME', 'LASTNAME')


class ConversationMode(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `FEEDBACK_CAPTURE`
    * `CLOSED_LOOP`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CLOSED_LOOP', 'FEEDBACK_CAPTURE')


class CustomerEffortTaggingCategory(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `HIGH`
    * `NEUTRAL`
    * `LOW`
    '''
    __schema__ = medallia_schema
    __choices__ = ('HIGH', 'LOW', 'NEUTRAL')


class DataSource(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `FEEDBACK`
    * `INVITATIONS`
    * `SSO_EVENT_STATS`
    * `SURVEY_EXPORT_STATS`
    * `USER_ACTIVITIES`
    * `FEED_FILES`
    * `FEEDBACK_AND_USER_ACTIVITIES`
    * `ACTION_PLANS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ACTION_PLANS', 'FEEDBACK', 'FEEDBACK_AND_USER_ACTIVITIES', 'FEED_FILES', 'INVITATIONS', 'SSO_EVENT_STATS', 'SURVEY_EXPORT_STATS', 'USER_ACTIVITIES')


class DataType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `DATE`
    * `TIME`
    * `DATETIME`
    * `EMAIL`
    * `ENUM`
    * `FLOAT`
    * `INT`
    * `BOOLEAN`
    * `STRING`
    * `UNIT`
    * `UNIT_GROUP`
    * `URL`
    * `COMMENT`
    * `NO_DATA`
    '''
    __schema__ = medallia_schema
    __choices__ = ('BOOLEAN', 'COMMENT', 'DATE', 'DATETIME', 'EMAIL', 'ENUM', 'FLOAT', 'INT', 'NO_DATA', 'STRING', 'TIME', 'UNIT', 'UNIT_GROUP', 'URL')


Date = sgqlc.types.datetime.Date

DateTime = sgqlc.types.datetime.DateTime

class DayOfWeek(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `MONDAY`
    * `TUESDAY`
    * `WEDNESDAY`
    * `THURSDAY`
    * `FRIDAY`
    * `SATURDAY`
    * `SUNDAY`
    '''
    __schema__ = medallia_schema
    __choices__ = ('FRIDAY', 'MONDAY', 'SATURDAY', 'SUNDAY', 'THURSDAY', 'TUESDAY', 'WEDNESDAY')


class DeliveryType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `SENT`
    * `DELIVERY_FAILED`
    * `DELIVERED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('DELIVERED', 'DELIVERY_FAILED', 'SENT')


class DeltaCalculation(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `INCREMENT`
    * `PROPORTION`
    * `PROPORTION_INCREMENT`
    * `PERCENTAGE`
    * `PERCENTAGE_INCREMENT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('INCREMENT', 'PERCENTAGE', 'PERCENTAGE_INCREMENT', 'PROPORTION', 'PROPORTION_INCREMENT')


class E360AssignedRaterOrderProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `RATER_NAME`
    * `RATER_RELATIONSHIP_NAME`
    * `ADDED_BY`
    * `RATER_EMAIL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ADDED_BY', 'RATER_EMAIL', 'RATER_NAME', 'RATER_RELATIONSHIP_NAME')


class E360EnrollmentDecision(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `APPROVED`
    * `REJECTED`
    * `CANCELED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'CANCELED', 'REJECTED')


class E360FeedbackPerRaterRelationshipProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `RATER_RELATIONSHIP_HIERARCHY`
    '''
    __schema__ = medallia_schema
    __choices__ = ('RATER_RELATIONSHIP_HIERARCHY',)


class E360FeedbackQuestionScoreProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `QUESTION_OVERALL_SCORE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('QUESTION_OVERALL_SCORE',)


class E360FeedbackRaterAssignmentAction(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ADD`
    * `UPDATE`
    * `REMOVE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ADD', 'REMOVE', 'UPDATE')


class E360FeedbackRaterAssignmentDecision(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `APPROVED`
    * `REJECTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'REJECTED')


class E360FeedbackRaterAssignmentErrorType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `BLOCKED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('BLOCKED',)


class E360FeedbackRequestOrderProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `EMPLOYEE_NAME`
    * `REVIEW_NAME`
    * `DUE_DATE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('DUE_DATE', 'EMPLOYEE_NAME', 'REVIEW_NAME')


class E360FeedbackStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_STARTED`
    * `STARTED`
    * `COMPLETED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COMPLETED', 'NOT_STARTED', 'STARTED')


class E360FeedbackWaveParticipationProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `EMPLOYEE_NAME`
    * `REVIEW_NAME`
    * `WAVE_NAME`
    * `WAVE_START_DATE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('EMPLOYEE_NAME', 'REVIEW_NAME', 'WAVE_NAME', 'WAVE_START_DATE')


class E360FeedbackWaveReportStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `AVAILABLE`
    * `UNAVAILABLE`
    * `INSUFFICIENT_RATINGS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AVAILABLE', 'INSUFFICIENT_RATINGS', 'UNAVAILABLE')


class E360RaterStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `DRAFT`
    * `PENDING_REVIEW`
    * `APPROVED`
    * `REJECTED`
    * `NEEDS_RATER_RELATIONSHIP`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'DRAFT', 'NEEDS_RATER_RELATIONSHIP', 'PENDING_REVIEW', 'REJECTED')


class E360ReviewRaterRelationshipCardinality(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ONE_TO_ONE`
    * `ONE_TO_MANY`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ONE_TO_MANY', 'ONE_TO_ONE')


class E360ReviewReportType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ORIGINAL_RATINGS`
    * `QUARTILE`
    * `LMO`
    '''
    __schema__ = medallia_schema
    __choices__ = ('LMO', 'ORIGINAL_RATINGS', 'QUARTILE')


class E360WaveEnrollmentAction(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ENROLL`
    * `UNENROLL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ENROLL', 'UNENROLL')


class EmotionTrend(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `IMPROVING`
    * `SIMILAR`
    * `WORSENING`
    * `TOO_SHORT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('IMPROVING', 'SIMILAR', 'TOO_SHORT', 'WORSENING')


class EmployeeProgramReportCombinationMode(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `PARTICIPATION`
    * `EMPLOYEE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('EMPLOYEE', 'PARTICIPATION')


class EmployeeProgramReportType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `GOALS_PARTICIPATION`
    * `ASSESSMENTS_PARTICIPATION`
    * `E360_PARTICIPATION`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ASSESSMENTS_PARTICIPATION', 'E360_PARTICIPATION', 'GOALS_PARTICIPATION')


class EmployeeProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NAME`
    * `MANAGER_NAME`
    '''
    __schema__ = medallia_schema
    __choices__ = ('MANAGER_NAME', 'NAME')


class Encoding(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `BIG5_HKSCS`
    * `CESU_8`
    * `IBM00858`
    * `ISO_8859_1`
    * `ISO_8859_15`
    * `ISO_8859_2`
    * `US_ASCII`
    * `UTF_8`
    * `UTF_16`
    * `UTF_32`
    * `UTF_16LE`
    * `WINDOWS_1250`
    * `WINDOWS_1251`
    * `WINDOWS_1252`
    * `X_UTF_16LE_BOM`
    * `X_UTF_32LE_BOM`
    '''
    __schema__ = medallia_schema
    __choices__ = ('BIG5_HKSCS', 'CESU_8', 'IBM00858', 'ISO_8859_1', 'ISO_8859_15', 'ISO_8859_2', 'US_ASCII', 'UTF_16', 'UTF_16LE', 'UTF_32', 'UTF_8', 'WINDOWS_1250', 'WINDOWS_1251', 'WINDOWS_1252', 'X_UTF_16LE_BOM', 'X_UTF_32LE_BOM')


class EnrollmentStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ENROLLED`
    * `NOT_ENROLLED`
    * `PENDING_APPROVAL`
    * `REJECTED`
    * `INCOMPLETE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ENROLLED', 'INCOMPLETE', 'NOT_ENROLLED', 'PENDING_APPROVAL', 'REJECTED')


class EnumeratedAltSetFormat(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NAME`
    * `NUMERIC`
    * `SEQUENCE_NUMBER`
    * `NUMERIC_OR_SEQUENCE_NUMBER`
    * `NUMERIC_OR_NAME`
    * `EXPORT_VALUE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('EXPORT_VALUE', 'NAME', 'NUMERIC', 'NUMERIC_OR_NAME', 'NUMERIC_OR_SEQUENCE_NUMBER', 'SEQUENCE_NUMBER')


class EventConditionOutput(sgqlc.types.Scalar):
    __schema__ = medallia_schema


class EventTypeKey(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `EVENT`
    * `AIRLINE_ARRIVAL`
    * `AIRLINE_BOOKING`
    * `AIRLINE_CALL_CENTER_SUPPORT`
    * `AIRLINE_CASE_CLOSED`
    * `AIRLINE_CASE_OPENED`
    * `AIRLINE_CHAT_SUPPORT`
    * `AIRLINE_CHECKIN`
    * `AIRLINE_DEPARTURE`
    * `AIRLINE_IN_FLIGHT`
    * `AIRLINE_MOBILE_EVENT`
    * `AIRLINE_WEBSITE_EVENT`
    * `AIRLINE_WEBSITE_VISIT`
    * `BANKING_ACCOUNT_CLOSED`
    * `BANKING_ACCOUNT_FUNDED`
    * `BANKING_ACCOUNT_OPENED`
    * `BANKING_ATM_TRANSACTION`
    * `BANKING_BRANCH_TRANSACTION`
    * `BANKING_CALL_CENTER_SUPPORT`
    * `BANKING_CASE_CLOSED`
    * `BANKING_CASE_OPENED`
    * `BANKING_CHAT_SUPPORT`
    * `BANKING_CREDIT_CARD_APPROVAL_DECISION`
    * `BANKING_CREDIT_CARD_APPLICATION`
    * `BANKING_FRAUD_INCIDENT`
    * `BANKING_MOBILE_EVENT`
    * `BANKING_MORTGAGE_EVENT`
    * `BANKING_MORTGAGE_OR_LOAN_APPLICATION`
    * `BANKING_MORTGAGE_OR_LOAN_CLOSING`
    * `BANKING_MORTGAGE_OR_LOAN_DECISION`
    * `BANKING_MORTGAGE_PRE_APPROVED`
    * `BANKING_WEBSITE_EVENT`
    * `BANKING_WEBSITE_VISIT`
    * `HOSPITALITY_BOOKING`
    * `HOSPITALITY_CALL_CENTER_SUPPORT`
    * `HOSPITALITY_CASE_CLOSED`
    * `HOSPITALITY_CASE_OPENED`
    * `HOSPITALITY_CHAT_SUPPORT`
    * `HOSPITALITY_CHECK_IN`
    * `HOSPITALITY_CHECK_OUT`
    * `HOSPITALITY_COMPLAINT_FILED`
    * `HOSPITALITY_FOOD_OR_DINING_EVENT`
    * `HOSPITALITY_MARKETING_EVENT`
    * `HOSPITALITY_MOBILE_EVENT`
    * `HOSPITALITY_ROOM_SERVICE`
    * `HOSPITALITY_WEBSITE_EVENT`
    * `INSURANCE_ACCOUNT_CLOSED`
    * `INSURANCE_ACCOUNT_OPENED`
    * `INSURANCE_CALL_CENTER_SUPPORT`
    * `INSURANCE_CASE_CLOSED`
    * `INSURANCE_CASE_OPENED`
    * `INSURANCE_CHAT_SUPPORT`
    * `INSURANCE_CLAIM_DENIED`
    * `INSURANCE_COMPLAINT_FILED`
    * `INSURANCE_DISPUTE`
    * `INSURANCE_FIRST_NOTICE_OF_LOSS`
    * `INSURANCE_MOBILE_EVENT`
    * `INSURANCE_WEBSITE_EVENT`
    * `RETAIL_CALL_CENTER_SUPPORT`
    * `RETAIL_CASE_CLOSED`
    * `RETAIL_CASE_OPENED`
    * `RETAIL_CHAT_SUPPORT`
    * `RETAIL_EDUCATION_EVENT`
    * `RETAIL_EXCHANGE`
    * `RETAIL_INSTALLATION_COMPLETED`
    * `RETAIL_INSTALLATION_STARTED`
    * `RETAIL_MOBILE_EVENT`
    * `RETAIL_PRODUCT_DELIVERED`
    * `RETAIL_PRODUCT_SHIPPED`
    * `RETAIL_PURCHASE_IN_STORE`
    * `RETAIL_PURCHASE_ONLINE`
    * `RETAIL_PURCHASE_OVER_PHONE`
    * `RETAIL_SERVICE_COMPLETED`
    * `RETAIL_WEBSITE_EVENT`
    * `RETAIL_WEBSITE_VISIT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AIRLINE_ARRIVAL', 'AIRLINE_BOOKING', 'AIRLINE_CALL_CENTER_SUPPORT', 'AIRLINE_CASE_CLOSED', 'AIRLINE_CASE_OPENED', 'AIRLINE_CHAT_SUPPORT', 'AIRLINE_CHECKIN', 'AIRLINE_DEPARTURE', 'AIRLINE_IN_FLIGHT', 'AIRLINE_MOBILE_EVENT', 'AIRLINE_WEBSITE_EVENT', 'AIRLINE_WEBSITE_VISIT', 'BANKING_ACCOUNT_CLOSED', 'BANKING_ACCOUNT_FUNDED', 'BANKING_ACCOUNT_OPENED', 'BANKING_ATM_TRANSACTION', 'BANKING_BRANCH_TRANSACTION', 'BANKING_CALL_CENTER_SUPPORT', 'BANKING_CASE_CLOSED', 'BANKING_CASE_OPENED', 'BANKING_CHAT_SUPPORT', 'BANKING_CREDIT_CARD_APPLICATION', 'BANKING_CREDIT_CARD_APPROVAL_DECISION', 'BANKING_FRAUD_INCIDENT', 'BANKING_MOBILE_EVENT', 'BANKING_MORTGAGE_EVENT', 'BANKING_MORTGAGE_OR_LOAN_APPLICATION', 'BANKING_MORTGAGE_OR_LOAN_CLOSING', 'BANKING_MORTGAGE_OR_LOAN_DECISION', 'BANKING_MORTGAGE_PRE_APPROVED', 'BANKING_WEBSITE_EVENT', 'BANKING_WEBSITE_VISIT', 'EVENT', 'HOSPITALITY_BOOKING', 'HOSPITALITY_CALL_CENTER_SUPPORT', 'HOSPITALITY_CASE_CLOSED', 'HOSPITALITY_CASE_OPENED', 'HOSPITALITY_CHAT_SUPPORT', 'HOSPITALITY_CHECK_IN', 'HOSPITALITY_CHECK_OUT', 'HOSPITALITY_COMPLAINT_FILED', 'HOSPITALITY_FOOD_OR_DINING_EVENT', 'HOSPITALITY_MARKETING_EVENT', 'HOSPITALITY_MOBILE_EVENT', 'HOSPITALITY_ROOM_SERVICE', 'HOSPITALITY_WEBSITE_EVENT', 'INSURANCE_ACCOUNT_CLOSED', 'INSURANCE_ACCOUNT_OPENED', 'INSURANCE_CALL_CENTER_SUPPORT', 'INSURANCE_CASE_CLOSED', 'INSURANCE_CASE_OPENED', 'INSURANCE_CHAT_SUPPORT', 'INSURANCE_CLAIM_DENIED', 'INSURANCE_COMPLAINT_FILED', 'INSURANCE_DISPUTE', 'INSURANCE_FIRST_NOTICE_OF_LOSS', 'INSURANCE_MOBILE_EVENT', 'INSURANCE_WEBSITE_EVENT', 'RETAIL_CALL_CENTER_SUPPORT', 'RETAIL_CASE_CLOSED', 'RETAIL_CASE_OPENED', 'RETAIL_CHAT_SUPPORT', 'RETAIL_EDUCATION_EVENT', 'RETAIL_EXCHANGE', 'RETAIL_INSTALLATION_COMPLETED', 'RETAIL_INSTALLATION_STARTED', 'RETAIL_MOBILE_EVENT', 'RETAIL_PRODUCT_DELIVERED', 'RETAIL_PRODUCT_SHIPPED', 'RETAIL_PURCHASE_IN_STORE', 'RETAIL_PURCHASE_ONLINE', 'RETAIL_PURCHASE_OVER_PHONE', 'RETAIL_SERVICE_COMPLETED', 'RETAIL_WEBSITE_EVENT', 'RETAIL_WEBSITE_VISIT')


class Ex360AssessmentStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_STARTED`
    * `DISMISSED`
    * `IN_PROGRESS`
    * `COMPLETED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COMPLETED', 'DISMISSED', 'IN_PROGRESS', 'NOT_STARTED')


class Ex360EnrolledParticipantProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `PROGRAM`
    * `WAVE`
    * `SELF_ASSESSMENT_STATUS`
    * `RATER_SELECTION_STATUS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('PROGRAM', 'RATER_SELECTION_STATUS', 'SELF_ASSESSMENT_STATUS', 'WAVE')


class Ex360EnrollmentApprovalDecision(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `APPROVED`
    * `REJECTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'REJECTED')


class Ex360EnrollmentStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `PENDING_APPROVAL`
    * `REJECTED`
    * `APPROVED`
    * `CANCELED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'CANCELED', 'PENDING_APPROVAL', 'REJECTED')


class Ex360RaterAssignmentApprovalDecision(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `APPROVED`
    * `REJECTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'REJECTED')


class Ex360RaterAssignmentStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `DRAFT`
    * `PENDING_REVIEW`
    * `APPROVED`
    * `REJECTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'DRAFT', 'PENDING_REVIEW', 'REJECTED')


class Ex360RaterElegibility(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ELEGIBLE`
    * `ALREADY_SELECTED_AS_RATER`
    * `MAX_RATING_REQUESTS_REACHED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ALREADY_SELECTED_AS_RATER', 'ELEGIBLE', 'MAX_RATING_REQUESTS_REACHED')


class Ex360RaterProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `RELATIONSHIP`
    '''
    __schema__ = medallia_schema
    __choices__ = ('RELATIONSHIP',)


class Ex360RaterSelectionApprovalMode(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NO_APPROVAL`
    * `SEQUENTIAL`
    * `ITERATIVE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ITERATIVE', 'NO_APPROVAL', 'SEQUENTIAL')


class Ex360UnsolicitedAssessmentParticipantElegibility(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ELEGIBLE`
    * `ALREADY_SELECTED_AS_PARTICIPANT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ALREADY_SELECTED_AS_PARTICIPANT', 'ELEGIBLE')


class Ex360WaveEnrolledAction(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ENROLL`
    * `CANCEL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CANCEL', 'ENROLL')


class Ex360WaveEnrollmentErrorType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_ELEGIBLE`
    * `QUARANTINED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('NOT_ELEGIBLE', 'QUARANTINED')


class Ex360WaveProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `WAVE_NAME`
    * `COMPLETION_DATE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COMPLETION_DATE', 'WAVE_NAME')


class Ex360WaveRaterAssignmentAction(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ADD`
    * `REMOVE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ADD', 'REMOVE')


class ExportAction(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `CANCEL`
    * `RERUN`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CANCEL', 'RERUN')


class ExportDefinitionScalar(sgqlc.types.Scalar):
    __schema__ = medallia_schema


class ExportError(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `MAX_ACTIVE_EXPORTS_EXCEEDED`
    * `UNSUPPORTED_FORMAT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('MAX_ACTIVE_EXPORTS_EXCEEDED', 'UNSUPPORTED_FORMAT')


class ExportFormat(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `CSV`
    * `EXCEL`
    * `PDF`
    * `CSV_SINGLE_LINE`
    * `PIPE_DELIMITED`
    * `TAB_DELIMITED`
    * `SPSS`
    * `ZIP`
    * `JSON`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CSV', 'CSV_SINGLE_LINE', 'EXCEL', 'JSON', 'PDF', 'PIPE_DELIMITED', 'SPSS', 'TAB_DELIMITED', 'ZIP')


class ExportJobStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `SCHEDULED`
    * `QUEUED`
    * `IN_PROGRESS`
    * `READY_TO_DOWNLOAD`
    * `CANCELED`
    * `DOWNLOADED`
    * `EXPIRED`
    * `FAILED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CANCELED', 'DOWNLOADED', 'EXPIRED', 'FAILED', 'IN_PROGRESS', 'QUEUED', 'READY_TO_DOWNLOAD', 'SCHEDULED')


class ExportType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `FEEDBACK`
    * `INVITATION`
    * `AGGREGATION_TABLE`
    * `AGGREGATION_TABLE_LIST`
    * `REPORT`
    * `MEDALLIA_BENCHMARKS_PREVIEW`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AGGREGATION_TABLE', 'AGGREGATION_TABLE_LIST', 'FEEDBACK', 'INVITATION', 'MEDALLIA_BENCHMARKS_PREVIEW', 'REPORT')


class ExternalBenchmarkOrder(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `BEFORE`
    * `AFTER`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AFTER', 'BEFORE')


class FieldLayout(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `SHORT_TEXT`
    * `MED_TEXT`
    * `LONG_TEXT`
    * `FOUR_LINES`
    * `TEN_LINES`
    * `DROP_DOWN`
    * `CHECK_BOX`
    * `RADIO_BUTTON`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CHECK_BOX', 'DROP_DOWN', 'FOUR_LINES', 'LONG_TEXT', 'MED_TEXT', 'RADIO_BUTTON', 'SHORT_TEXT', 'TEN_LINES')


class FieldNameFormat(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NAME`
    * `NAME_IN_SURVEY`
    * `CLIENT_IDENTIFIER`
    * `EXPORT_LABEL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CLIENT_IDENTIFIER', 'EXPORT_LABEL', 'NAME', 'NAME_IN_SURVEY')


class FileType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `CSV`
    * `DOCUMENT`
    * `IMAGE`
    * `PDF`
    * `PRESENTATION`
    * `SPREADSHEET`
    * `TEXT`
    * `UNKNOWN`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CSV', 'DOCUMENT', 'IMAGE', 'PDF', 'PRESENTATION', 'SPREADSHEET', 'TEXT', 'UNKNOWN')


Float = sgqlc.types.Float

class FormType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ALERT_RESOLUTION`
    * `CREATE_RECORD`
    * `EDIT_RECORD`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ALERT_RESOLUTION', 'CREATE_RECORD', 'EDIT_RECORD')


class ForwardResponseValidationError(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `EMAIL_BODY_EMPTY`
    * `EMAIL_SUBJECT_EMPTY`
    * `EMAIL_BODY_INCOMPLETE_PLACEHOLDERS`
    * `EMAIL_SUBJECT_INCOMPLETE_PLACEHOLDERS`
    * `EMAIL_RECIPIENTS_EMPTY`
    * `NON_RELATIVE_PDF_URL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('EMAIL_BODY_EMPTY', 'EMAIL_BODY_INCOMPLETE_PLACEHOLDERS', 'EMAIL_RECIPIENTS_EMPTY', 'EMAIL_SUBJECT_EMPTY', 'EMAIL_SUBJECT_INCOMPLETE_PLACEHOLDERS', 'NON_RELATIVE_PDF_URL')


class Gender(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `FEMALE`
    * `MALE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('FEMALE', 'MALE')


class GoalApprovalStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_SUBMITTED`
    * `PENDING_APPROVAL`
    * `EDITS_PENDING_APPROVAL`
    * `APPROVED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'EDITS_PENDING_APPROVAL', 'NOT_SUBMITTED', 'PENDING_APPROVAL')


class GoalLevel(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `COMPANY`
    * `TEAM`
    * `PERSONAL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COMPANY', 'PERSONAL', 'TEAM')


class GoalSubmissionStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_STARTED`
    * `STARTED`
    * `SUBMITTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('NOT_STARTED', 'STARTED', 'SUBMITTED')


class GoalsWaveParticipantProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `EMPLOYEE_NAME`
    * `GOAL_APPROVAL_STATUS`
    * `MANAGER_NAME`
    '''
    __schema__ = medallia_schema
    __choices__ = ('EMPLOYEE_NAME', 'GOAL_APPROVAL_STATUS', 'MANAGER_NAME')


class HeaderElementBasicProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `KEY`
    * `LABEL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('KEY', 'LABEL')


ID = sgqlc.types.ID

class InfiniteFloatValue(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `POSITIVE_INFINITY`
    * `NEGATIVE_INFINITY`
    '''
    __schema__ = medallia_schema
    __choices__ = ('NEGATIVE_INFINITY', 'POSITIVE_INFINITY')


class InstrumentationData(sgqlc.types.Scalar):
    __schema__ = medallia_schema


Int = sgqlc.types.Int

class IsolatedRecordType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `AD_HOC_PROGRAM`
    * `RIVAL_SOCIAL_REVIEW`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AD_HOC_PROGRAM', 'RIVAL_SOCIAL_REVIEW')


class KeywordTaggingSource(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `LUCENE`
    * `PARSER`
    '''
    __schema__ = medallia_schema
    __choices__ = ('LUCENE', 'PARSER')


class Long(sgqlc.types.Scalar):
    __schema__ = medallia_schema


class ManagerAssessmentDecision(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `APPROVED`
    * `REJECTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'REJECTED')


class ManagerAssessmentStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_STARTED`
    * `STARTED`
    * `SUBMITTED`
    * `AUTO_SUBMITTED`
    * `RELEASED`
    * `AUTO_RELEASED`
    * `ACKNOWLEDGED_BY_EMPLOYEE`
    * `ACKNOWLEDGED_BY_MANAGER`
    * `PENDING_APPROVAL`
    * `APPROVED`
    * `REJECTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ACKNOWLEDGED_BY_EMPLOYEE', 'ACKNOWLEDGED_BY_MANAGER', 'APPROVED', 'AUTO_RELEASED', 'AUTO_SUBMITTED', 'NOT_STARTED', 'PENDING_APPROVAL', 'REJECTED', 'RELEASED', 'STARTED', 'SUBMITTED')


class MatchingMode(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `RECORD_LEVEL`
    * `PHRASE_LEVEL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('PHRASE_LEVEL', 'RECORD_LEVEL')


class MediaFileEventType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `FILE_DOWNLOAD_FROM_SOURCE_DONE`
    * `FILE_DOWNLOAD_FROM_SOURCE_FAILED`
    * `MEDIA_TRANSCODING_FAILED`
    * `MEDIA_TRANSCRIPTION_FAILED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('FILE_DOWNLOAD_FROM_SOURCE_DONE', 'FILE_DOWNLOAD_FROM_SOURCE_FAILED', 'MEDIA_TRANSCODING_FAILED', 'MEDIA_TRANSCRIPTION_FAILED')


class MediaFileFormat(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `OPUS`
    * `MP4`
    '''
    __schema__ = medallia_schema
    __choices__ = ('MP4', 'OPUS')


class MediaFileQuality(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `_480P`
    * `_720P`
    * `_16KBPS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('_16KBPS', '_480P', '_720P')


class MediaPublishStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `DONE`
    * `TIMEOUT`
    * `FAILED`
    * `NOT_PUBLISHED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('DONE', 'FAILED', 'NOT_PUBLISHED', 'TIMEOUT')


class MessageCenterRegistrationChannel(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `APPLE_DEVICE`
    * `ANDROID_DEVICE`
    * `BAIDU_DEVICE`
    * `EMAIL_ACCOUNT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ANDROID_DEVICE', 'APPLE_DEVICE', 'BAIDU_DEVICE', 'EMAIL_ACCOUNT')


class MessageOrderProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `MESSAGE_ORDER`
    '''
    __schema__ = medallia_schema
    __choices__ = ('MESSAGE_ORDER',)


class MetricCalculation(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `COUNT`
    * `SUM`
    * `AVG`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AVG', 'COUNT', 'SUM')


class NestingSubtotal(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `BEFORE`
    * `AFTER`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AFTER', 'BEFORE')


class Operation(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `LESS_THAN`
    * `LESS_THAN_OR_EQUAL`
    * `GREATER_THAN`
    * `GREATER_THAN_OR_EQUAL`
    * `IN`
    * `NOT_IN`
    * `IS_NULL`
    * `IS_NOT_NULL`
    * `BEFORE_DATE`
    * `ON_BEFORE_DATE`
    * `AFTER_DATE`
    * `ON_AFTER_DATE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AFTER_DATE', 'BEFORE_DATE', 'GREATER_THAN', 'GREATER_THAN_OR_EQUAL', 'IN', 'IS_NOT_NULL', 'IS_NULL', 'LESS_THAN', 'LESS_THAN_OR_EQUAL', 'NOT_IN', 'ON_AFTER_DATE', 'ON_BEFORE_DATE')


class OrderDirection(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ASC`
    * `DESC`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ASC', 'DESC')


class OrgHierarchyFilterType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ACTION_PLANS`
    * `WATCHLIST`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ACTION_PLANS', 'WATCHLIST')


class OrgHierarchyListFilterField(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ORG_MEMBER_NAME`
    * `ORG_MEMBER_UNIT_IDENTIFIER`
    * `ORG_MEMBER_UNIT_GROUP_IDENTIFIER`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ORG_MEMBER_NAME', 'ORG_MEMBER_UNIT_GROUP_IDENTIFIER', 'ORG_MEMBER_UNIT_IDENTIFIER')


class OverallEmotion(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `STRONGLY_POSITIVE`
    * `POSITIVE`
    * `NEUTRAL`
    * `NEGATIVE`
    * `STRONGLY_NEGATIVE`
    * `TOO_SHORT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('NEGATIVE', 'NEUTRAL', 'POSITIVE', 'STRONGLY_NEGATIVE', 'STRONGLY_POSITIVE', 'TOO_SHORT')


class PageType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `CUSTOM_REPORT`
    * `DASHBOARD`
    * `EMBEDDED_APP`
    * `SYSTEM_REPORT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CUSTOM_REPORT', 'DASHBOARD', 'EMBEDDED_APP', 'SYSTEM_REPORT')


class PercentageComparison(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `INCREASE`
    * `DECREASE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('DECREASE', 'INCREASE')


class PerformanceRatingStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_STARTED`
    * `STARTED`
    * `SUBMITTED`
    * `AUTO_SUBMITTED`
    * `RELEASED`
    * `AUTO_RELEASED`
    * `APPROVED`
    * `PENDING_APPROVAL`
    * `REJECTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'AUTO_RELEASED', 'AUTO_SUBMITTED', 'NOT_STARTED', 'PENDING_APPROVAL', 'REJECTED', 'RELEASED', 'STARTED', 'SUBMITTED')


class PersonalizedAlertStatusEnum(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ACTIVE`
    * `INACTIVE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ACTIVE', 'INACTIVE')


class Quartile(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `FIRST`
    * `SECOND`
    * `THIRD`
    * `FOURTH`
    '''
    __schema__ = medallia_schema
    __choices__ = ('FIRST', 'FOURTH', 'SECOND', 'THIRD')


class QueryResult(sgqlc.types.Scalar):
    __schema__ = medallia_schema


class RaterSelectionScheduleStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `OPEN`
    * `CLOSED`
    * `FUTURE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CLOSED', 'FUTURE', 'OPEN')


class RaterSelectionStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_STARTED`
    * `STARTED`
    * `PENDING_APPROVAL`
    * `APPROVED`
    * `REJECTED`
    * `INSUFFICIENT_RATERS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('APPROVED', 'INSUFFICIENT_RATERS', 'NOT_STARTED', 'PENDING_APPROVAL', 'REJECTED', 'STARTED')


class ReceptionType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `RECEIVED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('RECEIVED',)


class RoundingMode(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `HALF_EVEN`
    * `HALF_UP`
    '''
    __schema__ = medallia_schema
    __choices__ = ('HALF_EVEN', 'HALF_UP')


class Rule(sgqlc.types.Scalar):
    __schema__ = medallia_schema


class SelfAssessmentStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_STARTED`
    * `STARTED`
    * `SUBMITTED`
    * `AUTO_SUBMITTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AUTO_SUBMITTED', 'NOT_STARTED', 'STARTED', 'SUBMITTED')


class Sentiment(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `STRONGLY_POSITIVE`
    * `POSITIVE`
    * `MIXED_OPINION`
    * `NEGATIVE`
    * `STRONGLY_NEGATIVE`
    * `NO_OPINION`
    '''
    __schema__ = medallia_schema
    __choices__ = ('MIXED_OPINION', 'NEGATIVE', 'NO_OPINION', 'POSITIVE', 'STRONGLY_NEGATIVE', 'STRONGLY_POSITIVE')


class SignificanceTestComparisonStrategy(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `PREVIOUS`
    * `COMPLEMENT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COMPLEMENT', 'PREVIOUS')


class SignificanceTestDifferenceClassification(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `INCREMENT`
    * `DECREMENT`
    * `INSIGNIFICANT`
    * `NOT_TESTED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('DECREMENT', 'INCREMENT', 'INSIGNIFICANT', 'NOT_TESTED')


class SocialFeedbackKind(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `REVIEWS`
    * `SOCIAL_NETWORK`
    '''
    __schema__ = medallia_schema
    __choices__ = ('REVIEWS', 'SOCIAL_NETWORK')


class SocialHeaderElementBasicProperty(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `KEY`
    * `LABEL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('KEY', 'LABEL')


class SocialReviewsSentiment(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `STRONGLY_POSITIVE`
    * `POSITIVE`
    * `MIXED_OPINION`
    * `NEGATIVE`
    * `STRONGLY_NEGATIVE`
    * `NO_OPINION`
    '''
    __schema__ = medallia_schema
    __choices__ = ('MIXED_OPINION', 'NEGATIVE', 'NO_OPINION', 'POSITIVE', 'STRONGLY_NEGATIVE', 'STRONGLY_POSITIVE')


class SocialSentimentId(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NO_SENTIMENT`
    * `NEGATIVE`
    * `MILD_NEGATIVE`
    * `NEUTRAL`
    * `MILD_POSITIVE`
    * `POSITIVE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('MILD_NEGATIVE', 'MILD_POSITIVE', 'NEGATIVE', 'NEUTRAL', 'NO_SENTIMENT', 'POSITIVE')


class SocialSortByDirection(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ASC`
    * `DESC`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ASC', 'DESC')


class SocialTimeGroupingUnit(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `MONTH`
    * `QUARTER`
    * `WEEK`
    * `DAY`
    * `YEAR`
    * `HOUR`
    * `NONE`
    * `ALL`
    * `WEEK_WITH_TIME_OF_YEAR_SPLIT`
    * `WEEK_STARTING_MONDAY`
    * `HALF_YEAR`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ALL', 'DAY', 'HALF_YEAR', 'HOUR', 'MONTH', 'NONE', 'QUARTER', 'WEEK', 'WEEK_STARTING_MONDAY', 'WEEK_WITH_TIME_OF_YEAR_SPLIT', 'YEAR')


class SortByDirection(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ASC`
    * `DESC`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ASC', 'DESC')


class SortingDirection(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ASC`
    * `DESC`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ASC', 'DESC')


class SortingField(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `TEXT_IDENTIFIER`
    * `NAME`
    * `ADDRESS`
    * `STATUS`
    * `SOURCE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ADDRESS', 'NAME', 'SOURCE', 'STATUS', 'TEXT_IDENTIFIER')


class SplitElementId(sgqlc.types.Scalar):
    __schema__ = medallia_schema


class StandardKind(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ATTENTION_NEEDED`
    * `HIGH_CUSTOMER_EFFORT`
    * `RECENT_NON_RESPONDERS`
    * `RECENT_RESPONDERS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ATTENTION_NEEDED', 'HIGH_CUSTOMER_EFFORT', 'RECENT_NON_RESPONDERS', 'RECENT_RESPONDERS')


class Status(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `DRAFT`
    * `ACTIVE`
    * `INACTIVE`
    * `ARCHIVED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ACTIVE', 'ARCHIVED', 'DRAFT', 'INACTIVE')


String = sgqlc.types.String

class TaskStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NOT_STARTED`
    * `IN_PROGRESS`
    * `COMPLETED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('COMPLETED', 'IN_PROGRESS', 'NOT_STARTED')


class TextAnalyticsLanguage(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ABKHAZIAN`
    * `AFAR`
    * `AFRIKAANS`
    * `AKAN`
    * `ALBANIAN`
    * `AMHARIC`
    * `ARABIC`
    * `ARAGONESE`
    * `ARMENIAN`
    * `ASSAMESE`
    * `AVARIC`
    * `AVESTAN`
    * `AYMARA`
    * `AZERBAIJANI`
    * `BAMBARA`
    * `BASHKIR`
    * `BASQUE`
    * `BELARUSIAN`
    * `BENGALI`
    * `BIHARI`
    * `BISLAMA`
    * `BOSNIAN`
    * `BRETON`
    * `BULGARIAN`
    * `CATALAN`
    * `CHAMORRO`
    * `CHECHEN`
    * `CHICHEWA`
    * `CHINESE`
    * `CHUVASH`
    * `CORNISH`
    * `CORSICAN`
    * `CREE`
    * `CROATIAN`
    * `CZECH`
    * `DANISH`
    * `DUTCH`
    * `DZONGKHA`
    * `ENGLISH`
    * `ESPERANTO`
    * `ESTONIAN`
    * `EWE`
    * `FAROESE`
    * `FIJIAN`
    * `FINNISH`
    * `FRENCH`
    * `FRISIAN`
    * `FULAH`
    * `GALICIAN`
    * `GANDA`
    * `GEORGIAN`
    * `GERMAN`
    * `GREEK`
    * `GREENLANDIC`
    * `GUARANI`
    * `GUJARATI`
    * `HAITIAN`
    * `HAUSA`
    * `HEBREW`
    * `HERERO`
    * `HINDI`
    * `HIRI_MOTU`
    * `HUNGARIAN`
    * `ICELANDIC`
    * `IDO`
    * `IGBO`
    * `INDONESIAN`
    * `INTERLINGUA`
    * `INUKTITUT`
    * `INUPIAQ`
    * `IRISH`
    * `ITALIAN`
    * `JAPANESE`
    * `JAVANESE`
    * `JAVANESE_DEPRECATED`
    * `KANNADA`
    * `KANURI`
    * `KASHMIRI`
    * `KAZAKH`
    * `KHMER`
    * `KIKUYU`
    * `KINYARWANDA`
    * `KIRGHIZ`
    * `KOMI`
    * `KONGO`
    * `KOREAN`
    * `KURDISH`
    * `KWANYAMA`
    * `LAO`
    * `LATIN`
    * `LATVIAN`
    * `LIMBURGISH`
    * `LINGALA`
    * `LITHUANIAN`
    * `LUBA_KATANGA`
    * `LUXEMBOURGISH`
    * `MACEDONIAN`
    * `MALAGASY`
    * `MALAY`
    * `MALAYALAM`
    * `MALTESE`
    * `MANX`
    * `MAORI`
    * `MARATHI`
    * `MARSHALLESE`
    * `MONGOLIAN`
    * `MYANMAR`
    * `NAURU`
    * `NAVAJO`
    * `NDONGA`
    * `NEPALI`
    * `NORTH_NDEBELE`
    * `NORTHERN_SAMI`
    * `NORWEGIAN_BOKMAL`
    * `NORWEGIAN`
    * `NORWEGIAN_NYNORSK`
    * `OCCITAN`
    * `OJIBWA`
    * `ORIYA`
    * `OROMO`
    * `OSSETIAN`
    * `PALI`
    * `PERSIAN`
    * `POLISH`
    * `PORTUGUESE`
    * `PUNJABI`
    * `PUNJABI_DEPRECATED`
    * `PUSHTO`
    * `QUECHUA`
    * `RAETO_ROMANCE`
    * `ROMANIAN`
    * `RUNDI`
    * `RUSSIAN`
    * `SAMOAN`
    * `SANGO`
    * `SANSKRIT`
    * `SARDINIAN`
    * `SCOTTISH_GAELIC`
    * `SERBIAN`
    * `SESOTHO`
    * `SHONA`
    * `SICHUAN_YI`
    * `SINDHI`
    * `SINHALA`
    * `SLOVAK`
    * `SLOVENIAN`
    * `SOMALI`
    * `SOUTH_NDEBELE`
    * `SPANISH`
    * `SUDANESE`
    * `SWAHILI`
    * `SWATI`
    * `SWEDISH`
    * `TAGALOG`
    * `TAHITIAN`
    * `TAJIK`
    * `TAMIL`
    * `TATAR`
    * `TELUGU`
    * `THAI`
    * `TIBETAN`
    * `TIGRINYA`
    * `TONGA`
    * `TSONGA`
    * `TSWANA`
    * `TURKISH`
    * `TURKMEN`
    * `TWI`
    * `UIGHUR`
    * `UKRAINIAN`
    * `URDU`
    * `UZBEK`
    * `VENDA`
    * `VIETNAMESE`
    * `VOLAPUK`
    * `WALLOON`
    * `WELSH`
    * `WOLOF`
    * `XHOSA`
    * `YIDDISH`
    * `YORUBA`
    * `ZHUANG`
    * `ZULU`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ABKHAZIAN', 'AFAR', 'AFRIKAANS', 'AKAN', 'ALBANIAN', 'AMHARIC', 'ARABIC', 'ARAGONESE', 'ARMENIAN', 'ASSAMESE', 'AVARIC', 'AVESTAN', 'AYMARA', 'AZERBAIJANI', 'BAMBARA', 'BASHKIR', 'BASQUE', 'BELARUSIAN', 'BENGALI', 'BIHARI', 'BISLAMA', 'BOSNIAN', 'BRETON', 'BULGARIAN', 'CATALAN', 'CHAMORRO', 'CHECHEN', 'CHICHEWA', 'CHINESE', 'CHUVASH', 'CORNISH', 'CORSICAN', 'CREE', 'CROATIAN', 'CZECH', 'DANISH', 'DUTCH', 'DZONGKHA', 'ENGLISH', 'ESPERANTO', 'ESTONIAN', 'EWE', 'FAROESE', 'FIJIAN', 'FINNISH', 'FRENCH', 'FRISIAN', 'FULAH', 'GALICIAN', 'GANDA', 'GEORGIAN', 'GERMAN', 'GREEK', 'GREENLANDIC', 'GUARANI', 'GUJARATI', 'HAITIAN', 'HAUSA', 'HEBREW', 'HERERO', 'HINDI', 'HIRI_MOTU', 'HUNGARIAN', 'ICELANDIC', 'IDO', 'IGBO', 'INDONESIAN', 'INTERLINGUA', 'INUKTITUT', 'INUPIAQ', 'IRISH', 'ITALIAN', 'JAPANESE', 'JAVANESE', 'JAVANESE_DEPRECATED', 'KANNADA', 'KANURI', 'KASHMIRI', 'KAZAKH', 'KHMER', 'KIKUYU', 'KINYARWANDA', 'KIRGHIZ', 'KOMI', 'KONGO', 'KOREAN', 'KURDISH', 'KWANYAMA', 'LAO', 'LATIN', 'LATVIAN', 'LIMBURGISH', 'LINGALA', 'LITHUANIAN', 'LUBA_KATANGA', 'LUXEMBOURGISH', 'MACEDONIAN', 'MALAGASY', 'MALAY', 'MALAYALAM', 'MALTESE', 'MANX', 'MAORI', 'MARATHI', 'MARSHALLESE', 'MONGOLIAN', 'MYANMAR', 'NAURU', 'NAVAJO', 'NDONGA', 'NEPALI', 'NORTHERN_SAMI', 'NORTH_NDEBELE', 'NORWEGIAN', 'NORWEGIAN_BOKMAL', 'NORWEGIAN_NYNORSK', 'OCCITAN', 'OJIBWA', 'ORIYA', 'OROMO', 'OSSETIAN', 'PALI', 'PERSIAN', 'POLISH', 'PORTUGUESE', 'PUNJABI', 'PUNJABI_DEPRECATED', 'PUSHTO', 'QUECHUA', 'RAETO_ROMANCE', 'ROMANIAN', 'RUNDI', 'RUSSIAN', 'SAMOAN', 'SANGO', 'SANSKRIT', 'SARDINIAN', 'SCOTTISH_GAELIC', 'SERBIAN', 'SESOTHO', 'SHONA', 'SICHUAN_YI', 'SINDHI', 'SINHALA', 'SLOVAK', 'SLOVENIAN', 'SOMALI', 'SOUTH_NDEBELE', 'SPANISH', 'SUDANESE', 'SWAHILI', 'SWATI', 'SWEDISH', 'TAGALOG', 'TAHITIAN', 'TAJIK', 'TAMIL', 'TATAR', 'TELUGU', 'THAI', 'TIBETAN', 'TIGRINYA', 'TONGA', 'TSONGA', 'TSWANA', 'TURKISH', 'TURKMEN', 'TWI', 'UIGHUR', 'UKRAINIAN', 'URDU', 'UZBEK', 'VENDA', 'VIETNAMESE', 'VOLAPUK', 'WALLOON', 'WELSH', 'WOLOF', 'XHOSA', 'YIDDISH', 'YORUBA', 'ZHUANG', 'ZULU')


class TextFormat(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `TEXT`
    * `IP_ADDRESS`
    * `PHONE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('IP_ADDRESS', 'PHONE', 'TEXT')


class ThresholdComparison(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `ABOVE`
    * `BELOW`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ABOVE', 'BELOW')


class TimeGroupingUnit(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `MONTH`
    * `QUARTER`
    * `WEEK`
    * `DAY`
    * `YEAR`
    * `HOUR`
    * `NONE`
    * `ALL`
    * `WEEK_WITH_TIME_OF_YEAR_SPLIT`
    * `WEEK_STARTING_MONDAY`
    * `HALF_YEAR`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ALL', 'DAY', 'HALF_YEAR', 'HOUR', 'MONTH', 'NONE', 'QUARTER', 'WEEK', 'WEEK_STARTING_MONDAY', 'WEEK_WITH_TIME_OF_YEAR_SPLIT', 'YEAR')


class TransitionResultStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `SUCCESS`
    * `QUEUE_LIMIT_REACHED`
    * `INVALID_OPERATION`
    '''
    __schema__ = medallia_schema
    __choices__ = ('INVALID_OPERATION', 'QUEUE_LIMIT_REACHED', 'SUCCESS')


class Type(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `AD_HOC`
    * `TRACKING`
    * `ENTERPRISE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AD_HOC', 'ENTERPRISE', 'TRACKING')


class URI(sgqlc.types.Scalar):
    __schema__ = medallia_schema


class UserMessageType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `EXPORT_READY_FOR_DOWNLOAD`
    * `EXPORT_FAILURE`
    * `PERSONALIZED_ALERT_TRIGGERED`
    * `PERSONALIZED_ALERT_FAILURE`
    * `RECORD_LEVEL_PERSONALIZED_ALERT_TRIGGERED`
    * `RECORD_LEVEL_PERSONALIZED_ALERT_FAILURE`
    * `SOCIALIZATION_LIKE`
    * `SOCIALIZATION_COMMENT`
    * `SOCIALIZATION_MENTION`
    * `SOCIALIZATION_UNIT_MENTION`
    * `UNIT_WATCH_NEW_RESPONSES`
    * `UNIT_WATCH_NEW_ALERTS`
    * `RAPID_RESPONSE`
    * `SURVEY_ACTIVITY`
    * `ALERT_ASSIGNMENT`
    * `ALERT_EMAIL_ACTION`
    * `ALERT_STATUS_CHANGE`
    * `ALERT_OWNER_NOTE`
    * `PROGRAM_APPROVAL_EVENT_RESOLUTION`
    * `PROGRAM_APPROVAL_EVENT_REQUEST`
    * `PROGRAM_APPROVAL_EVENT_CREATED`
    * `RESPONSE_FORWARD_FAILURE`
    * `TOPIC_PUBLISHING_COMPLETED`
    * `TOPIC_PUBLISHING_FAILED`
    * `EMPLOYEE_PROGRAM_NOTIFICATION`
    * `WATCHLIST_FORCED_UNSUBSCRIPTION`
    * `EMPLOYEE_PROGRAM_INVITE`
    * `EMPLOYEE_PROGRAM_REMINDER`
    * `ACTION_PLAN_UPDATE`
    * `ACTION_PLAN_DELETE`
    * `ACTION_PLAN_ASSIGNMENT`
    * `ACTION_PLAN_STATUS_CHANGE`
    * `ACTION_PLAN_TASK_UPDATE`
    * `ACTION_PLAN_TASK_DELETE`
    * `ACTION_PLAN_TASK_ASSIGNMENT`
    * `ACTION_PLAN_TASK_STATUS_CHANGE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ACTION_PLAN_ASSIGNMENT', 'ACTION_PLAN_DELETE', 'ACTION_PLAN_STATUS_CHANGE', 'ACTION_PLAN_TASK_ASSIGNMENT', 'ACTION_PLAN_TASK_DELETE', 'ACTION_PLAN_TASK_STATUS_CHANGE', 'ACTION_PLAN_TASK_UPDATE', 'ACTION_PLAN_UPDATE', 'ALERT_ASSIGNMENT', 'ALERT_EMAIL_ACTION', 'ALERT_OWNER_NOTE', 'ALERT_STATUS_CHANGE', 'EMPLOYEE_PROGRAM_INVITE', 'EMPLOYEE_PROGRAM_NOTIFICATION', 'EMPLOYEE_PROGRAM_REMINDER', 'EXPORT_FAILURE', 'EXPORT_READY_FOR_DOWNLOAD', 'PERSONALIZED_ALERT_FAILURE', 'PERSONALIZED_ALERT_TRIGGERED', 'PROGRAM_APPROVAL_EVENT_CREATED', 'PROGRAM_APPROVAL_EVENT_REQUEST', 'PROGRAM_APPROVAL_EVENT_RESOLUTION', 'RAPID_RESPONSE', 'RECORD_LEVEL_PERSONALIZED_ALERT_FAILURE', 'RECORD_LEVEL_PERSONALIZED_ALERT_TRIGGERED', 'RESPONSE_FORWARD_FAILURE', 'SOCIALIZATION_COMMENT', 'SOCIALIZATION_LIKE', 'SOCIALIZATION_MENTION', 'SOCIALIZATION_UNIT_MENTION', 'SURVEY_ACTIVITY', 'TOPIC_PUBLISHING_COMPLETED', 'TOPIC_PUBLISHING_FAILED', 'UNIT_WATCH_NEW_ALERTS', 'UNIT_WATCH_NEW_RESPONSES', 'WATCHLIST_FORCED_UNSUBSCRIPTION')


class ValueType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `SINGLE_VALUED`
    * `MULTI_VALUED`
    * `RANKING`
    * `NO_VALUE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('MULTI_VALUED', 'NO_VALUE', 'RANKING', 'SINGLE_VALUED')


class VoiceChannelRole(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `AGENT`
    * `CUSTOMER`
    * `NONE`
    * `BOT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('AGENT', 'BOT', 'CUSTOMER', 'NONE')


class WatchlistEventType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NEW_ALERTS`
    * `NEW_RESPONSES`
    * `ESCALATED_ALERTS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ESCALATED_ALERTS', 'NEW_ALERTS', 'NEW_RESPONSES')


class WaveStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `DRAFT`
    * `ACTIVE`
    * `INACTIVE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ACTIVE', 'DRAFT', 'INACTIVE')


class WaveType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `GOALS`
    * `ASSESSMENTS`
    * `E360_FEEDBACK`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ASSESSMENTS', 'E360_FEEDBACK', 'GOALS')


class WordcloudSentiment(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `POSITIVE`
    * `NEGATIVE`
    * `NEUTRAL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('NEGATIVE', 'NEUTRAL', 'POSITIVE')


class WordcloudSize(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `TINY`
    * `SMALL`
    * `MEDIUM`
    * `LARGE`
    * `HUGE`
    '''
    __schema__ = medallia_schema
    __choices__ = ('HUGE', 'LARGE', 'MEDIUM', 'SMALL', 'TINY')


class XStatsAnalysisExecutionStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `WAITING_FOR_WORKBENCH`
    * `JOB_CREATION_PENDING`
    * `RESULT_POLL_PENDING`
    * `RESULT_EVICTION_PENDING`
    * `RERUN_PENDING`
    '''
    __schema__ = medallia_schema
    __choices__ = ('JOB_CREATION_PENDING', 'RERUN_PENDING', 'RESULT_EVICTION_PENDING', 'RESULT_POLL_PENDING', 'WAITING_FOR_WORKBENCH')


class XStatsAnalysisStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `QUEUED`
    * `PROCESSING`
    * `READY`
    * `EXPIRED`
    * `FAILED`
    * `OUTDATED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('EXPIRED', 'FAILED', 'OUTDATED', 'PROCESSING', 'QUEUED', 'READY')


class XStatsDatasetTimeperiodUnit(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `DAYS`
    * `MONTHS`
    '''
    __schema__ = medallia_schema
    __choices__ = ('DAYS', 'MONTHS')


class XStatsErrorCode(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `UNKNOWN_ERROR`
    * `SYSTEM_ERROR`
    * `CONNECTION_ERROR`
    * `RESULT_POLL_LIMIT_REACHED`
    * `FIELD_VALUES_ERROR`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CONNECTION_ERROR', 'FIELD_VALUES_ERROR', 'RESULT_POLL_LIMIT_REACHED', 'SYSTEM_ERROR', 'UNKNOWN_ERROR')


class XStatsFieldErrorCode(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `UNKNOWN_ERROR`
    * `ALL_SAME_VALUES`
    * `ALL_VALUES_DIFFERENT`
    '''
    __schema__ = medallia_schema
    __choices__ = ('ALL_SAME_VALUES', 'ALL_VALUES_DIFFERENT', 'UNKNOWN_ERROR')


class XStatsValidationError(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `WORKBENCHES_LIMIT_EXCEEDED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('WORKBENCHES_LIMIT_EXCEEDED',)


class XStatsVariableType(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NUMERIC`
    * `CATEGORICAL`
    '''
    __schema__ = medallia_schema
    __choices__ = ('CATEGORICAL', 'NUMERIC')


class XStatsWorkbenchStatus(sgqlc.types.Enum):
    '''Enumeration Choices:

    * `NEEDS_PROCESSING`
    * `PROCESSING`
    * `READY`
    * `FAILED`
    '''
    __schema__ = medallia_schema
    __choices__ = ('FAILED', 'NEEDS_PROCESSING', 'PROCESSING', 'READY')



########################################################################
# Input Objects
########################################################################
class ActionImpactAnalysisInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('enabled', 'baseline_begins_date', 'setup_begins_date', 'start_test_date', 'end_test_date', 'control_group_name', 'control_group_query', 'impact_group_name', 'impact_group_query', 'metrics_ids')
    enabled = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='enabled')

    baseline_begins_date = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='baselineBeginsDate')

    setup_begins_date = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='setupBeginsDate')

    start_test_date = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='startTestDate')

    end_test_date = sgqlc.types.Field(Date, graphql_name='endTestDate')

    control_group_name = sgqlc.types.Field(String, graphql_name='controlGroupName')

    control_group_query = sgqlc.types.Field('EventCondition', graphql_name='controlGroupQuery')

    impact_group_name = sgqlc.types.Field(String, graphql_name='impactGroupName')

    impact_group_query = sgqlc.types.Field('EventCondition', graphql_name='impactGroupQuery')

    metrics_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='metricsIds')



class ActionPlanAttachmentInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'file_name', 'file_url')
    id = sgqlc.types.Field(ID, graphql_name='id')

    file_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fileName')

    file_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fileUrl')



class ActionPlanFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'in_', 'lt', 'lte', 'gt', 'gte')
    field = sgqlc.types.Field(sgqlc.types.non_null(ActionPlanFilterField), graphql_name='field')

    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='in')

    lt = sgqlc.types.Field(String, graphql_name='lt')

    lte = sgqlc.types.Field(String, graphql_name='lte')

    gt = sgqlc.types.Field(String, graphql_name='gt')

    gte = sgqlc.types.Field(String, graphql_name='gte')



class ActionPlanInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('title', 'description', 'owner_id', 'status', 'unit', 'rule_topics_ids', 'data_topics_ids', 'drivers_keys', 'aggregated_actions_identifiers', 'feedback_records_ids', 'impact_analysis', 'attachments')
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='title')

    description = sgqlc.types.Field(String, graphql_name='description')

    owner_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='ownerId')

    status = sgqlc.types.Field(sgqlc.types.non_null(ActionPlanStatus), graphql_name='status')

    unit = sgqlc.types.Field(ID, graphql_name='unit')

    rule_topics_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ruleTopicsIds')

    data_topics_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='dataTopicsIds')

    drivers_keys = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='driversKeys')

    aggregated_actions_identifiers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='aggregatedActionsIdentifiers')

    feedback_records_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='feedbackRecordsIds')

    impact_analysis = sgqlc.types.Field(ActionImpactAnalysisInput, graphql_name='impactAnalysis')

    attachments = sgqlc.types.Field(sgqlc.types.list_of(ActionPlanAttachmentInput), graphql_name='attachments')



class ActionPlanOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(OrderDirection, graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(ActionPlanOrderProperty), graphql_name='property')



class ActionPlanTaskInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('action_plan_id', 'name', 'description', 'owner_id', 'status', 'due_date')
    action_plan_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='actionPlanId')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    description = sgqlc.types.Field(String, graphql_name='description')

    owner_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='ownerId')

    status = sgqlc.types.Field(sgqlc.types.non_null(TaskStatus), graphql_name='status')

    due_date = sgqlc.types.Field(sgqlc.types.non_null(Date), graphql_name='dueDate')



class ActionPlanTaskOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(OrderDirection, graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(ActionPlanTaskOrderProperty), graphql_name='property')



class AggregateDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('data', 'metric', 'benchmark')
    data = sgqlc.types.Field(sgqlc.types.non_null('DatasetDefinition'), graphql_name='data')

    metric = sgqlc.types.Field(sgqlc.types.non_null('Metric'), graphql_name='metric')

    benchmark = sgqlc.types.Field('BenchmarkDefinition', graphql_name='benchmark')



class AggregateListDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('data', 'metrics')
    data = sgqlc.types.Field(sgqlc.types.non_null('DatasetDefinition'), graphql_name='data')

    metrics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Metric'))), graphql_name='metrics')



class AggregateRankDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('my_data', 'field_key', 'sort_field_by', 'metric', 'minimum_sample_size', 'sampling', 'ranked_data', 'sort_by_sample_size')
    my_data = sgqlc.types.Field(sgqlc.types.non_null('DatasetDefinition'), graphql_name='myData')

    field_key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fieldKey')

    sort_field_by = sgqlc.types.Field(AggregateRankSortFieldBy, graphql_name='sortFieldBy')

    metric = sgqlc.types.Field(sgqlc.types.non_null('Metric'), graphql_name='metric')

    minimum_sample_size = sgqlc.types.Field(Long, graphql_name='minimumSampleSize')

    sampling = sgqlc.types.Field(Int, graphql_name='sampling')

    ranked_data = sgqlc.types.Field(sgqlc.types.non_null('RankedDataDefinition'), graphql_name='rankedData')

    sort_by_sample_size = sgqlc.types.Field(Boolean, graphql_name='sortBySampleSize')



class AggregateRankListDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('my_data', 'field_key', 'sort_field_by', 'metrics', 'minimum_sample_size', 'sampling', 'ranked_data', 'sort_by_sample_size')
    my_data = sgqlc.types.Field(sgqlc.types.non_null('DatasetDefinition'), graphql_name='myData')

    field_key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fieldKey')

    sort_field_by = sgqlc.types.Field(AggregateRankSortFieldBy, graphql_name='sortFieldBy')

    metrics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Metric'))), graphql_name='metrics')

    minimum_sample_size = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='minimumSampleSize')

    sampling = sgqlc.types.Field(Int, graphql_name='sampling')

    ranked_data = sgqlc.types.Field(sgqlc.types.non_null('RankedDataDefinition'), graphql_name='rankedData')

    sort_by_sample_size = sgqlc.types.Field(Boolean, graphql_name='sortBySampleSize')



class AggregateTableCellSetOfValues(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('metrics', 'counts', 'metric_counts')
    metrics = sgqlc.types.Field('AggregationTableMetricReference', graphql_name='metrics')

    counts = sgqlc.types.Field('AggregationTableEmptyArg', graphql_name='counts')

    metric_counts = sgqlc.types.Field('AggregationTableMetricReference', graphql_name='metricCounts')



class AggregateTableColumn(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('group', 'key')
    group = sgqlc.types.Field(String, graphql_name='group')

    key = sgqlc.types.Field(String, graphql_name='key')



class AggregateTableColumnCell(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('row',)
    row = sgqlc.types.Field('AggregateTableRow', graphql_name='row')



class AggregateTableColumnCellMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'row')
    key = sgqlc.types.Field(String, graphql_name='key')

    row = sgqlc.types.Field('AggregateTableRow', graphql_name='row')



class AggregateTableColumnHaving(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('value', 'non_null', 'positive', 'gte', 'set_of_values', 'all_match', 'any_match', 'not_', 'and_', 'or_')
    value = sgqlc.types.Field('AggregateTableColumnValue', graphql_name='value')

    non_null = sgqlc.types.Field(Boolean, graphql_name='nonNull')

    positive = sgqlc.types.Field(Boolean, graphql_name='positive')

    gte = sgqlc.types.Field('AggregateTableColumnValue', graphql_name='gte')

    set_of_values = sgqlc.types.Field('AggregateTableColumnSetOfValues', graphql_name='setOfValues')

    all_match = sgqlc.types.Field('AggregateTableColumnHaving', graphql_name='allMatch')

    any_match = sgqlc.types.Field('AggregateTableColumnHaving', graphql_name='anyMatch')

    not_ = sgqlc.types.Field('AggregateTableColumnHaving', graphql_name='not')

    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('AggregateTableColumnHaving')), graphql_name='and')

    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('AggregateTableColumnHaving')), graphql_name='or')



class AggregateTableColumnSetOfCellMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'row')
    key = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='key')

    row = sgqlc.types.Field('AggregateTableSetOfRow', graphql_name='row')



class AggregateTableColumnSetOfCells(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('row',)
    row = sgqlc.types.Field('AggregateTableSetOfRow', graphql_name='row')



class AggregateTableColumnSetOfValues(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('metrics', 'counts', 'metric_counts')
    metrics = sgqlc.types.Field(AggregateTableColumnSetOfCellMetric, graphql_name='metrics')

    counts = sgqlc.types.Field(AggregateTableColumnSetOfCells, graphql_name='counts')

    metric_counts = sgqlc.types.Field(AggregateTableColumnSetOfCellMetric, graphql_name='metricCounts')



class AggregateTableColumnSetOfValues2(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('values', 'rows')
    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AggregateTableCellSetOfValues))), graphql_name='values')

    rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('AggregateTableSetOfRow'))), graphql_name='rows')



class AggregateTableColumnSortBy(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('value', 'direction')
    value = sgqlc.types.Field(sgqlc.types.non_null('AggregateTableColumnValue'), graphql_name='value')

    direction = sgqlc.types.Field(sgqlc.types.non_null(SortByDirection), graphql_name='direction')



class AggregateTableColumnValue(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('metric', 'count', 'metric_count', 'header', 'int', 'float')
    metric = sgqlc.types.Field(AggregateTableColumnCellMetric, graphql_name='metric')

    count = sgqlc.types.Field(AggregateTableColumnCell, graphql_name='count')

    metric_count = sgqlc.types.Field(AggregateTableColumnCellMetric, graphql_name='metricCount')

    header = sgqlc.types.Field('HeaderElementValue', graphql_name='header')

    int = sgqlc.types.Field(Long, graphql_name='int')

    float = sgqlc.types.Field(Float, graphql_name='float')



class AggregateTableDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('data', 'benchmark', 'columns', 'column_groups', 'rows', 'row_groups', 'metrics', 'labeled_metrics', 'text_analytics_matching', 'use_global_data_set_as_total')
    data = sgqlc.types.Field(sgqlc.types.non_null('DatasetDefinition'), graphql_name='data')

    benchmark = sgqlc.types.Field('BenchmarkDefinition', graphql_name='benchmark')

    columns = sgqlc.types.Field('AggregationTableColumnRecordSplitAxis', graphql_name='columns')

    column_groups = sgqlc.types.Field(sgqlc.types.list_of('AggregationTableColumnRecordSplitAxis'), graphql_name='columnGroups')

    rows = sgqlc.types.Field('AggregationTableRowRecordSplitAxis', graphql_name='rows')

    row_groups = sgqlc.types.Field(sgqlc.types.list_of('AggregationTableRowRecordSplitAxis'), graphql_name='rowGroups')

    metrics = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Metric')), graphql_name='metrics')

    labeled_metrics = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('LabeledMetric')), graphql_name='labeledMetrics')

    text_analytics_matching = sgqlc.types.Field(MatchingMode, graphql_name='textAnalyticsMatching')

    use_global_data_set_as_total = sgqlc.types.Field(Boolean, graphql_name='useGlobalDataSetAsTotal')



class AggregateTableListPagination(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('rows_pagination', 'columns_pagination')
    rows_pagination = sgqlc.types.Field('AggregateTablePagination', graphql_name='rowsPagination')

    columns_pagination = sgqlc.types.Field('AggregateTablePagination', graphql_name='columnsPagination')



class AggregateTablePagination(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('limit', 'offset', 'after_key', 'before_key')
    limit = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='limit')

    offset = sgqlc.types.Field(Int, graphql_name='offset')

    after_key = sgqlc.types.Field(SplitElementId, graphql_name='afterKey')

    before_key = sgqlc.types.Field(SplitElementId, graphql_name='beforeKey')



class AggregateTableRow(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('group', 'key')
    group = sgqlc.types.Field(String, graphql_name='group')

    key = sgqlc.types.Field(String, graphql_name='key')



class AggregateTableRowCell(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('column',)
    column = sgqlc.types.Field(AggregateTableColumn, graphql_name='column')



class AggregateTableRowCellMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'column')
    key = sgqlc.types.Field(String, graphql_name='key')

    column = sgqlc.types.Field(AggregateTableColumn, graphql_name='column')



class AggregateTableRowEnhancedAnonymity(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('inherit_data_view_threshold',)
    inherit_data_view_threshold = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='inheritDataViewThreshold')



class AggregateTableRowGroupHeader(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field_name',)
    field_name = sgqlc.types.Field('AggregationTableEmptyArg', graphql_name='fieldName')



class AggregateTableRowHaving(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('value', 'non_null', 'positive', 'gte', 'contains_string', 'set_of_values', 'all_match', 'any_match', 'not_', 'and_', 'or_')
    value = sgqlc.types.Field('AggregateTableRowValue', graphql_name='value')

    non_null = sgqlc.types.Field(Boolean, graphql_name='nonNull')

    positive = sgqlc.types.Field(Boolean, graphql_name='positive')

    gte = sgqlc.types.Field('AggregateTableRowValue', graphql_name='gte')

    contains_string = sgqlc.types.Field(String, graphql_name='containsString')

    set_of_values = sgqlc.types.Field('AggregateTableRowSetOfValues', graphql_name='setOfValues')

    all_match = sgqlc.types.Field('AggregateTableRowHaving', graphql_name='allMatch')

    any_match = sgqlc.types.Field('AggregateTableRowHaving', graphql_name='anyMatch')

    not_ = sgqlc.types.Field('AggregateTableRowHaving', graphql_name='not')

    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('AggregateTableRowHaving')), graphql_name='and')

    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('AggregateTableRowHaving')), graphql_name='or')



class AggregateTableRowSetOfCellMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'column')
    key = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='key')

    column = sgqlc.types.Field('AggregateTableSetOfColumn', graphql_name='column')



class AggregateTableRowSetOfCells(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('column',)
    column = sgqlc.types.Field('AggregateTableSetOfColumn', graphql_name='column')



class AggregateTableRowSetOfValues(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('metrics', 'counts', 'metric_counts')
    metrics = sgqlc.types.Field(AggregateTableRowSetOfCellMetric, graphql_name='metrics')

    counts = sgqlc.types.Field(AggregateTableRowSetOfCells, graphql_name='counts')

    metric_counts = sgqlc.types.Field(AggregateTableRowSetOfCellMetric, graphql_name='metricCounts')



class AggregateTableRowSetOfValues2(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('values', 'columns')
    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AggregateTableCellSetOfValues))), graphql_name='values')

    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('AggregateTableSetOfColumn'))), graphql_name='columns')



class AggregateTableRowSortBy(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('value', 'direction')
    value = sgqlc.types.Field(sgqlc.types.non_null('AggregateTableRowValue'), graphql_name='value')

    direction = sgqlc.types.Field(sgqlc.types.non_null(SortByDirection), graphql_name='direction')



class AggregateTableRowValue(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('metric', 'count', 'metric_count', 'header', 'int', 'float')
    metric = sgqlc.types.Field(AggregateTableRowCellMetric, graphql_name='metric')

    count = sgqlc.types.Field(AggregateTableRowCell, graphql_name='count')

    metric_count = sgqlc.types.Field(AggregateTableRowCellMetric, graphql_name='metricCount')

    header = sgqlc.types.Field('HeaderElementValue', graphql_name='header')

    int = sgqlc.types.Field(Long, graphql_name='int')

    float = sgqlc.types.Field(Float, graphql_name='float')



class AggregateTableSetOfColumn(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('group', 'key')
    group = sgqlc.types.Field(String, graphql_name='group')

    key = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='key')



class AggregateTableSetOfRow(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('group', 'key')
    group = sgqlc.types.Field(String, graphql_name='group')

    key = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='key')



class AggregatedActionCondition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('program_ids', 'in_')
    program_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='programIds')

    in_ = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='in')



class AggregatedActionOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property', 'custom_calculation')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(AggregatedActionsProperty, graphql_name='property')

    custom_calculation = sgqlc.types.Field('CustomCalculation', graphql_name='customCalculation')



class AggregationRankedTableExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('format', 'table', 'ranks')
    format = sgqlc.types.Field(sgqlc.types.non_null('AggregationTableFormat'), graphql_name='format')

    table = sgqlc.types.Field(sgqlc.types.non_null(AggregateTableDefinition), graphql_name='table')

    ranks = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AggregateRankDefinition))), graphql_name='ranks')



class AggregationTableBenchmarkTotalRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class AggregationTableColumnConcatRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('splits', 'pagination', 'sort_by', 'having')
    splits = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('AggregationTableColumnRecordSplitAxis'))), graphql_name='splits')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')



class AggregationTableColumnDataTopicsLevelRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('tag_pool_ids', 'level', 'language', 'search', 'comment_fields', 'personas', 'phrase_co_occurring_topic_id', 'role', 'name', 'sort_by', 'having', 'pagination')
    tag_pool_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='tagPoolIds')

    level = sgqlc.types.Field(Int, graphql_name='level')

    language = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='language')

    search = sgqlc.types.Field(String, graphql_name='search')

    comment_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='commentFields')

    personas = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='personas')

    phrase_co_occurring_topic_id = sgqlc.types.Field(String, graphql_name='phraseCoOccurringTopicId')

    role = sgqlc.types.Field(AggregationTableTASplitAxisTopicRole, graphql_name='role')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableColumnSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableColumnHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableColumnDeltaRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('comparison', 'reference', 'calculation', 'name')
    comparison = sgqlc.types.Field(sgqlc.types.non_null('AggregationTableColumnRecordSplitAxis'), graphql_name='comparison')

    reference = sgqlc.types.Field(sgqlc.types.non_null('AggregationTableColumnRecordSplitAxis'), graphql_name='reference')

    calculation = sgqlc.types.Field(DeltaCalculation, graphql_name='calculation')

    name = sgqlc.types.Field(String, graphql_name='name')



class AggregationTableColumnHierarchyAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('of', 'name', 'sort_by', 'having', 'pagination')
    of = sgqlc.types.Field('AggregationTableRowRecordSplitAxis', graphql_name='of')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableColumnSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableColumnHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableColumnNestingAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('subtotal', 'benchmark', 'splits', 'pagination', 'sort_by', 'having', 'use_default_naming')
    subtotal = sgqlc.types.Field(NestingSubtotal, graphql_name='subtotal')

    benchmark = sgqlc.types.Field('NestingBenchmark', graphql_name='benchmark')

    splits = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NestableColumnRecordSplitAxis'))), graphql_name='splits')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableColumnSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableColumnHaving, graphql_name='having')

    use_default_naming = sgqlc.types.Field(Boolean, graphql_name='useDefaultNaming')



class AggregationTableColumnRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('segment', 'slices', 'timeperiods', 'total', 'benchmark_total', 'topic_ids', 'rule_topics_level', 'data_topics_level', 'topic_children', 'hierarchy', 'nesting', 'concat', 'delta')
    segment = sgqlc.types.Field('AggregationTableColumnSegmentRecordSplitAxis', graphql_name='segment')

    slices = sgqlc.types.Field('AggregationTableColumnSlicesRecordSplitAxis', graphql_name='slices')

    timeperiods = sgqlc.types.Field('AggregationTableColumnTimeperiodsRecordSplitAxis', graphql_name='timeperiods')

    total = sgqlc.types.Field('AggregationTableTotalRecordSplitAxis', graphql_name='total')

    benchmark_total = sgqlc.types.Field(AggregationTableBenchmarkTotalRecordSplitAxis, graphql_name='benchmarkTotal')

    topic_ids = sgqlc.types.Field('AggregationTableColumnTopicIdsRecordSplitAxis', graphql_name='topicIds')

    rule_topics_level = sgqlc.types.Field('AggregationTableColumnRuleTopicsLevelRecordSplitAxis', graphql_name='ruleTopicsLevel')

    data_topics_level = sgqlc.types.Field(AggregationTableColumnDataTopicsLevelRecordSplitAxis, graphql_name='dataTopicsLevel')

    topic_children = sgqlc.types.Field('AggregationTableColumnTopicChildrenRecordSplitAxis', graphql_name='topicChildren')

    hierarchy = sgqlc.types.Field(AggregationTableColumnHierarchyAxis, graphql_name='hierarchy')

    nesting = sgqlc.types.Field(AggregationTableColumnNestingAxis, graphql_name='nesting')

    concat = sgqlc.types.Field(AggregationTableColumnConcatRecordSplitAxis, graphql_name='concat')

    delta = sgqlc.types.Field(AggregationTableColumnDeltaRecordSplitAxis, graphql_name='delta')



class AggregationTableColumnRuleTopicsLevelRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('tag_pool_ids', 'level', 'search', 'comment_fields', 'personas', 'phrase_co_occurring_topic_id', 'role', 'name', 'sort_by', 'having', 'pagination')
    tag_pool_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='tagPoolIds')

    level = sgqlc.types.Field(Int, graphql_name='level')

    search = sgqlc.types.Field(String, graphql_name='search')

    comment_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='commentFields')

    personas = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='personas')

    phrase_co_occurring_topic_id = sgqlc.types.Field(String, graphql_name='phraseCoOccurringTopicId')

    role = sgqlc.types.Field(AggregationTableTASplitAxisTopicRole, graphql_name='role')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableColumnSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableColumnHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableColumnSegmentRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'fields', 'name', 'sort_by', 'having', 'pagination')
    field = sgqlc.types.Field('FieldId', graphql_name='field')

    fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('FieldId')), graphql_name='fields')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableColumnSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableColumnHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableColumnSlicesRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('items', 'name', 'sort_by', 'having', 'pagination')
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Slice'))), graphql_name='items')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableColumnSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableColumnHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableColumnTimeperiodsRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'start', 'end', 'unit', 'rolling_window', 'name', 'sort_by', 'having', 'pagination')
    field = sgqlc.types.Field(sgqlc.types.non_null('FieldId'), graphql_name='field')

    start = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='start')

    end = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='end')

    unit = sgqlc.types.Field(sgqlc.types.non_null(TimeGroupingUnit), graphql_name='unit')

    rolling_window = sgqlc.types.Field(Int, graphql_name='rollingWindow')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableColumnSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableColumnHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableColumnTopicChildrenRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('parent_id', 'search', 'comment_fields', 'personas', 'phrase_co_occurring_topic_id', 'role', 'name', 'sort_by', 'having', 'pagination')
    parent_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='parentId')

    search = sgqlc.types.Field(String, graphql_name='search')

    comment_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='commentFields')

    personas = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='personas')

    phrase_co_occurring_topic_id = sgqlc.types.Field(String, graphql_name='phraseCoOccurringTopicId')

    role = sgqlc.types.Field(AggregationTableTASplitAxisTopicRole, graphql_name='role')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableColumnSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableColumnHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableColumnTopicIdsRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('ids', 'comment_fields', 'personas', 'phrase_co_occurring_topic_id', 'role', 'name', 'sort_by', 'having', 'pagination')
    ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='ids')

    comment_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='commentFields')

    personas = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='personas')

    phrase_co_occurring_topic_id = sgqlc.types.Field(String, graphql_name='phraseCoOccurringTopicId')

    role = sgqlc.types.Field(AggregationTableTASplitAxisTopicRole, graphql_name='role')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableColumnSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableColumnHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableColumnsLayoutAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('columns', 'values_and_columns', 'columns_and_values')
    columns = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AggregateTableSetOfColumn)), graphql_name='columns')

    values_and_columns = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AggregateTableRowSetOfValues2)), graphql_name='valuesAndColumns')

    columns_and_values = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AggregateTableRowSetOfValues2)), graphql_name='columnsAndValues')



class AggregationTableDifferenceColumnsDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('base_column_index', 'subtraction_column_index')
    base_column_index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='baseColumnIndex')

    subtraction_column_index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='subtractionColumnIndex')



class AggregationTableEmptyArg(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('dummy_field',)
    dummy_field = sgqlc.types.Field(String, graphql_name='dummyField')



class AggregationTableExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('format', 'table', 'with_chi_square_test_table')
    format = sgqlc.types.Field(sgqlc.types.non_null('AggregationTableFormat'), graphql_name='format')

    table = sgqlc.types.Field(sgqlc.types.non_null(AggregateTableDefinition), graphql_name='table')

    with_chi_square_test_table = sgqlc.types.Field(Boolean, graphql_name='withChiSquareTestTable')



class AggregationTableFormat(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('custom_headers', 'columns_layout_axis', 'rows_layout_axis', 'visible_sub_axes', 'columns_sub_axis_headers', 'rows_sub_axis_headers', 'numeric_format')
    custom_headers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String)))), graphql_name='customHeaders')

    columns_layout_axis = sgqlc.types.Field(sgqlc.types.non_null(AggregationTableColumnsLayoutAxis), graphql_name='columnsLayoutAxis')

    rows_layout_axis = sgqlc.types.Field(sgqlc.types.non_null('AggregationTableRowsLayoutAxis'), graphql_name='rowsLayoutAxis')

    visible_sub_axes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AggregationTableLayoutSubAxis)), graphql_name='visibleSubAxes')

    columns_sub_axis_headers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('AggregationTableLayoutSplitSubAxisHeader')), graphql_name='columnsSubAxisHeaders')

    rows_sub_axis_headers = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('AggregationTableLayoutSplitSubAxisHeader')), graphql_name='rowsSubAxisHeaders')

    numeric_format = sgqlc.types.Field('NumericFormat', graphql_name='numericFormat')



class AggregationTableLayoutSplitSubAxisHeader(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('label', 'rank_in_group', 'data_field')
    label = sgqlc.types.Field(AggregationTableEmptyArg, graphql_name='label')

    rank_in_group = sgqlc.types.Field(AggregationTableEmptyArg, graphql_name='rankInGroup')

    data_field = sgqlc.types.Field(String, graphql_name='dataField')



class AggregationTableListExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('items', 'with_chi_square_test_table')
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AggregationTableExport))), graphql_name='items')

    with_chi_square_test_table = sgqlc.types.Field(Boolean, graphql_name='withChiSquareTestTable')



class AggregationTableMetricReference(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('keys',)
    keys = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='keys')



class AggregationTablePercentage(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('axis',)
    axis = sgqlc.types.Field(sgqlc.types.non_null(Axis), graphql_name='axis')



class AggregationTableRowConcatRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('splits', 'pagination', 'sort_by', 'having')
    splits = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('AggregationTableRowRecordSplitAxis'))), graphql_name='splits')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')



class AggregationTableRowDataTopicsLevelRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('tag_pool_ids', 'level', 'language', 'search', 'comment_fields', 'personas', 'phrase_co_occurring_topic_id', 'role', 'name', 'sort_by', 'having', 'pagination')
    tag_pool_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='tagPoolIds')

    level = sgqlc.types.Field(Int, graphql_name='level')

    language = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='language')

    search = sgqlc.types.Field(String, graphql_name='search')

    comment_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='commentFields')

    personas = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='personas')

    phrase_co_occurring_topic_id = sgqlc.types.Field(String, graphql_name='phraseCoOccurringTopicId')

    role = sgqlc.types.Field(AggregationTableTASplitAxisTopicRole, graphql_name='role')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableRowHierarchyAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('of', 'name', 'sort_by', 'having', 'pagination')
    of = sgqlc.types.Field('AggregationTableRowRecordSplitAxis', graphql_name='of')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableRowNestingAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('subtotal', 'splits', 'pagination', 'sort_by', 'having')
    subtotal = sgqlc.types.Field(NestingSubtotal, graphql_name='subtotal')

    splits = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('NestableRowRecordSplitAxis'))), graphql_name='splits')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')



class AggregationTableRowRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('segment', 'concat', 'slices', 'timeperiods', 'units', 'total', 'topic_ids', 'rule_topics_level', 'data_topics_level', 'topic_children', 'hierarchy', 'nesting', 'use_default_naming')
    segment = sgqlc.types.Field('AggregationTableRowSegmentRecordSplitAxis', graphql_name='segment')

    concat = sgqlc.types.Field(AggregationTableRowConcatRecordSplitAxis, graphql_name='concat')

    slices = sgqlc.types.Field('AggregationTableRowSlicesRecordSplitAxis', graphql_name='slices')

    timeperiods = sgqlc.types.Field('AggregationTableRowTimeperiodsRecordSplitAxis', graphql_name='timeperiods')

    units = sgqlc.types.Field('AggregationTableRowUnitsRecordSplitAxis', graphql_name='units')

    total = sgqlc.types.Field('AggregationTableTotalRecordSplitAxis', graphql_name='total')

    topic_ids = sgqlc.types.Field('AggregationTableRowTopicIdsRecordSplitAxis', graphql_name='topicIds')

    rule_topics_level = sgqlc.types.Field('AggregationTableRowRuleTopicsLevelRecordSplitAxis', graphql_name='ruleTopicsLevel')

    data_topics_level = sgqlc.types.Field(AggregationTableRowDataTopicsLevelRecordSplitAxis, graphql_name='dataTopicsLevel')

    topic_children = sgqlc.types.Field('AggregationTableRowTopicChildrenRecordSplitAxis', graphql_name='topicChildren')

    hierarchy = sgqlc.types.Field(AggregationTableRowHierarchyAxis, graphql_name='hierarchy')

    nesting = sgqlc.types.Field(AggregationTableRowNestingAxis, graphql_name='nesting')

    use_default_naming = sgqlc.types.Field(Boolean, graphql_name='useDefaultNaming')



class AggregationTableRowRuleTopicsLevelRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('tag_pool_ids', 'level', 'search', 'comment_fields', 'personas', 'phrase_co_occurring_topic_id', 'role', 'name', 'sort_by', 'having', 'pagination')
    tag_pool_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='tagPoolIds')

    level = sgqlc.types.Field(Int, graphql_name='level')

    search = sgqlc.types.Field(String, graphql_name='search')

    comment_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='commentFields')

    personas = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='personas')

    phrase_co_occurring_topic_id = sgqlc.types.Field(String, graphql_name='phraseCoOccurringTopicId')

    role = sgqlc.types.Field(AggregationTableTASplitAxisTopicRole, graphql_name='role')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableRowSegmentRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'fields', 'name', 'sort_by', 'having', 'pagination', 'enhanced_anonymity')
    field = sgqlc.types.Field('FieldId', graphql_name='field')

    fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('FieldId')), graphql_name='fields')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')

    enhanced_anonymity = sgqlc.types.Field(AggregateTableRowEnhancedAnonymity, graphql_name='enhancedAnonymity')



class AggregationTableRowSlicesRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('items', 'name', 'sort_by', 'having', 'pagination')
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Slice'))), graphql_name='items')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableRowTimeperiodsRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'start', 'end', 'unit', 'rolling_window', 'name', 'sort_by', 'having', 'pagination')
    field = sgqlc.types.Field(sgqlc.types.non_null('FieldId'), graphql_name='field')

    start = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='start')

    end = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='end')

    unit = sgqlc.types.Field(sgqlc.types.non_null(TimeGroupingUnit), graphql_name='unit')

    rolling_window = sgqlc.types.Field(Int, graphql_name='rollingWindow')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableRowTopicChildrenRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('parent_id', 'search', 'comment_fields', 'personas', 'phrase_co_occurring_topic_id', 'role', 'name', 'sort_by', 'having', 'pagination')
    parent_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='parentId')

    search = sgqlc.types.Field(String, graphql_name='search')

    comment_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='commentFields')

    personas = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='personas')

    phrase_co_occurring_topic_id = sgqlc.types.Field(String, graphql_name='phraseCoOccurringTopicId')

    role = sgqlc.types.Field(AggregationTableTASplitAxisTopicRole, graphql_name='role')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableRowTopicIdsRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('ids', 'comment_fields', 'personas', 'phrase_co_occurring_topic_id', 'role', 'name', 'sort_by', 'having', 'pagination')
    ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='ids')

    comment_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='commentFields')

    personas = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='personas')

    phrase_co_occurring_topic_id = sgqlc.types.Field(String, graphql_name='phraseCoOccurringTopicId')

    role = sgqlc.types.Field(AggregationTableTASplitAxisTopicRole, graphql_name='role')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableRowUnitsRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('unit_field', 'unit_groups', 'name', 'sort_by', 'having', 'pagination')
    unit_field = sgqlc.types.Field('FieldId', graphql_name='unitField')

    unit_groups = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='unitGroups')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(AggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(AggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(AggregateTablePagination, graphql_name='pagination')



class AggregationTableRowsLayoutAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('rows', 'values_and_rows', 'rows_and_values', 'group_headers')
    rows = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AggregateTableSetOfRow)), graphql_name='rows')

    values_and_rows = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AggregateTableColumnSetOfValues2)), graphql_name='valuesAndRows')

    rows_and_values = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AggregateTableColumnSetOfValues2)), graphql_name='rowsAndValues')

    group_headers = sgqlc.types.Field(AggregateTableRowGroupHeader, graphql_name='groupHeaders')



class AggregationTableTotalRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('name',)
    name = sgqlc.types.Field(String, graphql_name='name')



class AlertFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('workflow_ids', 'status_ids', 'owner_role_ids')
    workflow_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='workflowIds')

    status_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='statusIds')

    owner_role_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ownerRoleIds')



class AskNowTestOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'attribute')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    attribute = sgqlc.types.Field(sgqlc.types.non_null(AskNowAttribute), graphql_name='attribute')



class AssessmentWaveParticipationOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(AssessmentWaveParticipationProperty), graphql_name='property')



class AsyncTaskOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(OrderDirection, graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(AsyncTaskOrderProperty), graphql_name='property')



class AttributeKey(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key',)
    key = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='key')



class AttributeListSource(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('schema', 'attribute_keys')
    schema = sgqlc.types.Field(ID, graphql_name='schema')

    attribute_keys = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='attributeKeys')



class AttributeSource(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('schema', 'attribute_key')
    schema = sgqlc.types.Field(ID, graphql_name='schema')

    attribute_key = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='attributeKey')



class BenchmarkDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class BucketCountDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field_ids', 'in_', 'lt', 'lte', 'gt', 'gte')
    field_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='fieldIds')

    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='in')

    lt = sgqlc.types.Field(String, graphql_name='lt')

    lte = sgqlc.types.Field(String, graphql_name='lte')

    gt = sgqlc.types.Field(String, graphql_name='gt')

    gte = sgqlc.types.Field(String, graphql_name='gte')



class ContactAttributeCondition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'is_null', 'is_not_null', 'in_', 'not_in', 'lt', 'lte', 'gt', 'gte', 'before', 'on_or_before', 'after', 'on_or_after')
    key = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='key')

    is_null = sgqlc.types.Field(Boolean, graphql_name='isNull')

    is_not_null = sgqlc.types.Field(Boolean, graphql_name='isNotNull')

    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='in')

    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='notIn')

    lt = sgqlc.types.Field(Float, graphql_name='lt')

    lte = sgqlc.types.Field(Float, graphql_name='lte')

    gt = sgqlc.types.Field(Float, graphql_name='gt')

    gte = sgqlc.types.Field(Float, graphql_name='gte')

    before = sgqlc.types.Field(DateTime, graphql_name='before')

    on_or_before = sgqlc.types.Field(DateTime, graphql_name='onOrBefore')

    after = sgqlc.types.Field(DateTime, graphql_name='after')

    on_or_after = sgqlc.types.Field(DateTime, graphql_name='onOrAfter')



class ContactCondition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('attribute',)
    attribute = sgqlc.types.Field(ContactAttributeCondition, graphql_name='attribute')



class ContactFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('attribute_key', 'in_', 'lt', 'lte', 'gt', 'gte', 'text_search', 'ids', 'segment', 'max_days_ago_updated', 'and_', 'or_', 'not_')
    attribute_key = sgqlc.types.Field(ID, graphql_name='attributeKey')

    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='in')

    lt = sgqlc.types.Field(String, graphql_name='lt')

    lte = sgqlc.types.Field(String, graphql_name='lte')

    gt = sgqlc.types.Field(String, graphql_name='gt')

    gte = sgqlc.types.Field(String, graphql_name='gte')

    text_search = sgqlc.types.Field(String, graphql_name='textSearch')

    ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids')

    segment = sgqlc.types.Field('ContactSegmentFilter', graphql_name='segment')

    max_days_ago_updated = sgqlc.types.Field(Int, graphql_name='maxDaysAgoUpdated')

    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ContactFilter')), graphql_name='and')

    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ContactFilter')), graphql_name='or')

    not_ = sgqlc.types.Field('ContactFilter', graphql_name='not')



class ContactOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'attribute_key')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    attribute_key = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='attributeKey')



class ContactSegmentCancelAction(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')



class ContactSegmentCancelExportAction(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')



class ContactSegmentDeleteAction(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')



class ContactSegmentDeleteDataAction(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')



class ContactSegmentFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')



class ContactSegmentInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('name', 'rules', 'data_view')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    rules = sgqlc.types.Field(sgqlc.types.non_null('ContactSegmentRule'), graphql_name='rules')

    data_view = sgqlc.types.Field(sgqlc.types.non_null('DataView'), graphql_name='dataView')



class ContactSegmentOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(ContactSegmentOrderProperty), graphql_name='property')



class ContactSegmentRefreshAction(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'export', 'attributes', 'format')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    export = sgqlc.types.Field(Boolean, graphql_name='export')

    attributes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AttributeKey)), graphql_name='attributes')

    format = sgqlc.types.Field(ExportFormat, graphql_name='format')



class ContactSegmentRestartAction(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'export', 'attributes', 'format')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    export = sgqlc.types.Field(Boolean, graphql_name='export')

    attributes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AttributeKey)), graphql_name='attributes')

    format = sgqlc.types.Field(ExportFormat, graphql_name='format')



class ContactSegmentRule(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('contact', 'event', 'and_', 'or_')
    contact = sgqlc.types.Field(ContactCondition, graphql_name='contact')

    event = sgqlc.types.Field('EventRule', graphql_name='event')

    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ContactSegmentRule')), graphql_name='and')

    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('ContactSegmentRule')), graphql_name='or')



class ContactSegmentRunAction(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'export', 'attributes', 'format')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    export = sgqlc.types.Field(Boolean, graphql_name='export')

    attributes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AttributeKey)), graphql_name='attributes')

    format = sgqlc.types.Field(ExportFormat, graphql_name='format')



class ContactSegmentStartExportAction(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'attributes', 'format')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    attributes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(AttributeKey)), graphql_name='attributes')

    format = sgqlc.types.Field(sgqlc.types.non_null(ExportFormat), graphql_name='format')



class ContactSegmentTestDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('rule', 'columns', 'update_segment', 'data_view')
    rule = sgqlc.types.Field(sgqlc.types.non_null(ContactSegmentRule), graphql_name='rule')

    columns = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('FormattedContactAttribute')), graphql_name='columns')

    update_segment = sgqlc.types.Field(ID, graphql_name='updateSegment')

    data_view = sgqlc.types.Field(sgqlc.types.non_null('DataView'), graphql_name='dataView')



class ContactUpdate(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('values',)
    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ContactValue'))), graphql_name='values')



class ContactValue(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'value')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')

    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')



class CorrelationOperation(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field_ids',)
    field_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='fieldIds')



class CountUniqueDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'gt', 'gte', 'lt', 'lte')
    field = sgqlc.types.Field(sgqlc.types.non_null('FieldId'), graphql_name='field')

    gt = sgqlc.types.Field(String, graphql_name='gt')

    gte = sgqlc.types.Field(String, graphql_name='gte')

    lt = sgqlc.types.Field(String, graphql_name='lt')

    lte = sgqlc.types.Field(String, graphql_name='lte')



class CustomCalculatedField(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'arguments')
    field = sgqlc.types.Field(sgqlc.types.non_null('FieldId'), graphql_name='field')

    arguments = sgqlc.types.Field(sgqlc.types.list_of('CustomCalculatedFieldArgument'), graphql_name='arguments')



class CustomCalculatedFieldArgument(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'value')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')

    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')



class CustomCalculation(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('name', 'field')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    field = sgqlc.types.Field(sgqlc.types.non_null('FieldId'), graphql_name='field')



class DailyFrequencyInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('daily',)
    daily = sgqlc.types.Field(Boolean, graphql_name='daily')



class DataTopicCondition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('program_ids', 'data_topics')
    program_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='programIds')

    data_topics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='dataTopics')



class DataView(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')



class DatasetDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('source', 'filter', 'include_ad_hoc', 'include_isolated_records_of_type')
    source = sgqlc.types.Field(sgqlc.types.non_null(DataSource), graphql_name='source')

    filter = sgqlc.types.Field('Filter', graphql_name='filter')

    include_ad_hoc = sgqlc.types.Field(Boolean, graphql_name='includeAdHoc')

    include_isolated_records_of_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(IsolatedRecordType)), graphql_name='includeIsolatedRecordsOfType')



class DateInterval(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('from_', 'to')
    from_ = sgqlc.types.Field(Date, graphql_name='from')

    to = sgqlc.types.Field(Date, graphql_name='to')



class DescribeOperation(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field_ids',)
    field_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='fieldIds')



class E360FeedbackAssignedRaterFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('relationship',)
    relationship = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='relationship')



class E360FeedbackAssignedRaterOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(E360AssignedRaterOrderProperty), graphql_name='property')



class E360FeedbackPerRaterRelationshipOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(E360FeedbackPerRaterRelationshipProperty), graphql_name='property')



class E360FeedbackQuestionScoreOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(E360FeedbackQuestionScoreProperty), graphql_name='property')



class E360FeedbackRaterAssignmentDecisionInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('rater_id', 'rater_relationship_id', 'decision')
    rater_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='raterId')

    rater_relationship_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='raterRelationshipId')

    decision = sgqlc.types.Field(sgqlc.types.non_null(E360FeedbackRaterAssignmentDecision), graphql_name='decision')



class E360FeedbackRaterAssignmentInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('rater_id', 'rater_relationship_id', 'action')
    rater_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='raterId')

    rater_relationship_id = sgqlc.types.Field(ID, graphql_name='raterRelationshipId')

    action = sgqlc.types.Field(sgqlc.types.non_null(E360FeedbackRaterAssignmentAction), graphql_name='action')



class E360FeedbackRequestOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(E360FeedbackRequestOrderProperty), graphql_name='property')



class E360FeedbackWaveParticipationOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(E360FeedbackWaveParticipationProperty), graphql_name='property')



class E360WaveEnrollmentDecisionInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('participation_id', 'action')
    participation_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='participationId')

    action = sgqlc.types.Field(sgqlc.types.non_null(E360EnrollmentDecision), graphql_name='action')



class E360WaveEnrollmentInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('wave_id', 'employee_id', 'action')
    wave_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='waveId')

    employee_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='employeeId')

    action = sgqlc.types.Field(sgqlc.types.non_null(E360WaveEnrollmentAction), graphql_name='action')



class EmployeeAttributeFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'in_')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    in_ = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='in')



class EmployeeFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('attribute', 'and_')
    attribute = sgqlc.types.Field(EmployeeAttributeFilter, graphql_name='attribute')

    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('EmployeeFilter')), graphql_name='and')



class EmployeeOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(EmployeeProperty), graphql_name='property')



class EmployeeProgramParticipationExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('program_id', 'segment', 'wave_ids', 'team_ids', 'report_definitions', 'combination_mode', 'wave_filters')
    program_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='programId')

    segment = sgqlc.types.Field('ReporteeSegment', graphql_name='segment')

    wave_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='waveIds')

    team_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='teamIds')

    report_definitions = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('EmployeeProgramReportDefinition')), graphql_name='reportDefinitions')

    combination_mode = sgqlc.types.Field(EmployeeProgramReportCombinationMode, graphql_name='combinationMode')

    wave_filters = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('EmployeeProgramReportWaveFilter')), graphql_name='waveFilters')



class EmployeeProgramReportDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('report_type', 'url_template')
    report_type = sgqlc.types.Field(sgqlc.types.non_null(EmployeeProgramReportType), graphql_name='reportType')

    url_template = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='urlTemplate')



class EmployeeProgramReportWaveFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('wave_type', 'wave_ids', 'review_ids')
    wave_type = sgqlc.types.Field(WaveType, graphql_name='waveType')

    wave_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='waveIds')

    review_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='reviewIds')



class EmployeeSegment(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('team_ids', 'currently_assigned', 'filter', 'query')
    team_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='teamIds')

    currently_assigned = sgqlc.types.Field(Boolean, graphql_name='currentlyAssigned')

    filter = sgqlc.types.Field(EmployeeFilter, graphql_name='filter')

    query = sgqlc.types.Field(String, graphql_name='query')



class EventCondition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('and_', 'or_', 'field', 'rule_topics', 'data_topics', 'insight', 'aggregated_action')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('EventCondition')), graphql_name='and')

    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('EventCondition')), graphql_name='or')

    field = sgqlc.types.Field('FieldCondition', graphql_name='field')

    rule_topics = sgqlc.types.Field('RuleTopicCondition', graphql_name='ruleTopics')

    data_topics = sgqlc.types.Field(DataTopicCondition, graphql_name='dataTopics')

    insight = sgqlc.types.Field('InsightCondition', graphql_name='insight')

    aggregated_action = sgqlc.types.Field(AggregatedActionCondition, graphql_name='aggregatedAction')



class EventFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('type_keys',)
    type_keys = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(EventTypeKey))), graphql_name='typeKeys')



class EventRule(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('metric', 'where')
    metric = sgqlc.types.Field('MetricCondition', graphql_name='metric')

    where = sgqlc.types.Field(EventCondition, graphql_name='where')



class Ex360AssessmentInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('participant_id',)
    participant_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='participantId')



class Ex360EnrolledParticipantOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(Ex360EnrolledParticipantProperty), graphql_name='property')



class Ex360EnrollmentApprovalInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('wave', 'participant_id', 'approval')
    wave = sgqlc.types.Field(sgqlc.types.non_null('Ex360WaveRefInput'), graphql_name='wave')

    participant_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='participantId')

    approval = sgqlc.types.Field(sgqlc.types.non_null(Ex360EnrollmentApprovalDecision), graphql_name='approval')



class Ex360RaterAssignmentApprovalInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('wave', 'participant_id', 'rater_id', 'relationship_id', 'approval')
    wave = sgqlc.types.Field(sgqlc.types.non_null('Ex360WaveRefInput'), graphql_name='wave')

    participant_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='participantId')

    rater_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='raterId')

    relationship_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='relationshipId')

    approval = sgqlc.types.Field(sgqlc.types.non_null(Ex360RaterAssignmentApprovalDecision), graphql_name='approval')



class Ex360RaterAssignmentOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'rater_property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    rater_property = sgqlc.types.Field(sgqlc.types.non_null(Ex360RaterProperty), graphql_name='raterProperty')



class Ex360SelectedRaterAssignment(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('participant_id', 'rater_id', 'relationship_id', 'action')
    participant_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='participantId')

    rater_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='raterID')

    relationship_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='relationshipId')

    action = sgqlc.types.Field(sgqlc.types.non_null(Ex360WaveRaterAssignmentAction), graphql_name='action')



class Ex360WaveEnrolledParticipantInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('wave', 'participant_id', 'action')
    wave = sgqlc.types.Field(sgqlc.types.non_null('Ex360WaveRefInput'), graphql_name='wave')

    participant_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='participantId')

    action = sgqlc.types.Field(sgqlc.types.non_null(Ex360WaveEnrolledAction), graphql_name='action')



class Ex360WaveOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(Ex360WaveProperty), graphql_name='property')



class Ex360WaveRefInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('program_id', 'id')
    program_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='programId')

    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')



class ExportConfig(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('encoding', 'date_format', 'date_time_format', 'enumerated_alt_set_format', 'field_name_format', 'max_records', 'excel_template_key', 'spss_attribute_name')
    encoding = sgqlc.types.Field(Encoding, graphql_name='encoding')

    date_format = sgqlc.types.Field(String, graphql_name='dateFormat')

    date_time_format = sgqlc.types.Field(String, graphql_name='dateTimeFormat')

    enumerated_alt_set_format = sgqlc.types.Field(EnumeratedAltSetFormat, graphql_name='enumeratedAltSetFormat')

    field_name_format = sgqlc.types.Field(FieldNameFormat, graphql_name='fieldNameFormat')

    max_records = sgqlc.types.Field(Int, graphql_name='maxRecords')

    excel_template_key = sgqlc.types.Field(String, graphql_name='excelTemplateKey')

    spss_attribute_name = sgqlc.types.Field(FieldNameFormat, graphql_name='spssAttributeName')



class ExportDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('feedback', 'invitation', 'sso_event_stats', 'survey_export_stats', 'feed_files', 'user_activities', 'report', 'missing_urls', 'employee_program_participation', 'aggregation_table', 'aggregation_table_list', 'aggregation_ranked_table', 'phrases')
    feedback = sgqlc.types.Field('FeedbackExport', graphql_name='feedback')

    invitation = sgqlc.types.Field('InvitationExport', graphql_name='invitation')

    sso_event_stats = sgqlc.types.Field('SSOEventStatsExport', graphql_name='ssoEventStats')

    survey_export_stats = sgqlc.types.Field('SurveyExportStatsExport', graphql_name='surveyExportStats')

    feed_files = sgqlc.types.Field('FeedFilesExport', graphql_name='feedFiles')

    user_activities = sgqlc.types.Field('UserActivitiesExport', graphql_name='userActivities')

    report = sgqlc.types.Field('ReportExport', graphql_name='report')

    missing_urls = sgqlc.types.Field('MissingUrlsExport', graphql_name='missingUrls')

    employee_program_participation = sgqlc.types.Field(EmployeeProgramParticipationExport, graphql_name='employeeProgramParticipation')

    aggregation_table = sgqlc.types.Field(AggregationTableExport, graphql_name='aggregationTable')

    aggregation_table_list = sgqlc.types.Field(AggregationTableListExport, graphql_name='aggregationTableList')

    aggregation_ranked_table = sgqlc.types.Field(AggregationRankedTableExport, graphql_name='aggregationRankedTable')

    phrases = sgqlc.types.Field('PhrasesExport', graphql_name='phrases')



class ExportOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'favorite')
    direction = sgqlc.types.Field(OrderDirection, graphql_name='direction')

    favorite = sgqlc.types.Field(Boolean, graphql_name='favorite')



class ExportSchedulingConfigInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('frequency', 'scheduling_time', 'scheduling_timezone')
    frequency = sgqlc.types.Field('ExportSchedulingFrequencyInput', graphql_name='frequency')

    scheduling_time = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='schedulingTime')

    scheduling_timezone = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='schedulingTimezone')



class ExportSchedulingFrequencyInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('daily', 'weekly', 'monthly')
    daily = sgqlc.types.Field(DailyFrequencyInput, graphql_name='daily')

    weekly = sgqlc.types.Field('WeeklyFrequencyInput', graphql_name='weekly')

    monthly = sgqlc.types.Field('MonthlyFrequencyInput', graphql_name='monthly')



class ExternalBenchmarkDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class FeedFilesExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('filter', 'order_by', 'data_view', 'record_fields', 'timeperiod')
    filter = sgqlc.types.Field('Filter', graphql_name='filter')

    order_by = sgqlc.types.Field(sgqlc.types.list_of('RecordOrder'), graphql_name='orderBy')

    data_view = sgqlc.types.Field(DataView, graphql_name='dataView')

    record_fields = sgqlc.types.Field(sgqlc.types.non_null('RecordDataTableDefinition'), graphql_name='recordFields')

    timeperiod = sgqlc.types.Field('TimeperiodFilterInput', graphql_name='timeperiod')



class FeedbackExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('filter', 'order_by', 'data_view', 'record_fields', 'export_config', 'show_excluded', 'include_ad_hoc', 'include_isolated_records_of_type', 'add_translations', 'timeperiod')
    filter = sgqlc.types.Field('Filter', graphql_name='filter')

    order_by = sgqlc.types.Field(sgqlc.types.list_of('RecordOrder'), graphql_name='orderBy')

    data_view = sgqlc.types.Field(DataView, graphql_name='dataView')

    record_fields = sgqlc.types.Field(sgqlc.types.non_null('RecordDataTableDefinition'), graphql_name='recordFields')

    export_config = sgqlc.types.Field(ExportConfig, graphql_name='exportConfig')

    show_excluded = sgqlc.types.Field(Boolean, graphql_name='showExcluded')

    include_ad_hoc = sgqlc.types.Field(Boolean, graphql_name='includeAdHoc')

    include_isolated_records_of_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(IsolatedRecordType)), graphql_name='includeIsolatedRecordsOfType')

    add_translations = sgqlc.types.Field(Boolean, graphql_name='addTranslations')

    timeperiod = sgqlc.types.Field('TimeperiodFilterInput', graphql_name='timeperiod')



class FeedbackRecordAttachmentInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('file_name', 'file_url', 'description')
    file_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fileName')

    file_url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fileUrl')

    description = sgqlc.types.Field(String, graphql_name='description')



class FieldCondition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('program_ids', 'id', 'is_null', 'is_not_null', 'in_', 'not_in', 'lt', 'lte', 'gt', 'gte', 'before', 'on_or_before', 'after', 'on_or_after')
    program_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='programIds')

    id = sgqlc.types.Field(ID, graphql_name='id')

    is_null = sgqlc.types.Field(Boolean, graphql_name='isNull')

    is_not_null = sgqlc.types.Field(Boolean, graphql_name='isNotNull')

    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='in')

    not_in = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='notIn')

    lt = sgqlc.types.Field(Float, graphql_name='lt')

    lte = sgqlc.types.Field(Float, graphql_name='lte')

    gt = sgqlc.types.Field(Float, graphql_name='gt')

    gte = sgqlc.types.Field(Float, graphql_name='gte')

    before = sgqlc.types.Field(DateTime, graphql_name='before')

    on_or_before = sgqlc.types.Field(DateTime, graphql_name='onOrBefore')

    after = sgqlc.types.Field(DateTime, graphql_name='after')

    on_or_after = sgqlc.types.Field(DateTime, graphql_name='onOrAfter')



class FieldContactSegmentationOptions(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('program_ids', 'additional_fields', 'comment_fields_for_topics')
    program_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='programIds')

    additional_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='additionalFields')

    comment_fields_for_topics = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='commentFieldsForTopics')



class FieldDataInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field_id', 'values')
    field_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='fieldId')

    values = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('FieldValue')), graphql_name='values')



class FieldId(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')



class FieldValue(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('value', 'sequence_number')
    value = sgqlc.types.Field(String, graphql_name='value')

    sequence_number = sgqlc.types.Field(Int, graphql_name='sequenceNumber')



class Filter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field_ids', 'in_', 'is_null', 'is_empty', 'has_numeric_value', 'lt', 'lte', 'gt', 'gte', 'contact', 'program', 'secure_filter', 'always', 'topic_filter', 'and_', 'or_', 'not_')
    field_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='fieldIds')

    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='in')

    is_null = sgqlc.types.Field(Boolean, graphql_name='isNull')

    is_empty = sgqlc.types.Field(Boolean, graphql_name='isEmpty')

    has_numeric_value = sgqlc.types.Field(Boolean, graphql_name='hasNumericValue')

    lt = sgqlc.types.Field(String, graphql_name='lt')

    lte = sgqlc.types.Field(String, graphql_name='lte')

    gt = sgqlc.types.Field(String, graphql_name='gt')

    gte = sgqlc.types.Field(String, graphql_name='gte')

    contact = sgqlc.types.Field(ContactFilter, graphql_name='contact')

    program = sgqlc.types.Field('ProgramFilter', graphql_name='program')

    secure_filter = sgqlc.types.Field('SecureFilter', graphql_name='secureFilter')

    always = sgqlc.types.Field(Boolean, graphql_name='always')

    topic_filter = sgqlc.types.Field('Filter', graphql_name='topicFilter')

    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Filter')), graphql_name='and')

    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Filter')), graphql_name='or')

    not_ = sgqlc.types.Field('Filter', graphql_name='not')



class FilteredMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('metric', 'filter')
    metric = sgqlc.types.Field(sgqlc.types.non_null('Metric'), graphql_name='metric')

    filter = sgqlc.types.Field(sgqlc.types.non_null(Filter), graphql_name='filter')



class FormRecordInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('form_id', 'responses')
    form_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='formId')

    responses = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(FieldDataInput)), graphql_name='responses')



class FormattedContactAttribute(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class ForwardResponse(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('response_id', 'to', 'cc', 'subject', 'body', 'include_pdf', 'pdf_url')
    response_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='responseId')

    to = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='to')

    cc = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='cc')

    subject = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='subject')

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='body')

    include_pdf = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='includePDF')

    pdf_url = sgqlc.types.Field(String, graphql_name='pdfUrl')



class GoalAssigneeInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('employee_id', 'segment')
    employee_id = sgqlc.types.Field(ID, graphql_name='employeeId')

    segment = sgqlc.types.Field(EmployeeSegment, graphql_name='segment')



class GoalAssignmentDelta(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('remove', 'add')
    remove = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(GoalAssigneeInput)), graphql_name='remove')

    add = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(GoalAssigneeInput)), graphql_name='add')



class GoalsWaveParticipantOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(GoalsWaveParticipantProperty), graphql_name='property')



class HeaderElementValue(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('property',)
    property = sgqlc.types.Field(sgqlc.types.non_null(HeaderElementBasicProperty), graphql_name='property')



class HourlyFrequencyInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('hours',)
    hours = sgqlc.types.Field(Boolean, graphql_name='hours')



class InsightCondition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('program_ids', 'id', 'in_')
    program_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='programIds')

    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    in_ = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='in')



class InvitationExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('filter', 'order_by', 'data_view', 'record_fields', 'export_config', 'show_excluded', 'include_ad_hoc', 'include_isolated_records_of_type', 'add_translations', 'timeperiod')
    filter = sgqlc.types.Field(Filter, graphql_name='filter')

    order_by = sgqlc.types.Field(sgqlc.types.list_of('RecordOrder'), graphql_name='orderBy')

    data_view = sgqlc.types.Field(DataView, graphql_name='dataView')

    record_fields = sgqlc.types.Field(sgqlc.types.non_null('RecordDataTableDefinition'), graphql_name='recordFields')

    export_config = sgqlc.types.Field(ExportConfig, graphql_name='exportConfig')

    show_excluded = sgqlc.types.Field(Boolean, graphql_name='showExcluded')

    include_ad_hoc = sgqlc.types.Field(Boolean, graphql_name='includeAdHoc')

    include_isolated_records_of_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(IsolatedRecordType)), graphql_name='includeIsolatedRecordsOfType')

    add_translations = sgqlc.types.Field(Boolean, graphql_name='addTranslations')

    timeperiod = sgqlc.types.Field('TimeperiodFilterInput', graphql_name='timeperiod')



class LabeledMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('label', 'metric')
    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')

    metric = sgqlc.types.Field(sgqlc.types.non_null('Metric'), graphql_name='metric')



class LinearRegressionMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('dependent_value', 'independent_value', 'minimum_sample_size')
    dependent_value = sgqlc.types.Field(sgqlc.types.non_null('RecordValueDefinition'), graphql_name='dependentValue')

    independent_value = sgqlc.types.Field(sgqlc.types.non_null('RecordValueDefinition'), graphql_name='independentValue')

    minimum_sample_size = sgqlc.types.Field(Long, graphql_name='minimumSampleSize')



class ManagerAssessmentDecisionInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('participation_id', 'decision')
    participation_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='participationId')

    decision = sgqlc.types.Field(sgqlc.types.non_null(ManagerAssessmentDecision), graphql_name='decision')



class MedalliaBenchmarksInputFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class MedalliaBenchmarksPreviewExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class MedalliaBenchmarksTableDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class MessageCenterRegistrationInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('channel', 'label', 'enabled', 'excluded_message_types', 'destination_identifier')
    channel = sgqlc.types.Field(sgqlc.types.non_null(MessageCenterRegistrationChannel), graphql_name='channel')

    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')

    enabled = sgqlc.types.Field(Boolean, graphql_name='enabled')

    excluded_message_types = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(UserMessageType)), graphql_name='excludedMessageTypes')

    destination_identifier = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='destinationIdentifier')



class MessageCenterSettingsInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('time_zone', 'do_not_disturb_hour_begin', 'do_not_disturb_hour_end', 'show_unread_only')
    time_zone = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='timeZone')

    do_not_disturb_hour_begin = sgqlc.types.Field(String, graphql_name='doNotDisturbHourBegin')

    do_not_disturb_hour_end = sgqlc.types.Field(String, graphql_name='doNotDisturbHourEnd')

    show_unread_only = sgqlc.types.Field(Boolean, graphql_name='showUnreadOnly')



class MessageOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'property')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    property = sgqlc.types.Field(sgqlc.types.non_null(MessageOrderProperty), graphql_name='property')



class Metric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('average', 'sum', 'count', 'custom_calculation', 'custom', 'count_unique', 'bucket_count', 'percentage', 'topic_percentage', 'global_records_topic_percentage', 'topic_impact', 'scaled_topic_impact', 'sentiment_count', 'sentiment_percentage', 'sentiment_net_percentage', 'regression_beta', 'regression_correlation', 'segment_average', 'segment_percentile', 'filtered', 'sum_of_product')
    average = sgqlc.types.Field('RecordValueDefinition', graphql_name='average')

    sum = sgqlc.types.Field('RecordValueDefinition', graphql_name='sum')

    count = sgqlc.types.Field('RecordValueDefinition', graphql_name='count')

    custom_calculation = sgqlc.types.Field(CustomCalculation, graphql_name='customCalculation')

    custom = sgqlc.types.Field(CustomCalculatedField, graphql_name='custom')

    count_unique = sgqlc.types.Field(CountUniqueDefinition, graphql_name='countUnique')

    bucket_count = sgqlc.types.Field(BucketCountDefinition, graphql_name='bucketCount')

    percentage = sgqlc.types.Field(AggregationTablePercentage, graphql_name='percentage')

    topic_percentage = sgqlc.types.Field(AggregationTableEmptyArg, graphql_name='topicPercentage')

    global_records_topic_percentage = sgqlc.types.Field(AggregationTableEmptyArg, graphql_name='globalRecordsTopicPercentage')

    topic_impact = sgqlc.types.Field('Metric', graphql_name='topicImpact')

    scaled_topic_impact = sgqlc.types.Field('Metric', graphql_name='scaledTopicImpact')

    sentiment_count = sgqlc.types.Field(sgqlc.types.list_of(Sentiment), graphql_name='sentimentCount')

    sentiment_percentage = sgqlc.types.Field(sgqlc.types.list_of(Sentiment), graphql_name='sentimentPercentage')

    sentiment_net_percentage = sgqlc.types.Field(AggregationTableEmptyArg, graphql_name='sentimentNetPercentage')

    regression_beta = sgqlc.types.Field(LinearRegressionMetric, graphql_name='regressionBeta')

    regression_correlation = sgqlc.types.Field(LinearRegressionMetric, graphql_name='regressionCorrelation')

    segment_average = sgqlc.types.Field('SegmentAverageMetric', graphql_name='segmentAverage')

    segment_percentile = sgqlc.types.Field('SegmentPercentileMetric', graphql_name='segmentPercentile')

    filtered = sgqlc.types.Field(FilteredMetric, graphql_name='filtered')

    sum_of_product = sgqlc.types.Field('SumOfProductMetric', graphql_name='sumOfProduct')



class MetricCondition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field_id', 'calculation', 'lt', 'lte', 'gt', 'gte')
    field_id = sgqlc.types.Field(ID, graphql_name='fieldId')

    calculation = sgqlc.types.Field(sgqlc.types.non_null(MetricCalculation), graphql_name='calculation')

    lt = sgqlc.types.Field(Float, graphql_name='lt')

    lte = sgqlc.types.Field(Float, graphql_name='lte')

    gt = sgqlc.types.Field(Float, graphql_name='gt')

    gte = sgqlc.types.Field(Float, graphql_name='gte')



class MissingUrlsExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('unit_id', 'source_id', 'sorting')
    unit_id = sgqlc.types.Field(ID, graphql_name='unitId')

    source_id = sgqlc.types.Field(ID, graphql_name='sourceId')

    sorting = sgqlc.types.Field('Sorting', graphql_name='sorting')



class MonthlyFrequencyInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('day_of_month',)
    day_of_month = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='dayOfMonth')



class NestableColumnRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('name', 'segment', 'slices', 'topic_ids', 'rule_topics_level', 'data_topics_level', 'topic_children')
    name = sgqlc.types.Field(String, graphql_name='name')

    segment = sgqlc.types.Field(AggregationTableColumnSegmentRecordSplitAxis, graphql_name='segment')

    slices = sgqlc.types.Field(AggregationTableColumnSlicesRecordSplitAxis, graphql_name='slices')

    topic_ids = sgqlc.types.Field(AggregationTableColumnTopicIdsRecordSplitAxis, graphql_name='topicIds')

    rule_topics_level = sgqlc.types.Field(AggregationTableColumnRuleTopicsLevelRecordSplitAxis, graphql_name='ruleTopicsLevel')

    data_topics_level = sgqlc.types.Field(AggregationTableColumnDataTopicsLevelRecordSplitAxis, graphql_name='dataTopicsLevel')

    topic_children = sgqlc.types.Field(AggregationTableColumnTopicChildrenRecordSplitAxis, graphql_name='topicChildren')



class NestableRowRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('name', 'segment', 'slices', 'topic_ids', 'rule_topics_level', 'data_topics_level', 'topic_children')
    name = sgqlc.types.Field(String, graphql_name='name')

    segment = sgqlc.types.Field(AggregationTableRowSegmentRecordSplitAxis, graphql_name='segment')

    slices = sgqlc.types.Field(AggregationTableRowSlicesRecordSplitAxis, graphql_name='slices')

    topic_ids = sgqlc.types.Field(AggregationTableRowTopicIdsRecordSplitAxis, graphql_name='topicIds')

    rule_topics_level = sgqlc.types.Field(AggregationTableRowRuleTopicsLevelRecordSplitAxis, graphql_name='ruleTopicsLevel')

    data_topics_level = sgqlc.types.Field(AggregationTableRowDataTopicsLevelRecordSplitAxis, graphql_name='dataTopicsLevel')

    topic_children = sgqlc.types.Field(AggregationTableRowTopicChildrenRecordSplitAxis, graphql_name='topicChildren')



class NestingBenchmark(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class NumericFormat(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('decimal_places', 'round_mode')
    decimal_places = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='decimalPlaces')

    round_mode = sgqlc.types.Field(sgqlc.types.non_null(RoundingMode), graphql_name='roundMode')



class OrgHierarchyListFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class OrgHierarchyListFilterParameter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class OrgHierarchyTreeFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class PairInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class PercentageCriteriaInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class PerformanceRatingInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('participation_id', 'performance_rating')
    participation_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='participationId')

    performance_rating = sgqlc.types.Field(sgqlc.types.non_null(FormRecordInput), graphql_name='performanceRating')



class PersonalizedAlertAggregateCriteriaInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class PersonalizedAlertCriteriaInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class PersonalizedAlertFeedbackRecordLevelCriteriaInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class PersonalizedAlertFrequencyInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class PersonalizedAlertInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class PersonalizedAlertsUserConfigurationInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class PhrasesExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('filter', 'order_by', 'data_view', 'comment_fields_ids', 'additional_columns_field_ids', 'score_field_id', 'tagging_filters', 'show_excluded', 'include_ad_hoc', 'add_translations', 'timeperiod')
    filter = sgqlc.types.Field(Filter, graphql_name='filter')

    order_by = sgqlc.types.Field(sgqlc.types.list_of('RecordOrder'), graphql_name='orderBy')

    data_view = sgqlc.types.Field(DataView, graphql_name='dataView')

    comment_fields_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='commentFieldsIds')

    additional_columns_field_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='additionalColumnsFieldIds')

    score_field_id = sgqlc.types.Field(ID, graphql_name='scoreFieldId')

    tagging_filters = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TaggingFilter'))), graphql_name='taggingFilters')

    show_excluded = sgqlc.types.Field(Boolean, graphql_name='showExcluded')

    include_ad_hoc = sgqlc.types.Field(Boolean, graphql_name='includeAdHoc')

    add_translations = sgqlc.types.Field(Boolean, graphql_name='addTranslations')

    timeperiod = sgqlc.types.Field('TimeperiodFilterInput', graphql_name='timeperiod')



class ProgramFieldsIds(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('program_id', 'field_ids')
    program_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='programId')

    field_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds')



class ProgramFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('program_ids', 'schema_ids')
    program_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='programIds')

    schema_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='schemaIds')



class RankedDataDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('benchmark', 'data_view')
    benchmark = sgqlc.types.Field(BenchmarkDefinition, graphql_name='benchmark')

    data_view = sgqlc.types.Field(DataView, graphql_name='dataView')



class RecordDataColumnDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field_id',)
    field_id = sgqlc.types.Field(ID, graphql_name='fieldId')



class RecordDataTableDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('columns',)
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RecordDataColumnDefinition))), graphql_name='columns')



class RecordOrder(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('direction', 'field_id')
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name='direction')

    field_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='fieldId')



class RecordValueDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field',)
    field = sgqlc.types.Field(FieldId, graphql_name='field')



class RegressionOperation(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('dependent_field_id', 'independent_field_ids')
    dependent_field_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='dependentFieldId')

    independent_field_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='independentFieldIds')



class ReportExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('url', 'user_id')
    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='url')

    user_id = sgqlc.types.Field(ID, graphql_name='userId')



class ReporteeSegment(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('employee_ids', 'team_ids', 'query')
    employee_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='employeeIds')

    team_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='teamIds')

    query = sgqlc.types.Field(String, graphql_name='query')



class RuleTopicCondition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('program_ids', 'rule_topics', 'sentiments', 'comment_fields')
    program_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='programIds')

    rule_topics = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ruleTopics')

    sentiments = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(Sentiment)), graphql_name='sentiments')

    comment_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='commentFields')



class SSOEventStatsExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('filter', 'order_by', 'data_view', 'record_fields', 'timeperiod')
    filter = sgqlc.types.Field(Filter, graphql_name='filter')

    order_by = sgqlc.types.Field(sgqlc.types.list_of(RecordOrder), graphql_name='orderBy')

    data_view = sgqlc.types.Field(DataView, graphql_name='dataView')

    record_fields = sgqlc.types.Field(sgqlc.types.non_null(RecordDataTableDefinition), graphql_name='recordFields')

    timeperiod = sgqlc.types.Field('TimeperiodFilterInput', graphql_name='timeperiod')



class Sampling(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('random',)
    random = sgqlc.types.Field(Boolean, graphql_name='random')



class SecureFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('token',)
    token = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='token')



class SegmentAverageMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('segment_field', 'metric')
    segment_field = sgqlc.types.Field(sgqlc.types.non_null(FieldId), graphql_name='segmentField')

    metric = sgqlc.types.Field(sgqlc.types.non_null(Metric), graphql_name='metric')



class SegmentPercentileMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('segment_field', 'metric', 'percentile')
    segment_field = sgqlc.types.Field(sgqlc.types.non_null(FieldId), graphql_name='segmentField')

    metric = sgqlc.types.Field(sgqlc.types.non_null(Metric), graphql_name='metric')

    percentile = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='percentile')



class SignificanceTestConfig(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('minimum_sample_size', 'minimum_absolute_difference', 'significance_level')
    minimum_sample_size = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='minimumSampleSize')

    minimum_absolute_difference = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='minimumAbsoluteDifference')

    significance_level = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='significanceLevel')



class Slice(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'label', 'filter')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')

    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')

    filter = sgqlc.types.Field(sgqlc.types.non_null(Filter), graphql_name='filter')



class SocialAggregateDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('data', 'social_metric')
    data = sgqlc.types.Field(sgqlc.types.non_null('SocialDatasetDefinition'), graphql_name='data')

    social_metric = sgqlc.types.Field(sgqlc.types.non_null('SocialMetric'), graphql_name='socialMetric')



class SocialAggregateTableColumn(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('group', 'key')
    group = sgqlc.types.Field(String, graphql_name='group')

    key = sgqlc.types.Field(String, graphql_name='key')



class SocialAggregateTableDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('data', 'columns', 'column_groups', 'rows', 'row_groups', 'social_metrics', 'social_labeled_metrics')
    data = sgqlc.types.Field(sgqlc.types.non_null('SocialDatasetDefinition'), graphql_name='data')

    columns = sgqlc.types.Field('SocialAggregationTableColumnRecordSplitAxis', graphql_name='columns')

    column_groups = sgqlc.types.Field(sgqlc.types.list_of('SocialAggregationTableColumnRecordSplitAxis'), graphql_name='columnGroups')

    rows = sgqlc.types.Field('SocialAggregationTableRowRecordSplitAxis', graphql_name='rows')

    row_groups = sgqlc.types.Field(sgqlc.types.list_of('SocialAggregationTableRowRecordSplitAxis'), graphql_name='rowGroups')

    social_metrics = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SocialMetric')), graphql_name='socialMetrics')

    social_labeled_metrics = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SocialLabeledMetric')), graphql_name='socialLabeledMetrics')



class SocialAggregateTablePagination(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('limit', 'offset')
    limit = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='limit')

    offset = sgqlc.types.Field(Int, graphql_name='offset')



class SocialAggregateTableRowCell(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('column',)
    column = sgqlc.types.Field(SocialAggregateTableColumn, graphql_name='column')



class SocialAggregateTableRowCellMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'column')
    key = sgqlc.types.Field(String, graphql_name='key')

    column = sgqlc.types.Field(SocialAggregateTableColumn, graphql_name='column')



class SocialAggregateTableRowHaving(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('value', 'non_null', 'positive', 'gte', 'has_samples', 'not_', 'and_', 'or_')
    value = sgqlc.types.Field('SocialAggregateTableRowValue', graphql_name='value')

    non_null = sgqlc.types.Field(Boolean, graphql_name='nonNull')

    positive = sgqlc.types.Field(Boolean, graphql_name='positive')

    gte = sgqlc.types.Field('SocialAggregateTableRowValue', graphql_name='gte')

    has_samples = sgqlc.types.Field(Boolean, graphql_name='hasSamples')

    not_ = sgqlc.types.Field('SocialAggregateTableRowHaving', graphql_name='not')

    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SocialAggregateTableRowHaving')), graphql_name='and')

    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SocialAggregateTableRowHaving')), graphql_name='or')



class SocialAggregateTableRowSortBy(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('value', 'direction')
    value = sgqlc.types.Field(sgqlc.types.non_null('SocialAggregateTableRowValue'), graphql_name='value')

    direction = sgqlc.types.Field(sgqlc.types.non_null(SocialSortByDirection), graphql_name='direction')



class SocialAggregateTableRowValue(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('social_metric', 'count', 'metric_count', 'header', 'int', 'float')
    social_metric = sgqlc.types.Field(SocialAggregateTableRowCellMetric, graphql_name='socialMetric')

    count = sgqlc.types.Field(SocialAggregateTableRowCell, graphql_name='count')

    metric_count = sgqlc.types.Field(SocialAggregateTableRowCellMetric, graphql_name='metricCount')

    header = sgqlc.types.Field('SocialHeaderElementValue', graphql_name='header')

    int = sgqlc.types.Field(Int, graphql_name='int')

    float = sgqlc.types.Field(Float, graphql_name='float')



class SocialAggregationTableColumnHierarchyAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('of', 'name')
    of = sgqlc.types.Field('SocialAggregationTableRowRecordSplitAxis', graphql_name='of')

    name = sgqlc.types.Field(String, graphql_name='name')



class SocialAggregationTableColumnRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('segment', 'slices', 'timeperiods', 'total', 'topic_ids', 'social_topics_level', 'topic_children', 'hierarchy')
    segment = sgqlc.types.Field('SocialAggregationTableColumnSegmentRecordSplitAxis', graphql_name='segment')

    slices = sgqlc.types.Field('SocialAggregationTableColumnSlicesRecordSplitAxis', graphql_name='slices')

    timeperiods = sgqlc.types.Field('SocialAggregationTableColumnTimeperiodsRecordSplitAxis', graphql_name='timeperiods')

    total = sgqlc.types.Field('SocialAggregationTableTotalRecordSplitAxis', graphql_name='total')

    topic_ids = sgqlc.types.Field('SocialAggregationTableColumnTopicIdsRecordSplitAxis', graphql_name='topicIds')

    social_topics_level = sgqlc.types.Field('SocialAggregationTableColumnTopicsLevelRecordSplitAxis', graphql_name='socialTopicsLevel')

    topic_children = sgqlc.types.Field('SocialAggregationTableColumnTopicChildrenRecordSplitAxis', graphql_name='topicChildren')

    hierarchy = sgqlc.types.Field(SocialAggregationTableColumnHierarchyAxis, graphql_name='hierarchy')



class SocialAggregationTableColumnSegmentRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'name')
    field = sgqlc.types.Field(sgqlc.types.non_null('SocialFieldId'), graphql_name='field')

    name = sgqlc.types.Field(String, graphql_name='name')



class SocialAggregationTableColumnSlicesRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('items', 'name')
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SocialSlice'))), graphql_name='items')

    name = sgqlc.types.Field(String, graphql_name='name')



class SocialAggregationTableColumnTimeperiodsRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'start', 'end', 'unit', 'rolling_window', 'name')
    field = sgqlc.types.Field(sgqlc.types.non_null('SocialFieldId'), graphql_name='field')

    start = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='start')

    end = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='end')

    unit = sgqlc.types.Field(sgqlc.types.non_null(SocialTimeGroupingUnit), graphql_name='unit')

    rolling_window = sgqlc.types.Field(Int, graphql_name='rollingWindow')

    name = sgqlc.types.Field(String, graphql_name='name')



class SocialAggregationTableColumnTopicChildrenRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('parent_id', 'name')
    parent_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='parentId')

    name = sgqlc.types.Field(String, graphql_name='name')



class SocialAggregationTableColumnTopicIdsRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('ids', 'name')
    ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='ids')

    name = sgqlc.types.Field(String, graphql_name='name')



class SocialAggregationTableColumnTopicsLevelRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('industries', 'level', 'name')
    industries = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='industries')

    level = sgqlc.types.Field(Int, graphql_name='level')

    name = sgqlc.types.Field(String, graphql_name='name')



class SocialAggregationTableEmptyArg(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('dummy_field',)
    dummy_field = sgqlc.types.Field(String, graphql_name='dummyField')



class SocialAggregationTableRowHierarchyAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('of', 'name', 'sort_by', 'having', 'pagination')
    of = sgqlc.types.Field('SocialAggregationTableRowRecordSplitAxis', graphql_name='of')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(SocialAggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(SocialAggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(SocialAggregateTablePagination, graphql_name='pagination')



class SocialAggregationTableRowRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('segment', 'slices', 'timeperiods', 'total', 'topic_ids', 'social_topics_level', 'topic_children', 'hierarchy')
    segment = sgqlc.types.Field('SocialAggregationTableRowSegmentRecordSplitAxis', graphql_name='segment')

    slices = sgqlc.types.Field('SocialAggregationTableRowSlicesRecordSplitAxis', graphql_name='slices')

    timeperiods = sgqlc.types.Field('SocialAggregationTableRowTimeperiodsRecordSplitAxis', graphql_name='timeperiods')

    total = sgqlc.types.Field('SocialAggregationTableTotalRecordSplitAxis', graphql_name='total')

    topic_ids = sgqlc.types.Field('SocialAggregationTableRowTopicIdsRecordSplitAxis', graphql_name='topicIds')

    social_topics_level = sgqlc.types.Field('SocialAggregationTableRowTopicsLevelRecordSplitAxis', graphql_name='socialTopicsLevel')

    topic_children = sgqlc.types.Field('SocialAggregationTableRowTopicChildrenRecordSplitAxis', graphql_name='topicChildren')

    hierarchy = sgqlc.types.Field(SocialAggregationTableRowHierarchyAxis, graphql_name='hierarchy')



class SocialAggregationTableRowSegmentRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'name', 'sort_by', 'having', 'pagination')
    field = sgqlc.types.Field(sgqlc.types.non_null('SocialFieldId'), graphql_name='field')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(SocialAggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(SocialAggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(SocialAggregateTablePagination, graphql_name='pagination')



class SocialAggregationTableRowSlicesRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('items', 'name', 'sort_by', 'having', 'pagination')
    items = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SocialSlice'))), graphql_name='items')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(SocialAggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(SocialAggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(SocialAggregateTablePagination, graphql_name='pagination')



class SocialAggregationTableRowTimeperiodsRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'start', 'end', 'unit', 'rolling_window', 'name', 'sort_by', 'having', 'pagination')
    field = sgqlc.types.Field(sgqlc.types.non_null('SocialFieldId'), graphql_name='field')

    start = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='start')

    end = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='end')

    unit = sgqlc.types.Field(sgqlc.types.non_null(SocialTimeGroupingUnit), graphql_name='unit')

    rolling_window = sgqlc.types.Field(Int, graphql_name='rollingWindow')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(SocialAggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(SocialAggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(SocialAggregateTablePagination, graphql_name='pagination')



class SocialAggregationTableRowTopicChildrenRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('parent_id', 'name', 'sort_by', 'having', 'pagination')
    parent_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='parentId')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(SocialAggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(SocialAggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(SocialAggregateTablePagination, graphql_name='pagination')



class SocialAggregationTableRowTopicIdsRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('ids', 'name', 'sort_by', 'having', 'pagination')
    ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='ids')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(SocialAggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(SocialAggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(SocialAggregateTablePagination, graphql_name='pagination')



class SocialAggregationTableRowTopicsLevelRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('industries', 'level', 'name', 'sort_by', 'having', 'pagination')
    industries = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='industries')

    level = sgqlc.types.Field(Int, graphql_name='level')

    name = sgqlc.types.Field(String, graphql_name='name')

    sort_by = sgqlc.types.Field(sgqlc.types.list_of(SocialAggregateTableRowSortBy), graphql_name='sortBy')

    having = sgqlc.types.Field(SocialAggregateTableRowHaving, graphql_name='having')

    pagination = sgqlc.types.Field(SocialAggregateTablePagination, graphql_name='pagination')



class SocialAggregationTableTotalRecordSplitAxis(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('name',)
    name = sgqlc.types.Field(String, graphql_name='name')



class SocialDatasetDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('filter',)
    filter = sgqlc.types.Field('SocialFilter', graphql_name='filter')



class SocialFieldId(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id',)
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')



class SocialFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field_ids', 'in_', 'is_null', 'is_empty', 'lt', 'lte', 'gt', 'gte', 'always', 'any_subrecord', 'and_', 'or_', 'not_')
    field_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='fieldIds')

    in_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='in')

    is_null = sgqlc.types.Field(Boolean, graphql_name='isNull')

    is_empty = sgqlc.types.Field(Boolean, graphql_name='isEmpty')

    lt = sgqlc.types.Field(String, graphql_name='lt')

    lte = sgqlc.types.Field(String, graphql_name='lte')

    gt = sgqlc.types.Field(String, graphql_name='gt')

    gte = sgqlc.types.Field(String, graphql_name='gte')

    always = sgqlc.types.Field(Boolean, graphql_name='always')

    any_subrecord = sgqlc.types.Field('SocialFilter', graphql_name='anySubrecord')

    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SocialFilter')), graphql_name='and')

    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SocialFilter')), graphql_name='or')

    not_ = sgqlc.types.Field('SocialFilter', graphql_name='not')



class SocialHeaderElementValue(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('property',)
    property = sgqlc.types.Field(sgqlc.types.non_null(SocialHeaderElementBasicProperty), graphql_name='property')



class SocialLabeledMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('label', 'social_metric')
    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')

    social_metric = sgqlc.types.Field(sgqlc.types.non_null('SocialMetric'), graphql_name='socialMetric')



class SocialMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('average', 'sum', 'count', 'top_box', 'topic_percentage', 'topic_impact', 'scaled_topic_impact', 'sentiment_count', 'sentiment_percentage', 'sentiment_net_percentage')
    average = sgqlc.types.Field('SocialRecordValueDefinition', graphql_name='average')

    sum = sgqlc.types.Field('SocialRecordValueDefinition', graphql_name='sum')

    count = sgqlc.types.Field('SocialRecordValueDefinition', graphql_name='count')

    top_box = sgqlc.types.Field('SocialTopBoxDefinition', graphql_name='topBox')

    topic_percentage = sgqlc.types.Field(SocialAggregationTableEmptyArg, graphql_name='topicPercentage')

    topic_impact = sgqlc.types.Field('SocialMetric', graphql_name='topicImpact')

    scaled_topic_impact = sgqlc.types.Field('SocialMetric', graphql_name='scaledTopicImpact')

    sentiment_count = sgqlc.types.Field(sgqlc.types.list_of(SocialReviewsSentiment), graphql_name='sentimentCount')

    sentiment_percentage = sgqlc.types.Field(sgqlc.types.list_of(SocialReviewsSentiment), graphql_name='sentimentPercentage')

    sentiment_net_percentage = sgqlc.types.Field(SocialAggregationTableEmptyArg, graphql_name='sentimentNetPercentage')



class SocialRecordValueDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field',)
    field = sgqlc.types.Field(SocialFieldId, graphql_name='field')



class SocialSlice(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'label', 'filter')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')

    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')

    filter = sgqlc.types.Field(sgqlc.types.non_null(SocialFilter), graphql_name='filter')



class SocialTopBoxDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'sub_set_range', 'whole_set_range')
    field = sgqlc.types.Field(sgqlc.types.non_null(SocialFieldId), graphql_name='field')

    sub_set_range = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='subSetRange')

    whole_set_range = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='wholeSetRange')



class Sorting(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'direction')
    field = sgqlc.types.Field(sgqlc.types.non_null(SortingField), graphql_name='field')

    direction = sgqlc.types.Field(sgqlc.types.non_null(SortingDirection), graphql_name='direction')



class SplitColumnNesting(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('subtotal', 'segment', 'slices', 'timeperiods')
    subtotal = sgqlc.types.Field(NestingSubtotal, graphql_name='subtotal')

    segment = sgqlc.types.Field(AggregationTableColumnSegmentRecordSplitAxis, graphql_name='segment')

    slices = sgqlc.types.Field(AggregationTableColumnSlicesRecordSplitAxis, graphql_name='slices')

    timeperiods = sgqlc.types.Field(AggregationTableColumnTimeperiodsRecordSplitAxis, graphql_name='timeperiods')



class SubSampling(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('k', 'n')
    k = sgqlc.types.Field(Int, graphql_name='k')

    n = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='n')



class SumOfProductMetric(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('field1', 'field2')
    field1 = sgqlc.types.Field(sgqlc.types.non_null(FieldId), graphql_name='field1')

    field2 = sgqlc.types.Field(sgqlc.types.non_null(FieldId), graphql_name='field2')



class SurveyExportStatsExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('filter', 'order_by', 'data_view', 'record_fields', 'timeperiod')
    filter = sgqlc.types.Field(Filter, graphql_name='filter')

    order_by = sgqlc.types.Field(sgqlc.types.list_of(RecordOrder), graphql_name='orderBy')

    data_view = sgqlc.types.Field(DataView, graphql_name='dataView')

    record_fields = sgqlc.types.Field(sgqlc.types.non_null(RecordDataTableDefinition), graphql_name='recordFields')

    timeperiod = sgqlc.types.Field('TimeperiodFilterInput', graphql_name='timeperiod')



class TaggingFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('topic_type', 'tagpools', 'topics', 'co_occurring_topic', 'co_occurring_topic_type', 'co_occurring_level', 'sentiments', 'comment_fields', 'translation_type', 'level', 'exact_level', 'personas', 'search', 'text_analytics_matching')
    topic_type = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='topicType')

    tagpools = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='tagpools')

    topics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='topics')

    co_occurring_topic = sgqlc.types.Field(String, graphql_name='coOccurringTopic')

    co_occurring_topic_type = sgqlc.types.Field(String, graphql_name='coOccurringTopicType')

    co_occurring_level = sgqlc.types.Field(Int, graphql_name='coOccurringLevel')

    sentiments = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='sentiments')

    comment_fields = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='commentFields')

    translation_type = sgqlc.types.Field(String, graphql_name='translationType')

    level = sgqlc.types.Field(Int, graphql_name='level')

    exact_level = sgqlc.types.Field(Boolean, graphql_name='exactLevel')

    personas = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='personas')

    search = sgqlc.types.Field(String, graphql_name='search')

    text_analytics_matching = sgqlc.types.Field(MatchingMode, graphql_name='textAnalyticsMatching')



class TestsInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('chi_squared', 't_test', 'z_test')
    chi_squared = sgqlc.types.Field(Boolean, graphql_name='chiSquared')

    t_test = sgqlc.types.Field(Boolean, graphql_name='tTest')

    z_test = sgqlc.types.Field(Boolean, graphql_name='zTest')



class ThresholdCriteriaInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class TimeperiodFilterInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'field_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    field_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='fieldId')



class TopicTaggingFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('tagpools', 'topics', 'co_occurring_topic', 'co_occurring_topic_type', 'co_occurring_level', 'sentiments', 'comment_fields', 'translation_type', 'level', 'exact_level', 'personas', 'search')
    tagpools = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='tagpools')

    topics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='topics')

    co_occurring_topic = sgqlc.types.Field(String, graphql_name='coOccurringTopic')

    co_occurring_topic_type = sgqlc.types.Field(String, graphql_name='coOccurringTopicType')

    co_occurring_level = sgqlc.types.Field(Int, graphql_name='coOccurringLevel')

    sentiments = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='sentiments')

    comment_fields = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='commentFields')

    translation_type = sgqlc.types.Field(String, graphql_name='translationType')

    level = sgqlc.types.Field(Int, graphql_name='level')

    exact_level = sgqlc.types.Field(Boolean, graphql_name='exactLevel')

    personas = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='personas')

    search = sgqlc.types.Field(String, graphql_name='search')



class UnitDataFieldFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'in_')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')

    in_ = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='in')



class UnitFilter(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('and_', 'or_', 'field', 'unit_groups')
    and_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UnitFilter')), graphql_name='and')

    or_ = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UnitFilter')), graphql_name='or')

    field = sgqlc.types.Field(UnitDataFieldFilter, graphql_name='field')

    unit_groups = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='unitGroups')



class UserActivitiesExport(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('filter', 'order_by', 'data_view', 'record_fields', 'timeperiod')
    filter = sgqlc.types.Field(Filter, graphql_name='filter')

    order_by = sgqlc.types.Field(sgqlc.types.list_of(RecordOrder), graphql_name='orderBy')

    data_view = sgqlc.types.Field(DataView, graphql_name='dataView')

    record_fields = sgqlc.types.Field(sgqlc.types.non_null(RecordDataTableDefinition), graphql_name='recordFields')

    timeperiod = sgqlc.types.Field(TimeperiodFilterInput, graphql_name='timeperiod')



class ValueCalculationsInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('count', 'percentage_of_row', 'percentage_of_column')
    count = sgqlc.types.Field(Boolean, graphql_name='count')

    percentage_of_row = sgqlc.types.Field(Boolean, graphql_name='percentageOfRow')

    percentage_of_column = sgqlc.types.Field(Boolean, graphql_name='percentageOfColumn')



class WatchlistFilters(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ()


class WeeklyFrequencyInput(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('day',)
    day = sgqlc.types.Field(sgqlc.types.non_null(DayOfWeek), graphql_name='day')



class WordCloudConfiguration(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('score_field', 'negative_threshold', 'positive_threshold', 'use_raw_frequency', 'include_non_english_words', 'include_translated_data', 'limit_number_of_words')
    score_field = sgqlc.types.Field(FieldId, graphql_name='scoreField')

    negative_threshold = sgqlc.types.Field(Float, graphql_name='negativeThreshold')

    positive_threshold = sgqlc.types.Field(Float, graphql_name='positiveThreshold')

    use_raw_frequency = sgqlc.types.Field(Boolean, graphql_name='useRawFrequency')

    include_non_english_words = sgqlc.types.Field(Boolean, graphql_name='includeNonEnglishWords')

    include_translated_data = sgqlc.types.Field(Boolean, graphql_name='includeTranslatedData')

    limit_number_of_words = sgqlc.types.Field(Int, graphql_name='limitNumberOfWords')



class XStatsOperation(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('description', 'correlation', 'regression')
    description = sgqlc.types.Field(DescribeOperation, graphql_name='description')

    correlation = sgqlc.types.Field(CorrelationOperation, graphql_name='correlation')

    regression = sgqlc.types.Field(RegressionOperation, graphql_name='regression')



class XStatsWorkbenchDefinition(sgqlc.types.Input):
    __schema__ = medallia_schema
    __field_names__ = ('filter', 'data_view', 'include_isolated_records_of_type', 'timeperiod')
    filter = sgqlc.types.Field(Filter, graphql_name='filter')

    data_view = sgqlc.types.Field(DataView, graphql_name='dataView')

    include_isolated_records_of_type = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(IsolatedRecordType)), graphql_name='includeIsolatedRecordsOfType')

    timeperiod = sgqlc.types.Field(TimeperiodFilterInput, graphql_name='timeperiod')




########################################################################
# Output Objects and Interfaces
########################################################################
class ActionPlan(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanAttachment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanAttachmentLink(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanField(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanFieldConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanGroup(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanGroupFilteringConfig(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanGroupMetricTable(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanImpactAnalysis(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanImpactMetric(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanMetricConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanMetricData(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanMetricOption(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanNumberFormatConfig(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanStatusConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanStatusOption(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanTask(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanTaskConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanTaskUpsertResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanUpsertError(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('message',)
    message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='message')



class ActionPlanUpsertResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionableTagging(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('region', 'is_actionable')
    region = sgqlc.types.Field(sgqlc.types.non_null('TextRegion'), graphql_name='region')

    is_actionable = sgqlc.types.Field(Boolean, graphql_name='isActionable')



class Activity(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'source', 'title', 'content', 'timestamp', 'attachment_name', 'attachment_link', 'author', 'author_role')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    source = sgqlc.types.Field(sgqlc.types.non_null(ActivitySource), graphql_name='source')

    title = sgqlc.types.Field(String, graphql_name='title')

    content = sgqlc.types.Field(String, graphql_name='content')

    timestamp = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='timestamp')

    attachment_name = sgqlc.types.Field(String, graphql_name='attachmentName')

    attachment_link = sgqlc.types.Field(String, graphql_name='attachmentLink')

    author = sgqlc.types.Field('User', graphql_name='author')

    author_role = sgqlc.types.Field('Role', graphql_name='authorRole')



class ActivityConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Activity))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class AggregatedAction(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class AggregatedActionsConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class AggregationFormattedTable(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('formatted_header_rows', 'formatted_rows', 'formatted_footer_rows', 'formatted_rows_width')
    formatted_header_rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='formattedHeaderRows')

    formatted_rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='formattedRows')

    formatted_footer_rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='formattedFooterRows')

    formatted_rows_width = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='formattedRowsWidth')



class AggregationKey(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('value', 'label')
    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='value')

    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')



class AggregationRank(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'rank', 'total_elements', 'samples', 'metric_value', 'count', 'survey_count', 'is_valid')
    key = sgqlc.types.Field(AggregationKey, graphql_name='key')

    rank = sgqlc.types.Field(Int, graphql_name='rank')

    total_elements = sgqlc.types.Field(Int, graphql_name='totalElements')

    samples = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('AggregationRankSample')), graphql_name='samples')

    metric_value = sgqlc.types.Field(Float, graphql_name='metricValue')

    count = sgqlc.types.Field(Int, graphql_name='count')

    survey_count = sgqlc.types.Field(Long, graphql_name='surveyCount')

    is_valid = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isValid')



class AggregationRankSample(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('rank', 'count', 'survey_count', 'metric_value')
    rank = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='rank')

    count = sgqlc.types.Field(Long, graphql_name='count')

    survey_count = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='surveyCount')

    metric_value = sgqlc.types.Field(Float, graphql_name='metricValue')



class AggregationTable(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('columns', 'column_keys', 'column_labels', 'column_field_data_list', 'row_field_data_list', 'total_columns', 'rows', 'row_keys', 'row_labels', 'total_rows', 'metrics', 'metric_keys', 'metric_labels', 'metrics_table', 'metric_table', 'metrics_table_visibility', 'metric_table_visibility', 'metrics_table_cell_status', 'metric_table_cell_status', 'counts_table', 'metrics_count_table', 'metric_count_table', 'cross_columns_significance_test_table', 'chi_square_test_table', 'cross_columns_significance_test_table_list', 'formatted_table')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('HeaderElement'))), graphql_name='columns')

    column_keys = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(SplitElementId))), graphql_name='columnKeys')

    column_labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(SplitElementId))), graphql_name='columnLabels')

    column_field_data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('FieldData')), graphql_name='columnFieldDataList')

    row_field_data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('FieldData')), graphql_name='rowFieldDataList')

    total_columns = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalColumns')

    rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('HeaderElement'))), graphql_name='rows')

    row_keys = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(SplitElementId))), graphql_name='rowKeys')

    row_labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(SplitElementId))), graphql_name='rowLabels')

    total_rows = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalRows')

    metrics = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('MetricHeaderElement')), graphql_name='metrics')

    metric_keys = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='metricKeys')

    metric_labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='metricLabels')

    metrics_table = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(Float)))))), graphql_name='metricsTable')

    metric_table = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(Float)))), graphql_name='metricTable', args=sgqlc.types.ArgDict((
        ('index', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='index', default=None)),
))
    )
    '''Arguments:

    * `index` (`Int!`)
    '''

    metrics_table_visibility = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Boolean))))))), graphql_name='metricsTableVisibility')

    metric_table_visibility = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(Boolean)))), graphql_name='metricTableVisibility', args=sgqlc.types.ArgDict((
        ('index', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='index', default=None)),
))
    )
    '''Arguments:

    * `index` (`Int!`)
    '''

    metrics_table_cell_status = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CellStatus))))))), graphql_name='metricsTableCellStatus')

    metric_table_cell_status = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(CellStatus)))), graphql_name='metricTableCellStatus', args=sgqlc.types.ArgDict((
        ('index', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='index', default=None)),
))
    )
    '''Arguments:

    * `index` (`Int!`)
    '''

    counts_table = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(Long)))), graphql_name='countsTable')

    metrics_count_table = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(Long)))))), graphql_name='metricsCountTable')

    metric_count_table = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(Long)))), graphql_name='metricCountTable', args=sgqlc.types.ArgDict((
        ('index', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='index', default=None)),
))
    )
    '''Arguments:

    * `index` (`Int!`)
    '''

    cross_columns_significance_test_table = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of('SignificanceTestResult')))))), graphql_name='crossColumnsSignificanceTestTable', args=sgqlc.types.ArgDict((
        ('comparison_strategy', sgqlc.types.Arg(sgqlc.types.non_null(SignificanceTestComparisonStrategy), graphql_name='comparisonStrategy', default=None)),
        ('config', sgqlc.types.Arg(sgqlc.types.non_null(SignificanceTestConfig), graphql_name='config', default=None)),
        ('column_group', sgqlc.types.Arg(sgqlc.types.non_null(String), graphql_name='columnGroup', default=None)),
))
    )
    '''Arguments:

    * `comparison_strategy` (`SignificanceTestComparisonStrategy!`)
    * `config` (`SignificanceTestConfig!`)
    * `column_group` (`String!`)
    '''

    chi_square_test_table = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of('ChiSquareTestResult')))), graphql_name='chiSquareTestTable')

    cross_columns_significance_test_table_list = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of('SignificanceTestResult'))))))), graphql_name='crossColumnsSignificanceTestTableList', args=sgqlc.types.ArgDict((
        ('comparison_strategy', sgqlc.types.Arg(sgqlc.types.non_null(SignificanceTestComparisonStrategy), graphql_name='comparisonStrategy', default=None)),
        ('config', sgqlc.types.Arg(sgqlc.types.non_null(SignificanceTestConfig), graphql_name='config', default=None)),
        ('column_groups', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='columnGroups', default=None)),
))
    )
    '''Arguments:

    * `comparison_strategy` (`SignificanceTestComparisonStrategy!`)
    * `config` (`SignificanceTestConfig!`)
    * `column_groups` (`[String!]!`)
    '''

    formatted_table = sgqlc.types.Field(sgqlc.types.non_null(AggregationFormattedTable), graphql_name='formattedTable', args=sgqlc.types.ArgDict((
        ('format', sgqlc.types.Arg(sgqlc.types.non_null(AggregationTableFormat), graphql_name='format', default=None)),
))
    )
    '''Arguments:

    * `format` (`AggregationTableFormat!`)
    '''



class Alert(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'next_deadline', 'next_deadline_with_zone', 'assignee', 'workflow', 'status', 'allowed_status_changes', 'actions')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    next_deadline = sgqlc.types.Field(DateTime, graphql_name='nextDeadline')

    next_deadline_with_zone = sgqlc.types.Field('ZoneDateTime', graphql_name='nextDeadlineWithZone')

    assignee = sgqlc.types.Field('AlertAssignee', graphql_name='assignee')

    workflow = sgqlc.types.Field('AlertWorkflow', graphql_name='workflow')

    status = sgqlc.types.Field('AlertStatus', graphql_name='status')

    allowed_status_changes = sgqlc.types.Field(sgqlc.types.list_of('AlertStatus'), graphql_name='allowedStatusChanges')

    actions = sgqlc.types.Field(sgqlc.types.non_null('AlertActions'), graphql_name='actions')



class AlertActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('put_alert_workflow', 'put_assign_alert', 'put_update_status')
    put_alert_workflow = sgqlc.types.Field(URI, graphql_name='putAlertWorkflow')

    put_assign_alert = sgqlc.types.Field(URI, graphql_name='putAssignAlert')

    put_update_status = sgqlc.types.Field(URI, graphql_name='putUpdateStatus')



class AlertAssignableGroup(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'role', 'individually_assignable', 'individually_assignable_users')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    role = sgqlc.types.Field(sgqlc.types.non_null('Role'), graphql_name='role')

    individually_assignable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='individuallyAssignable')

    individually_assignable_users = sgqlc.types.Field('UserConnection', graphql_name='individuallyAssignableUsers', args=sgqlc.types.ArgDict((
        ('record_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='recordId', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('search', sgqlc.types.Arg(String, graphql_name='search', default=None)),
))
    )
    '''Arguments:

    * `record_id` (`ID!`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `search` (`String`)
    '''



class AlertAssignableGroupConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AlertAssignableGroup))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class AlertAssignee(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('group', 'owner')
    group = sgqlc.types.Field(sgqlc.types.non_null(AlertAssignableGroup), graphql_name='group')

    owner = sgqlc.types.Field('User', graphql_name='owner')



class AlertStatus(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'label', 'active', 'icon')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')

    active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='active')

    icon = sgqlc.types.Field(String, graphql_name='icon')



class AlertType(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class AlertTypeConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class AlertWorkflow(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'brief_name', 'description')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    brief_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='briefName')

    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='description')



class Anova(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ApplicationTypeConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class ApplicationTypeContainer(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class AskNowConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class AskNowTest(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'status', 'short_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    status = sgqlc.types.Field(sgqlc.types.non_null(AskNowTestStatus), graphql_name='status')

    short_id = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='shortId')



class AssessmentEvent(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class AssessmentWave(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class AssessmentWaveConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class AssessmentWaveParticipation(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class AssessmentWaveParticipationConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class AsyncRequest(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class AsyncResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class AsyncTask(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ()


class AsyncTaskConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class Attachment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Attribute(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'name', 'type', 'contains_pii')
    key = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='key')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    type = sgqlc.types.Field(sgqlc.types.non_null(DataType), graphql_name='type')

    contains_pii = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='containsPii')



class AttributeConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Attribute))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class AttributeData(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('attribute', 'values', 'labels')
    attribute = sgqlc.types.Field(sgqlc.types.non_null(Attribute), graphql_name='attribute')

    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='values')

    labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='labels')



class AvailabilityWindow(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Benchmark(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class CachedDataInfo(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Case(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class CaseActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class CaseManagementColumn(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class CaseManagementField(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class CategoricalOption(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class CategoricalOptionLinearRegressionField(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class CategoricalOptionLogisticRegressionField(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ChiSquareTestResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('score', 'p_value', 'degrees_of_freedom')
    score = sgqlc.types.Field(Float, graphql_name='score')

    p_value = sgqlc.types.Field(Float, graphql_name='pValue')

    degrees_of_freedom = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='degreesOfFreedom')



class ChiSquared(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ClosedLoopMessageResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Comment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'user', 'entity_id', 'timestamp', 'is_edited', 'content', 'mentions', 'unit_mentions')
    id = sgqlc.types.Field(ID, graphql_name='id')

    user = sgqlc.types.Field(sgqlc.types.non_null('User'), graphql_name='user')

    entity_id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='entityId')

    timestamp = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='timestamp')

    is_edited = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isEdited')

    content = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='content')

    mentions = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('User')), graphql_name='mentions')

    unit_mentions = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Unit')), graphql_name='unitMentions')



class CommentActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class CommentConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count', 'comment_actions')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Comment))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')

    comment_actions = sgqlc.types.Field(sgqlc.types.non_null(CommentActions), graphql_name='commentActions')



class CommentFieldDataActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('post_edit_sentiment_taggings', 'post_edit_rule_topic_taggings', 'put_edit_manual_translations', 'post_edit_pii_taggings', 'post_edit_aggregated_action_taggings', 'post_edit_actionable_taggings')
    post_edit_sentiment_taggings = sgqlc.types.Field(URI, graphql_name='postEditSentimentTaggings')

    post_edit_rule_topic_taggings = sgqlc.types.Field(URI, graphql_name='postEditRuleTopicTaggings')

    put_edit_manual_translations = sgqlc.types.Field(URI, graphql_name='putEditManualTranslations')

    post_edit_pii_taggings = sgqlc.types.Field(URI, graphql_name='postEditPiiTaggings')

    post_edit_aggregated_action_taggings = sgqlc.types.Field(URI, graphql_name='postEditAggregatedActionTaggings')

    post_edit_actionable_taggings = sgqlc.types.Field(URI, graphql_name='postEditActionableTaggings')



class ComplexQuery(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ComplexQueryConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class Contact(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'email', 'firstname', 'lastname', 'phone', 'data', 'data_list', 'value', 'values', 'value_list', 'values_list', 'feedback', 'events', 'invitations', 'aggregate', 'aggregate_list', 'aggregate_table', 'aggregate_table_list')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    email = sgqlc.types.Field(String, graphql_name='email')

    firstname = sgqlc.types.Field(String, graphql_name='firstname')

    lastname = sgqlc.types.Field(String, graphql_name='lastname')

    phone = sgqlc.types.Field(String, graphql_name='phone')

    data = sgqlc.types.Field('ContactData', graphql_name='data', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(sgqlc.types.non_null(AttributeSource), graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource!`)
    '''

    data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('ContactData')), graphql_name='dataList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''

    value = sgqlc.types.Field(String, graphql_name='value', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    values = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='values', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    value_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='valueList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='valuesList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    feedback = sgqlc.types.Field(sgqlc.types.non_null('FeedbackConnection'), graphql_name='feedback', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(Filter, graphql_name='filter', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('order_by', sgqlc.types.Arg(sgqlc.types.list_of(RecordOrder), graphql_name='orderBy', default=None)),
        ('show_excluded', sgqlc.types.Arg(Boolean, graphql_name='showExcluded', default=False)),
        ('include_ad_hoc', sgqlc.types.Arg(Boolean, graphql_name='includeAdHoc', default=False)),
        ('include_isolated_records_of_type', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(IsolatedRecordType)), graphql_name='includeIsolatedRecordsOfType', default=None)),
))
    )
    '''Arguments:

    * `filter` (`Filter`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `order_by` (`[RecordOrder]`)
    * `show_excluded` (`Boolean`) (default: `false`)
    * `include_ad_hoc` (`Boolean`) (default: `false`)
    * `include_isolated_records_of_type` (`[IsolatedRecordType!]`)
    '''

    events = sgqlc.types.Field(sgqlc.types.non_null('EventConnection'), graphql_name='events', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(Filter, graphql_name='filter', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('schemas', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='schemas', default=None)),
        ('include_ad_hoc', sgqlc.types.Arg(Boolean, graphql_name='includeAdHoc', default=False)),
))
    )
    '''Arguments:

    * `filter` (`Filter`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `schemas` (`[ID!]`)
    * `include_ad_hoc` (`Boolean`) (default: `false`)
    '''

    invitations = sgqlc.types.Field(sgqlc.types.non_null('InvitationConnection'), graphql_name='invitations', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(Filter, graphql_name='filter', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('order_by', sgqlc.types.Arg(sgqlc.types.list_of(RecordOrder), graphql_name='orderBy', default=None)),
        ('include_ad_hoc', sgqlc.types.Arg(Boolean, graphql_name='includeAdHoc', default=False)),
        ('include_isolated_records_of_type', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(IsolatedRecordType)), graphql_name='includeIsolatedRecordsOfType', default=None)),
))
    )
    '''Arguments:

    * `filter` (`Filter`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `order_by` (`[RecordOrder]`)
    * `include_ad_hoc` (`Boolean`) (default: `false`)
    * `include_isolated_records_of_type` (`[IsolatedRecordType!]`)
    '''

    aggregate = sgqlc.types.Field(Float, graphql_name='aggregate', args=sgqlc.types.ArgDict((
        ('definition', sgqlc.types.Arg(sgqlc.types.non_null(AggregateDefinition), graphql_name='definition', default=None)),
        ('batch_key', sgqlc.types.Arg(String, graphql_name='batchKey', default=None)),
))
    )
    '''Arguments:

    * `definition` (`AggregateDefinition!`)
    * `batch_key` (`String`)
    '''

    aggregate_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Float)), graphql_name='aggregateList', args=sgqlc.types.ArgDict((
        ('definition', sgqlc.types.Arg(AggregateListDefinition, graphql_name='definition', default=None)),
        ('definitions', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AggregateDefinition)), graphql_name='definitions', default=None)),
        ('batch_keys', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='batchKeys', default=None)),
))
    )
    '''Arguments:

    * `definition` (`AggregateListDefinition`)
    * `definitions` (`[AggregateDefinition!]`)
    * `batch_keys` (`[String!]`)
    '''

    aggregate_table = sgqlc.types.Field(AggregationTable, graphql_name='aggregateTable', args=sgqlc.types.ArgDict((
        ('definition', sgqlc.types.Arg(sgqlc.types.non_null(AggregateTableDefinition), graphql_name='definition', default=None)),
        ('batch_key', sgqlc.types.Arg(String, graphql_name='batchKey', default=None)),
        ('optimization', sgqlc.types.Arg(Boolean, graphql_name='optimization', default=None)),
))
    )
    '''Arguments:

    * `definition` (`AggregateTableDefinition!`)
    * `batch_key` (`String`)
    * `optimization` (`Boolean`)
    '''

    aggregate_table_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(AggregationTable)), graphql_name='aggregateTableList', args=sgqlc.types.ArgDict((
        ('definitions', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AggregateTableDefinition)), graphql_name='definitions', default=None)),
        ('batch_keys', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='batchKeys', default=None)),
        ('optimization', sgqlc.types.Arg(Boolean, graphql_name='optimization', default=None)),
))
    )
    '''Arguments:

    * `definitions` (`[AggregateTableDefinition!]`)
    * `batch_keys` (`[String!]`)
    * `optimization` (`Boolean`)
    '''



class ContactAttribute(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'name', 'type', 'contains_pii', 'is_key', 'is_indexed', 'supports_text_search')
    key = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='key')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    type = sgqlc.types.Field(sgqlc.types.non_null(DataType), graphql_name='type')

    contains_pii = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='containsPii')

    is_key = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isKey')

    is_indexed = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isIndexed')

    supports_text_search = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='supportsTextSearch')



class ContactAttributeConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ContactAttribute))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class ContactData(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('attribute', 'values')
    attribute = sgqlc.types.Field(sgqlc.types.non_null(ContactAttribute), graphql_name='attribute')

    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='values')



class ContactSchema(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'attributes')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    attributes = sgqlc.types.Field(ContactAttributeConnection, graphql_name='attributes', args=sgqlc.types.ArgDict((
        ('keys', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='keys', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('data_types', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(DataType)), graphql_name='dataTypes', default=None)),
        ('q', sgqlc.types.Arg(String, graphql_name='q', default=None)),
        ('is_key', sgqlc.types.Arg(Boolean, graphql_name='isKey', default=None)),
))
    )
    '''Arguments:

    * `keys` (`[ID!]`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `data_types` (`[DataType!]`)
    * `q` (`String`)
    * `is_key` (`Boolean`)
    '''



class ContactSegment(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'creation_time', 'rules', 'display_attributes', 'data_view_id', 'snapshot', 'export', 'status', 'available_actions')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    creation_time = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='creationTime')

    rules = sgqlc.types.Field(sgqlc.types.non_null(Rule), graphql_name='rules')

    display_attributes = sgqlc.types.Field(sgqlc.types.non_null('ContactSegmentDisplayAttributes'), graphql_name='displayAttributes')

    data_view_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='dataViewId')

    snapshot = sgqlc.types.Field(sgqlc.types.non_null('ContactSegmentDataSnapshot'), graphql_name='snapshot')

    export = sgqlc.types.Field('Export', graphql_name='export')

    status = sgqlc.types.Field(sgqlc.types.non_null(ContactSegmentStatus), graphql_name='status')

    available_actions = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ContactSegmentAction)), graphql_name='availableActions')



class ContactSegmentDataSnapshot(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ContactSegmentDisplayAttributes(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ContactSegmentSizeEstimation(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ContactSegmentsConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class ContactsConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Contact))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')



class Conversation(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ConversationsBlackoutAndAvailability(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class CrosstabSavedFilter(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'creator_id', 'is_default', 'name', 'module_uuid', 'columns', 'rows', 'value_calculations', 'tests')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    creator_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='creatorId')

    is_default = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isDefault')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    module_uuid = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='moduleUuid')

    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))))), graphql_name='columns')

    rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='rows')

    value_calculations = sgqlc.types.Field(sgqlc.types.non_null('ValueCalculations'), graphql_name='valueCalculations')

    tests = sgqlc.types.Field(sgqlc.types.non_null('Tests'), graphql_name='tests')



class CuePoint(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class CustomerEffortTagging(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('customer_effort', 'regions')
    customer_effort = sgqlc.types.Field(CustomerEffortTaggingCategory, graphql_name='customerEffort')

    regions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TextRegion'))), graphql_name='regions')



class DailyFrequency(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class DataTopic(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')



class DataTopicConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class DataTopicTagging(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('topic', 'persona', 'regions', 'phrases')
    topic = sgqlc.types.Field(DataTopic, graphql_name='topic')

    persona = sgqlc.types.Field(VoiceChannelRole, graphql_name='persona')

    regions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TextRegion'))), graphql_name='regions')

    phrases = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('PhraseRegion'))), graphql_name='phrases')



class DataTopicTaggingConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DataTopicTagging))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class DataTopicsData(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class DataVersion(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class DeliveryEvent(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class DriverFieldConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class DriverFieldOption(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360EligibleReview(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360EligibleReviewConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360Feedback(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackAssignedRater(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackAssignedRaterConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackCompetencyScore(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackPerCompetencyScore(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackPerRaterRelationshipComments(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackPerRaterRelationshipScore(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackPerUnitGroupScore(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackQuartileScore(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackQuestionComment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackQuestionScore(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackQuestionScoreConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackQuestionScoreFrequency(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackRaterAssignmentError(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('participation_id', 'rater_id', 'error_type')
    participation_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='participationId')

    rater_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='raterId')

    error_type = sgqlc.types.Field(sgqlc.types.non_null(E360FeedbackRaterAssignmentErrorType), graphql_name='errorType')



class E360FeedbackRaterResponse(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('rater_assignments', 'rater_selection', 'errors')
    rater_assignments = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(E360FeedbackAssignedRater))), graphql_name='raterAssignments')

    rater_selection = sgqlc.types.Field(sgqlc.types.non_null('E360FeedbackWaveRaterSelection'), graphql_name='raterSelection')

    errors = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(E360FeedbackRaterAssignmentError)), graphql_name='errors')



class E360FeedbackRatingResponseRateStats(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackRatingStats(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackRatingStatsPerRaterRelationship(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackRequest(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackRequestConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackScore(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackScoreDetails(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackSubmitRaterResponse(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('success', 'rater_selection')
    success = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='success')

    rater_selection = sgqlc.types.Field(sgqlc.types.non_null('E360FeedbackWaveRaterSelection'), graphql_name='raterSelection')



class E360FeedbackWave(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackWaveConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackWaveEnrollment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackWaveParticipation(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackWaveParticipationConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackWaveRaterSelection(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360FeedbackWaveReport(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360Review(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360ReviewCompetency(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360ReviewConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360ReviewRaterCriteria(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360ReviewRaterRelationship(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360ReviewRaterRelationshipConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class E360WaveEnrollmentResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class EX360Program(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class EX360ProgramConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class EligibleEmployee(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class EligibleEmployeeConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmailSettings(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmailSettingsActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Employee(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmployeeAttributeDefinition(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmployeeAttributeDefinitionConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmployeeConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmployeeProgram(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmployeeProgramConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmployeeProgramCycle(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmployeeSelection(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmployeeSelectionConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmployeeSelectionSegment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class EnumFieldData(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'values', 'labels', 'options')
    field = sgqlc.types.Field(sgqlc.types.non_null('Field'), graphql_name='field')

    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='values')

    labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='labels')

    options = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('EnumOption')), graphql_name='options')



class EnumHistogramEntry(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class EnumOption(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'numeric_value')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    numeric_value = sgqlc.types.Field(Int, graphql_name='numericValue')



class Event(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('data', 'data_list', 'value', 'values', 'value_list', 'values_list', 'numeric_value', 'numeric_values', 'numeric_value_list', 'numeric_values_list', 'label', 'labels', 'label_list', 'labels_list', 'feedback', 'type', 'schema', 'program_record', 'primary_unit', 'timezone', 'invitation')
    data = sgqlc.types.Field(AttributeData, graphql_name='data', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(AttributeData)), graphql_name='dataList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''

    value = sgqlc.types.Field(String, graphql_name='value', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    values = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='values', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    value_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='valueList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='valuesList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    numeric_value = sgqlc.types.Field(Int, graphql_name='numericValue', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    numeric_values = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='numericValues', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    numeric_value_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Int)), graphql_name='numericValueList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    numeric_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(Int))), graphql_name='numericValuesList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    label = sgqlc.types.Field(String, graphql_name='label', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    labels = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='labels', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    label_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='labelList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    labels_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='labelsList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    feedback = sgqlc.types.Field('FeedbackRecord', graphql_name='feedback')

    type = sgqlc.types.Field(sgqlc.types.non_null('EventType'), graphql_name='type')

    schema = sgqlc.types.Field(sgqlc.types.non_null('EventSchema'), graphql_name='schema')

    program_record = sgqlc.types.Field('ProgramRecord', graphql_name='programRecord')

    primary_unit = sgqlc.types.Field('Unit', graphql_name='primaryUnit')

    timezone = sgqlc.types.Field(String, graphql_name='timezone')

    invitation = sgqlc.types.Field('InvitationRecord', graphql_name='invitation')



class EventConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Event))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='totalCount')



class EventSchema(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'attributes')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    attributes = sgqlc.types.Field(AttributeConnection, graphql_name='attributes', args=sgqlc.types.ArgDict((
        ('keys', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='keys', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('data_types', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(DataType)), graphql_name='dataTypes', default=None)),
        ('q', sgqlc.types.Arg(String, graphql_name='q', default=None)),
))
    )
    '''Arguments:

    * `keys` (`[ID!]`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `data_types` (`[DataType!]`)
    * `q` (`String`)
    '''



class EventSchemaConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(EventSchema))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class EventType(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'name')
    key = sgqlc.types.Field(sgqlc.types.non_null(EventTypeKey), graphql_name='key')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')



class Ex360Assessment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360Assessments(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360AssignedAssessment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360AssignedAssessmentConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360EnrollmentApproval(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360ParticipantAttribute(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360ParticipantAttributeConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360ParticipantAttributeDefinition(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360PossibleRater(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360PossibleUnsolicitedAssessmentParticipant(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360ProgramEnrollmentSettings(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360ProgramParticipant(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360ProgramParticipantConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360Rater(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360RaterAssignment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360RaterAssignmentApproval(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360RaterCountByRelationship(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360Relationship(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360RelationshipConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360RequiredRaterPerRelationship(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360Wave(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360WaveConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360WaveEnrolledParticipant(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360WaveEnrolledParticipantConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360WaveEnrollment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360WaveEnrollmentError(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360WaveEnrollmentResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Ex360WaveRaterSelection(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Export(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'format', 'annotation', 'latest_job', 'available_actions', 'jobs', 'rescheduling_properties', 'archived', 'favorite', 'report_id')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    format = sgqlc.types.Field(ExportFormat, graphql_name='format')

    annotation = sgqlc.types.Field(String, graphql_name='annotation')

    latest_job = sgqlc.types.Field(sgqlc.types.non_null('ExportJob'), graphql_name='latestJob')

    available_actions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExportAction))), graphql_name='availableActions')

    jobs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('ExportJob'))), graphql_name='jobs', args=sgqlc.types.ArgDict((
        ('archived', sgqlc.types.Arg(Boolean, graphql_name='archived', default=None)),
))
    )
    '''Arguments:

    * `archived` (`Boolean`)
    '''

    rescheduling_properties = sgqlc.types.Field('ExportSchedulingConfig', graphql_name='reschedulingProperties')

    archived = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='archived')

    favorite = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='favorite')

    report_id = sgqlc.types.Field(String, graphql_name='reportId')



class ExportConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Export)), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class ExportJob(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'creation_time', 'start_time', 'status', 'download_url', 'message', 'progress', 'archived', 'available_actions')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    creation_time = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='creationTime')

    start_time = sgqlc.types.Field(DateTime, graphql_name='startTime')

    status = sgqlc.types.Field(sgqlc.types.non_null(ExportJobStatus), graphql_name='status')

    download_url = sgqlc.types.Field(URI, graphql_name='downloadURL')

    message = sgqlc.types.Field(String, graphql_name='message')

    progress = sgqlc.types.Field(Float, graphql_name='progress')

    archived = sgqlc.types.Field(Boolean, graphql_name='archived')

    available_actions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ExportAction))), graphql_name='availableActions')



class ExportResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('export', 'error')
    export = sgqlc.types.Field(Export, graphql_name='export')

    error = sgqlc.types.Field(ExportError, graphql_name='error')



class ExportSchedulingConfig(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('frequency', 'scheduling_time', 'scheduling_timezone')
    frequency = sgqlc.types.Field('ExportSchedulingFrequency', graphql_name='frequency')

    scheduling_time = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='schedulingTime')

    scheduling_timezone = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='schedulingTimezone')



class ExternalBenchmark(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class FacebookTree(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class FeedFileConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('FeedFileRecord')), graphql_name='nodes')

    page_info = sgqlc.types.Field('PageInfo', graphql_name='pageInfo')

    total_count = sgqlc.types.Field(Long, graphql_name='totalCount')



class FeedFileRecord(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'field_data', 'field_data_list', 'field_value', 'field_value_list', 'field_values', 'field_values_list', 'field_numeric_value', 'field_numeric_value_list', 'field_numeric_values', 'field_numeric_values_list', 'field_labels', 'field_labels_list')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    field_data = sgqlc.types.Field('FieldData', graphql_name='fieldData', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('FieldData')), graphql_name='fieldDataList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''

    field_value = sgqlc.types.Field(String, graphql_name='fieldValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_value_list = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_values = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_value = sgqlc.types.Field(Int, graphql_name='fieldNumericValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_value_list = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_values = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(Int))), graphql_name='fieldNumericValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='fieldLabels', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_labels_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldLabelsList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''



class FeedbackConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'data_table', 'has_concealed_records', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('FeedbackRecord')), graphql_name='nodes')

    data_table = sgqlc.types.Field(sgqlc.types.non_null('RecordDataTable'), graphql_name='dataTable', args=sgqlc.types.ArgDict((
        ('definition', sgqlc.types.Arg(sgqlc.types.non_null(RecordDataTableDefinition), graphql_name='definition', default=None)),
))
    )
    '''Arguments:

    * `definition` (`RecordDataTableDefinition!`)
    '''

    has_concealed_records = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasConcealedRecords')

    page_info = sgqlc.types.Field('PageInfo', graphql_name='pageInfo')

    total_count = sgqlc.types.Field(Long, graphql_name='totalCount')



class FeedbackRecord(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'field_data', 'field_data_list', 'field_value', 'field_value_list', 'field_values', 'field_values_list', 'field_numeric_value', 'field_numeric_value_list', 'field_numeric_values', 'field_numeric_values_list', 'field_labels', 'field_labels_list', 'primary_unit', 'timezone', 'ask_now_test', 'ask_now_field_data_list', 'case', 'comments')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    field_data = sgqlc.types.Field('FieldData', graphql_name='fieldData', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('FieldData')), graphql_name='fieldDataList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''

    field_value = sgqlc.types.Field(String, graphql_name='fieldValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_value_list = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_values = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_value = sgqlc.types.Field(Int, graphql_name='fieldNumericValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_value_list = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_values = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(Int))), graphql_name='fieldNumericValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='fieldLabels', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_labels_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldLabelsList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    primary_unit = sgqlc.types.Field(sgqlc.types.non_null('Unit'), graphql_name='primaryUnit')

    timezone = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='timezone')

    ask_now_test = sgqlc.types.Field(AskNowTest, graphql_name='askNowTest')

    ask_now_field_data_list = sgqlc.types.Field(sgqlc.types.list_of('FieldData'), graphql_name='askNowFieldDataList')

    case = sgqlc.types.Field(Case, graphql_name='case')

    comments = sgqlc.types.Field(CommentConnection, graphql_name='comments', args=sgqlc.types.ArgDict((
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
))
    )
    '''Arguments:

    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    '''



class FeedbackRecordActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('put_mark_as_read', 'post_subscribe_to', 'put_apply_tag', 'put_update_exclusion_state', 'post_create_activity', 'post_create_activity_with_attachments', 'post_edit_attention_taggings')
    put_mark_as_read = sgqlc.types.Field(URI, graphql_name='putMarkAsRead')

    post_subscribe_to = sgqlc.types.Field(URI, graphql_name='postSubscribeTo')

    put_apply_tag = sgqlc.types.Field(URI, graphql_name='putApplyTag')

    put_update_exclusion_state = sgqlc.types.Field(URI, graphql_name='putUpdateExclusionState')

    post_create_activity = sgqlc.types.Field(URI, graphql_name='postCreateActivity')

    post_create_activity_with_attachments = sgqlc.types.Field(URI, graphql_name='postCreateActivityWithAttachments')

    post_edit_attention_taggings = sgqlc.types.Field(URI, graphql_name='postEditAttentionTaggings')



class FeedbackRecordAttachment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class FeedbackRecordAttachmentActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class FeedbackRecordAttachmentConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class FeedbackRecordLevelCriteria(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class FeedbackScoreScale(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Field(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'description', 'data_type', 'multivalued', 'value_type', 'filterable', 'used_on_programs', 'aggregatable', 'sub_record_fields')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    description = sgqlc.types.Field(String, graphql_name='description')

    data_type = sgqlc.types.Field(sgqlc.types.non_null(DataType), graphql_name='dataType')

    multivalued = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='multivalued')

    value_type = sgqlc.types.Field(sgqlc.types.non_null(ValueType), graphql_name='valueType')

    filterable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='filterable')

    used_on_programs = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Program'))), graphql_name='usedOnPrograms')

    aggregatable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='aggregatable')

    sub_record_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('Field')), graphql_name='subRecordFields')



class FieldConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Field))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class FieldCorrelation(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('field1', 'field2', 'sample_size_completeness', 'data_version')
    field1 = sgqlc.types.Field(sgqlc.types.non_null('XStatsAnalysisField'), graphql_name='field1')

    field2 = sgqlc.types.Field(sgqlc.types.non_null('XStatsAnalysisField'), graphql_name='field2')

    sample_size_completeness = sgqlc.types.Field(sgqlc.types.non_null('SampleSizeCompleteness'), graphql_name='sampleSizeCompleteness')

    data_version = sgqlc.types.Field(sgqlc.types.non_null(DataVersion), graphql_name='dataVersion')



class FieldData(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'values', 'labels')
    field = sgqlc.types.Field(sgqlc.types.non_null(Field), graphql_name='field')

    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='values')

    labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='labels')



class FieldDescription(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('field', 'sample_size_completeness', 'data_version')
    field = sgqlc.types.Field(sgqlc.types.non_null('XStatsAnalysisField'), graphql_name='field')

    sample_size_completeness = sgqlc.types.Field(sgqlc.types.non_null('SampleSizeCompleteness'), graphql_name='sampleSizeCompleteness')

    data_version = sgqlc.types.Field(sgqlc.types.non_null(DataVersion), graphql_name='dataVersion')



class File(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class FileAttachment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('file_name', 'download_link')
    file_name = sgqlc.types.Field(String, graphql_name='fileName')

    download_link = sgqlc.types.Field(String, graphql_name='downloadLink')



class FileVersion(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class FiniteFloat(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('finite_value',)
    finite_value = sgqlc.types.Field(sgqlc.types.non_null(Float), graphql_name='finiteValue')



class Form(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class FormRecord(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class FormattedTable(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('formatted_header_rows', 'formatted_rows', 'formatted_footer_rows')
    formatted_header_rows = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.list_of(String)), graphql_name='formattedHeaderRows')

    formatted_rows = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.list_of(String)), graphql_name='formattedRows')

    formatted_footer_rows = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.list_of(String)), graphql_name='formattedFooterRows')



class ForwardResponseEmailTemplate(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ForwardResponseInfo(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ForwardResponseResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ForwardResponseSettings(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ForwardResponseTemplateConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class From(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Goal(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class GoalConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class GoalEvent(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class GoalsWave(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class GoalsWaveConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class GoalsWaveParticipant(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class GoalsWaveParticipantConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class HeaderElement(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'label', 'field_id', 'group', 'rank_in_group', 'index', 'total_children')
    key = sgqlc.types.Field(sgqlc.types.non_null(SplitElementId), graphql_name='key')

    label = sgqlc.types.Field(sgqlc.types.non_null(SplitElementId), graphql_name='label')

    field_id = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='fieldId')

    group = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='group')

    rank_in_group = sgqlc.types.Field(Int, graphql_name='rankInGroup')

    index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='index')

    total_children = sgqlc.types.Field(Int, graphql_name='totalChildren')



class HourlyFrequency(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class IApplication(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('type', 'name', 'id', 'default_role', 'switchable_roles', 'uuid', 'link')
    type = sgqlc.types.Field(ApplicationTypeEnum, graphql_name='type')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')

    default_role = sgqlc.types.Field(sgqlc.types.non_null('Role'), graphql_name='defaultRole')

    switchable_roles = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Role'))), graphql_name='switchableRoles')

    uuid = sgqlc.types.Field(ID, graphql_name='uuid')

    link = sgqlc.types.Field(String, graphql_name='link')



class INavigationableApplication(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('type', 'name', 'id', 'default_role', 'switchable_roles', 'uuid', 'link', 'navigation')
    type = sgqlc.types.Field(ApplicationTypeEnum, graphql_name='type')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')

    default_role = sgqlc.types.Field(sgqlc.types.non_null('Role'), graphql_name='defaultRole')

    switchable_roles = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Role'))), graphql_name='switchableRoles')

    uuid = sgqlc.types.Field(ID, graphql_name='uuid')

    link = sgqlc.types.Field(String, graphql_name='link')

    navigation = sgqlc.types.Field(sgqlc.types.non_null('TabConnection'), graphql_name='navigation', args=sgqlc.types.ArgDict((
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
))
    )
    '''Arguments:

    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    '''



class IPage(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')



class InfiniteFloat(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('infinite_value',)
    infinite_value = sgqlc.types.Field(sgqlc.types.non_null(InfiniteFloatValue), graphql_name='infiniteValue')



class Insight(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class InvitationConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'has_concealed_records', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('InvitationRecord')), graphql_name='nodes')

    page_info = sgqlc.types.Field('PageInfo', graphql_name='pageInfo')

    has_concealed_records = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasConcealedRecords')

    total_count = sgqlc.types.Field(Long, graphql_name='totalCount')



class InvitationRecord(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'field_data', 'field_data_list', 'field_value', 'field_value_list', 'field_values', 'field_values_list', 'field_numeric_value', 'field_numeric_value_list', 'field_numeric_values', 'field_numeric_values_list', 'field_labels', 'field_labels_list', 'timezone', 'feedback')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    field_data = sgqlc.types.Field(FieldData, graphql_name='fieldData', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(FieldData)), graphql_name='fieldDataList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''

    field_value = sgqlc.types.Field(String, graphql_name='fieldValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_value_list = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_values = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_value = sgqlc.types.Field(Int, graphql_name='fieldNumericValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_value_list = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_values = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(Int))), graphql_name='fieldNumericValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='fieldLabels', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_labels_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldLabelsList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    timezone = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='timezone')

    feedback = sgqlc.types.Field(FeedbackRecord, graphql_name='feedback')



class InvitationRecordActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('put_mark_as_read', 'post_subscribe_to', 'put_apply_tag', 'put_update_exclusion_state')
    put_mark_as_read = sgqlc.types.Field(URI, graphql_name='putMarkAsRead')

    post_subscribe_to = sgqlc.types.Field(URI, graphql_name='postSubscribeTo')

    put_apply_tag = sgqlc.types.Field(URI, graphql_name='putApplyTag')

    put_update_exclusion_state = sgqlc.types.Field(URI, graphql_name='putUpdateExclusionState')



class KeywordSearchMatchesWithLanguage(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('language', 'matches')
    language = sgqlc.types.Field(sgqlc.types.non_null(TextAnalyticsLanguage), graphql_name='language')

    matches = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('KeywordTagging'))), graphql_name='matches')



class KeywordTagging(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('source', 'regions', 'token')
    source = sgqlc.types.Field(sgqlc.types.non_null(KeywordTaggingSource), graphql_name='source')

    regions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TextRegion'))), graphql_name='regions')

    token = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='token')



class LikeEvent(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class LikeEventConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class LinearRegression(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class LinearRegressionField(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('field',)
    field = sgqlc.types.Field(sgqlc.types.non_null('XStatsAnalysisField'), graphql_name='field')



class LinearRegressionResults(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class LogisticRegression(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class LogisticRegressionField(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('field',)
    field = sgqlc.types.Field(sgqlc.types.non_null('XStatsAnalysisField'), graphql_name='field')



class ManagerAssessment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MatchingTagging(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('topic_regions', 'sentiment_regions')
    topic_regions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('RuleTopicRegions'))), graphql_name='topicRegions')

    sentiment_regions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SentimentRegions'))), graphql_name='sentimentRegions')



class MatrixFieldAxis(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'label', 'fields')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')

    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')

    fields = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Field))), graphql_name='fields')



class MatrixFieldDataAxis(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('values',)
    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(FieldData))), graphql_name='values')



class Me(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('roles',)
    roles = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('Role'))), graphql_name='roles')



class MedalliaBenchmarksFilter(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MedalliaBenchmarksFilterOption(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MedalliaBenchmarksTable(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MedalliaBenchmarksTableColumnHeader(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MedalliaBenchmarksTableRowHeader(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MediaAnalytics(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MediaEvent(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('name', 'start', 'end')
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')

    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')



class MediaFileEvent(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MediaFileMetadata(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('media_processing_status', 'living_lens_report', 'show_download_link')
    media_processing_status = sgqlc.types.Field(sgqlc.types.non_null(MediaPublishStatus), graphql_name='mediaProcessingStatus')

    living_lens_report = sgqlc.types.Field(URI, graphql_name='livingLensReport')

    show_download_link = sgqlc.types.Field(Boolean, graphql_name='showDownloadLink')



class MediaTranscript(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Message(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'raw_text', 'participant_id', 'conversation_mode')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    raw_text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='rawText')

    participant_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='participantId')

    conversation_mode = sgqlc.types.Field(ConversationMode, graphql_name='conversationMode')



class MessageCenterRegistration(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MessageCenterRegistrationPolicy(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MessageCenterSettings(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MessageConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class MessageSourceStatus(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MessageTypeFilter(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MetricHeaderElement(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('key', 'index', 'label', 'valid')
    key = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='key')

    index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='index')

    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')

    valid = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='valid')



class MissingSocialUrl(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'text_identifier', 'name', 'address', 'status', 'source')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    text_identifier = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='textIdentifier')

    name = sgqlc.types.Field(String, graphql_name='name')

    address = sgqlc.types.Field(String, graphql_name='address')

    status = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='status')

    source = sgqlc.types.Field(sgqlc.types.non_null('SocialSource'), graphql_name='source')



class MissingUrlsConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MissingSocialUrl))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null('PageInfo'), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class MonthlyFrequency(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MultinomialRegression(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MultinomialRegressionDependentField(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class MultinomialRegressionIndependentField(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Mutation(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('update_customers',)
    update_customers = sgqlc.types.Field(String, graphql_name='updateCustomers', args=sgqlc.types.ArgDict((
        ('customers', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ContactUpdate))), graphql_name='customers', default=None)),
))
    )
    '''Arguments:

    * `customers` (`[ContactUpdate!]!`)
    '''



class NumericHistogram(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class NumericHistogramData(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class NumericSummary(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class OptionConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class OrgHierarchyListNode(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class OrgHierarchyListNodesConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class OrgHierarchyTreeChildConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class OrgHierarchyTreeChildNode(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class OrgHierarchyTreeNode(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class OrgHierarchyTreeRootNode(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class PIITagging(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class PageConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class PageInfo(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('end_cursor', 'has_next_page')
    end_cursor = sgqlc.types.Field(ID, graphql_name='endCursor')

    has_next_page = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='hasNextPage')



class Pair(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Participant(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Pearson(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class PercentageCriteria(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Percentile(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class PerformanceRating(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class PersonalizedAlert(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class PersonalizedAlertConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class PersonalizedAlertCriteriaTimeperiod(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class PersonalizedAlertsConfiguration(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class PhraseRegion(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Program(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'description', 'status', 'created_by', 'created_on', 'modified_by', 'modified_on', 'activation_date', 'responses_count', 'get_program_report_configuration', 'type')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    description = sgqlc.types.Field(String, graphql_name='description')

    status = sgqlc.types.Field(sgqlc.types.non_null(Status), graphql_name='status')

    created_by = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='createdBy')

    created_on = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='createdOn')

    modified_by = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='modifiedBy')

    modified_on = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='modifiedOn')

    activation_date = sgqlc.types.Field(DateTime, graphql_name='activationDate')

    responses_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='responsesCount')

    get_program_report_configuration = sgqlc.types.Field(sgqlc.types.non_null(URI), graphql_name='getProgramReportConfiguration')

    type = sgqlc.types.Field(sgqlc.types.non_null(Type), graphql_name='type')



class ProgramConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Program))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class ProgramRecord(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('data', 'data_list', 'main_score_data', 'value', 'values', 'value_list', 'values_list', 'main_score', 'numeric_value', 'numeric_values', 'numeric_value_list', 'numeric_values_list', 'label', 'labels', 'label_list', 'labels_list', 'feedback', 'schema')
    data = sgqlc.types.Field(AttributeData, graphql_name='data', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(AttributeData)), graphql_name='dataList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''

    main_score_data = sgqlc.types.Field(AttributeData, graphql_name='mainScoreData')

    value = sgqlc.types.Field(String, graphql_name='value', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    values = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='values', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    value_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='valueList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='valuesList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    main_score = sgqlc.types.Field(Float, graphql_name='mainScore')

    numeric_value = sgqlc.types.Field(Int, graphql_name='numericValue', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    numeric_values = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='numericValues', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    numeric_value_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Int)), graphql_name='numericValueList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    numeric_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(Int))), graphql_name='numericValuesList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    label = sgqlc.types.Field(String, graphql_name='label', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    labels = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='labels', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeSource, graphql_name='src', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeSource`)
    '''

    label_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='labelList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    labels_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='labelsList', args=sgqlc.types.ArgDict((
        ('src', sgqlc.types.Arg(AttributeListSource, graphql_name='src', default=None)),
        ('srcs', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AttributeSource)), graphql_name='srcs', default=None)),
))
    )
    '''Arguments:

    * `src` (`AttributeListSource`)
    * `srcs` (`[AttributeSource!]`)
    '''

    feedback = sgqlc.types.Field(FeedbackRecord, graphql_name='feedback')

    schema = sgqlc.types.Field(sgqlc.types.non_null('ProgramRecordSchema'), graphql_name='schema')



class ProgramRecordData(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ProgramRecordSchema(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'attributes', 'main_score_attribute')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    attributes = sgqlc.types.Field(AttributeConnection, graphql_name='attributes', args=sgqlc.types.ArgDict((
        ('keys', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='keys', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('data_types', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(DataType)), graphql_name='dataTypes', default=None)),
        ('q', sgqlc.types.Arg(String, graphql_name='q', default=None)),
))
    )
    '''Arguments:

    * `keys` (`[ID!]`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `data_types` (`[DataType!]`)
    * `q` (`String`)
    '''

    main_score_attribute = sgqlc.types.Field(Attribute, graphql_name='mainScoreAttribute')



class ProgramRecordSchemaConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ProgramRecordSchema))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class Quartiles(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Query(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('feedback', 'invitations', 'fields', 'customers', 'wordcloud', 'me', 'rate_limit', 'aggregate', 'aggregate_table', 'aggregate_table_list', 'aggregate_rank', 'aggregate_rank_list', 'event_schemas', 'program_record_schemas', 'customer_schema', 'programs', 'social_urlcoverage', 'missing_social_urls', 'social_active_sources', 'crosstab_saved_filters')
    feedback = sgqlc.types.Field(sgqlc.types.non_null(FeedbackConnection), graphql_name='feedback', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids', default=None)),
        ('filter', sgqlc.types.Arg(Filter, graphql_name='filter', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('order_by', sgqlc.types.Arg(sgqlc.types.list_of(RecordOrder), graphql_name='orderBy', default=None)),
        ('sampling', sgqlc.types.Arg(Sampling, graphql_name='sampling', default=None)),
        ('show_excluded', sgqlc.types.Arg(Boolean, graphql_name='showExcluded', default=False)),
        ('include_ad_hoc', sgqlc.types.Arg(Boolean, graphql_name='includeAdHoc', default=False)),
        ('include_isolated_records_of_type', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(IsolatedRecordType)), graphql_name='includeIsolatedRecordsOfType', default=None)),
))
    )
    '''Arguments:

    * `ids` (`[ID!]`)
    * `filter` (`Filter`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `order_by` (`[RecordOrder]`)
    * `sampling` (`Sampling`)
    * `show_excluded` (`Boolean`) (default: `false`)
    * `include_ad_hoc` (`Boolean`) (default: `false`)
    * `include_isolated_records_of_type` (`[IsolatedRecordType!]`)
    '''

    invitations = sgqlc.types.Field(sgqlc.types.non_null(InvitationConnection), graphql_name='invitations', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids', default=None)),
        ('filter', sgqlc.types.Arg(Filter, graphql_name='filter', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('order_by', sgqlc.types.Arg(sgqlc.types.list_of(RecordOrder), graphql_name='orderBy', default=None)),
        ('show_excluded', sgqlc.types.Arg(Boolean, graphql_name='showExcluded', default=False)),
        ('include_ad_hoc', sgqlc.types.Arg(Boolean, graphql_name='includeAdHoc', default=False)),
        ('include_isolated_records_of_type', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(IsolatedRecordType)), graphql_name='includeIsolatedRecordsOfType', default=None)),
))
    )
    '''Arguments:

    * `ids` (`[ID!]`)
    * `filter` (`Filter`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `order_by` (`[RecordOrder]`)
    * `show_excluded` (`Boolean`) (default: `false`)
    * `include_ad_hoc` (`Boolean`) (default: `false`)
    * `include_isolated_records_of_type` (`[IsolatedRecordType!]`)
    '''

    fields = sgqlc.types.Field(FieldConnection, graphql_name='fields', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids', default=None)),
        ('q', sgqlc.types.Arg(String, graphql_name='q', default=None)),
        ('data_types', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(DataType)), graphql_name='dataTypes', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('data_view', sgqlc.types.Arg(DataView, graphql_name='dataView', default=None)),
        ('filterable', sgqlc.types.Arg(Boolean, graphql_name='filterable', default=None)),
        ('aggregatable', sgqlc.types.Arg(Boolean, graphql_name='aggregatable', default=None)),
))
    )
    '''Arguments:

    * `ids` (`[ID!]`)
    * `q` (`String`)
    * `data_types` (`[DataType!]`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `data_view` (`DataView`)
    * `filterable` (`Boolean`)
    * `aggregatable` (`Boolean`)
    '''

    customers = sgqlc.types.Field(sgqlc.types.non_null(ContactsConnection), graphql_name='customers', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('query', sgqlc.types.Arg(String, graphql_name='query', default=None)),
        ('filter', sgqlc.types.Arg(ContactFilter, graphql_name='filter', default=None)),
        ('order_by', sgqlc.types.Arg(ContactOrder, graphql_name='orderBy', default=None)),
        ('data_view', sgqlc.types.Arg(DataView, graphql_name='dataView', default=None)),
))
    )
    '''Arguments:

    * `ids` (`[ID!]`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `query` (`String`)
    * `filter` (`ContactFilter`)
    * `order_by` (`ContactOrder`)
    * `data_view` (`DataView`)
    '''

    wordcloud = sgqlc.types.Field(sgqlc.types.list_of('WordcloudItem'), graphql_name='wordcloud', args=sgqlc.types.ArgDict((
        ('filter', sgqlc.types.Arg(Filter, graphql_name='filter', default=None)),
        ('data_view', sgqlc.types.Arg(DataView, graphql_name='dataView', default=None)),
        ('field', sgqlc.types.Arg(FieldId, graphql_name='field', default=None)),
        ('config', sgqlc.types.Arg(WordCloudConfiguration, graphql_name='config', default=None)),
))
    )
    '''Arguments:

    * `filter` (`Filter`)
    * `data_view` (`DataView`)
    * `field` (`FieldId`)
    * `config` (`WordCloudConfiguration`)
    '''

    me = sgqlc.types.Field(Me, graphql_name='me')

    rate_limit = sgqlc.types.Field('RateLimit', graphql_name='rateLimit')

    aggregate = sgqlc.types.Field(Float, graphql_name='aggregate', args=sgqlc.types.ArgDict((
        ('definition', sgqlc.types.Arg(sgqlc.types.non_null(AggregateDefinition), graphql_name='definition', default=None)),
        ('batch_key', sgqlc.types.Arg(String, graphql_name='batchKey', default=None)),
))
    )
    '''Arguments:

    * `definition` (`AggregateDefinition!`)
    * `batch_key` (`String`)
    '''

    aggregate_table = sgqlc.types.Field(AggregationTable, graphql_name='aggregateTable', args=sgqlc.types.ArgDict((
        ('definition', sgqlc.types.Arg(sgqlc.types.non_null(AggregateTableDefinition), graphql_name='definition', default=None)),
        ('batch_key', sgqlc.types.Arg(String, graphql_name='batchKey', default=None)),
        ('optimization', sgqlc.types.Arg(Boolean, graphql_name='optimization', default=None)),
))
    )
    '''Arguments:

    * `definition` (`AggregateTableDefinition!`)
    * `batch_key` (`String`)
    * `optimization` (`Boolean`)
    '''

    aggregate_table_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(AggregationTable)), graphql_name='aggregateTableList', args=sgqlc.types.ArgDict((
        ('definitions', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(AggregateTableDefinition))), graphql_name='definitions', default=None)),
        ('batch_keys', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='batchKeys', default=None)),
        ('optimization', sgqlc.types.Arg(Boolean, graphql_name='optimization', default=None)),
        ('pagination', sgqlc.types.Arg(AggregateTablePagination, graphql_name='pagination', default=None)),
        ('pagination_v2', sgqlc.types.Arg(AggregateTableListPagination, graphql_name='paginationV2', default=None)),
))
    )
    '''Arguments:

    * `definitions` (`[AggregateTableDefinition!]!`)
    * `batch_keys` (`[String!]`)
    * `optimization` (`Boolean`)
    * `pagination` (`AggregateTablePagination`)
    * `pagination_v2` (`AggregateTableListPagination`)
    '''

    aggregate_rank = sgqlc.types.Field(AggregationRank, graphql_name='aggregateRank', args=sgqlc.types.ArgDict((
        ('definition', sgqlc.types.Arg(sgqlc.types.non_null(AggregateRankDefinition), graphql_name='definition', default=None)),
))
    )
    '''Arguments:

    * `definition` (`AggregateRankDefinition!`)
    '''

    aggregate_rank_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(AggregationRank)), graphql_name='aggregateRankList', args=sgqlc.types.ArgDict((
        ('definition', sgqlc.types.Arg(AggregateRankListDefinition, graphql_name='definition', default=None)),
        ('definitions', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(AggregateRankDefinition)), graphql_name='definitions', default=None)),
))
    )
    '''Arguments:

    * `definition` (`AggregateRankListDefinition`)
    * `definitions` (`[AggregateRankDefinition!]`)
    '''

    event_schemas = sgqlc.types.Field(sgqlc.types.non_null(EventSchemaConnection), graphql_name='eventSchemas', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
))
    )
    '''Arguments:

    * `ids` (`[ID!]`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    '''

    program_record_schemas = sgqlc.types.Field(sgqlc.types.non_null(ProgramRecordSchemaConnection), graphql_name='programRecordSchemas', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
))
    )
    '''Arguments:

    * `ids` (`[ID!]`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    '''

    customer_schema = sgqlc.types.Field(ContactSchema, graphql_name='customerSchema')

    programs = sgqlc.types.Field(sgqlc.types.non_null(ProgramConnection), graphql_name='programs', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids', default=None)),
        ('query', sgqlc.types.Arg(String, graphql_name='query', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
        ('types', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='types', default=None)),
))
    )
    '''Arguments:

    * `ids` (`[ID!]`)
    * `query` (`String`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    * `types` (`[ID!]`)
    '''

    social_urlcoverage = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('SocialURLCoverage'))), graphql_name='socialURLCoverage')

    missing_social_urls = sgqlc.types.Field(MissingUrlsConnection, graphql_name='missingSocialURLs', args=sgqlc.types.ArgDict((
        ('after', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='after', default=0)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=25)),
        ('sorting', sgqlc.types.Arg(Sorting, graphql_name='sorting', default=None)),
        ('source_id', sgqlc.types.Arg(ID, graphql_name='sourceId', default=None)),
        ('unit_id', sgqlc.types.Arg(ID, graphql_name='unitId', default=None)),
))
    )
    '''Arguments:

    * `after` (`Int!`) (default: `0`)
    * `first` (`Int!`) (default: `25`)
    * `sorting` (`Sorting`)
    * `source_id` (`ID`)
    * `unit_id` (`ID`)
    '''

    social_active_sources = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of('SocialSource')), graphql_name='socialActiveSources')

    crosstab_saved_filters = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CrosstabSavedFilter))), graphql_name='crosstabSavedFilters', args=sgqlc.types.ArgDict((
        ('module_uuid', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='moduleUuid', default=None)),
))
    )
    '''Arguments:

    * `module_uuid` (`ID!`)
    '''



class QueryInfo(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('query', 'variables')
    query = sgqlc.types.Field(String, graphql_name='query')

    variables = sgqlc.types.Field(String, graphql_name='variables')



class QuestionGroupOption(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class QuestionGroupOptionConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class RapidResponse(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class RapidResponseActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class RapidResponseConversationMessage(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class RapidResponseConversationTemplate(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class RapidResponseConversationTemplateConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class RapidResponseEmailTemplate(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class RapidResponseEmailTemplateActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class RapidResponseMessage(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class RateLimit(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('cost',)
    cost = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='cost')



class RaterCriteriaPerRaterRelationship(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ReceptionEvent(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class RecordDataTable(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('values',)
    values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(sgqlc.types.list_of(String)))), graphql_name='values')



class RecordTag(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'label', 'is_editable', 'actions')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')

    is_editable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='isEditable')

    actions = sgqlc.types.Field('RecordTagActions', graphql_name='actions')



class RecordTagActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('patch_update_tag',)
    patch_update_tag = sgqlc.types.Field(URI, graphql_name='patchUpdateTag')



class RegressionResult(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('dependent_field', 'independent_fields', 'sample_size_completeness', 'data_version')
    dependent_field = sgqlc.types.Field(sgqlc.types.non_null('XStatsAnalysisField'), graphql_name='dependentField')

    independent_fields = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('XStatsAnalysisField')), graphql_name='independentFields')

    sample_size_completeness = sgqlc.types.Field(sgqlc.types.non_null('SampleSizeCompleteness'), graphql_name='sampleSizeCompleteness')

    data_version = sgqlc.types.Field(sgqlc.types.non_null(DataVersion), graphql_name='dataVersion')



class ReschedulingProperties(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Reviews(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Role(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'view_name')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    view_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='viewName')



class RuleTopic(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'has_descendants', 'ancestors')
    id = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    has_descendants = sgqlc.types.Field(Boolean, graphql_name='hasDescendants')

    ancestors = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='ancestors')



class RuleTopicConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class RuleTopicRegions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('topics', 'start_index', 'end_index')
    topics = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RuleTopic))), graphql_name='topics')

    start_index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='startIndex')

    end_index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='endIndex')



class RuleTopicTagging(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('topic', 'persona', 'regions', 'phrases')
    topic = sgqlc.types.Field(RuleTopic, graphql_name='topic')

    persona = sgqlc.types.Field(VoiceChannelRole, graphql_name='persona')

    regions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TextRegion'))), graphql_name='regions')

    phrases = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(PhraseRegion))), graphql_name='phrases')



class RuleTopicTaggingConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RuleTopicTagging))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class SSOEventStatConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SSOEventStatRecord')), graphql_name='nodes')

    page_info = sgqlc.types.Field(PageInfo, graphql_name='pageInfo')

    total_count = sgqlc.types.Field(Long, graphql_name='totalCount')



class SSOEventStatRecord(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'field_data', 'field_data_list', 'field_value', 'field_value_list', 'field_values', 'field_values_list', 'field_numeric_value', 'field_numeric_value_list', 'field_numeric_values', 'field_numeric_values_list', 'field_labels', 'field_labels_list')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    field_data = sgqlc.types.Field(FieldData, graphql_name='fieldData', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(FieldData)), graphql_name='fieldDataList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''

    field_value = sgqlc.types.Field(String, graphql_name='fieldValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_value_list = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_values = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_value = sgqlc.types.Field(Int, graphql_name='fieldNumericValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_value_list = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_values = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(Int))), graphql_name='fieldNumericValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='fieldLabels', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_labels_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldLabelsList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''



class SampleSizeCompleteness(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ScaleColorScheme(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('start', 'end', 'background', 'border')
    start = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='start')

    end = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='end')

    background = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='background')

    border = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='border')



class SelfAssessment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class SentimentRegions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('sentiment', 'start_index', 'end_index')
    sentiment = sgqlc.types.Field(Sentiment, graphql_name='sentiment')

    start_index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='startIndex')

    end_index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='endIndex')



class SentimentTagging(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('sentiment', 'persona', 'regions')
    sentiment = sgqlc.types.Field(Sentiment, graphql_name='sentiment')

    persona = sgqlc.types.Field(VoiceChannelRole, graphql_name='persona')

    regions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('TextRegion'))), graphql_name='regions')



class SentimentTaggingConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(SentimentTagging))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class SignificanceTestResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('p_value', 'difference_classification')
    p_value = sgqlc.types.Field(Float, graphql_name='pValue')

    difference_classification = sgqlc.types.Field(SignificanceTestDifferenceClassification, graphql_name='differenceClassification')



class SocialAggregationTable(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class SocialFeedbackSourceData(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class SocialHeaderElement(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class SocialMetricHeaderElement(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class SocialReplySettings(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('warning_message',)
    warning_message = sgqlc.types.Field(String, graphql_name='warningMessage')



class SocialSentiment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'label', 'value', 'actions')
    id = sgqlc.types.Field(sgqlc.types.non_null(SocialSentimentId), graphql_name='id')

    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='label')

    value = sgqlc.types.Field(Int, graphql_name='value')

    actions = sgqlc.types.Field(sgqlc.types.non_null('SocialSentimentActions'), graphql_name='actions')



class SocialSentimentActions(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('put_update_social_sentiment',)
    put_update_social_sentiment = sgqlc.types.Field(URI, graphql_name='putUpdateSocialSentiment')



class SocialSource(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'name', 'display_name')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    display_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='displayName')



class SocialSourceScoreData(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class SocialURLCoverage(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('source', 'expected_urls_count', 'existing_urls_count')
    source = sgqlc.types.Field(sgqlc.types.non_null(SocialSource), graphql_name='source')

    expected_urls_count = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='expectedUrlsCount')

    existing_urls_count = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='existingUrlsCount')



class SurveyAttachment(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class SurveyAttachmentsConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class SurveyExportStatConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('SurveyExportStatRecord')), graphql_name='nodes')

    page_info = sgqlc.types.Field(PageInfo, graphql_name='pageInfo')

    total_count = sgqlc.types.Field(Long, graphql_name='totalCount')



class SurveyExportStatRecord(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'field_data', 'field_data_list', 'field_value', 'field_value_list', 'field_values', 'field_values_list', 'field_numeric_value', 'field_numeric_value_list', 'field_numeric_values', 'field_numeric_values_list', 'field_labels', 'field_labels_list')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    field_data = sgqlc.types.Field(FieldData, graphql_name='fieldData', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(FieldData)), graphql_name='fieldDataList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''

    field_value = sgqlc.types.Field(String, graphql_name='fieldValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_value_list = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_values = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_value = sgqlc.types.Field(Int, graphql_name='fieldNumericValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_value_list = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_values = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(Int))), graphql_name='fieldNumericValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='fieldLabels', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_labels_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldLabelsList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''



class Tab(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class TabConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class Tests(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('chi_squared', 't_test', 'z_test')
    chi_squared = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='chiSquared')

    t_test = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='tTest')

    z_test = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='zTest')



class TextRegion(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('start_index', 'end_index')
    start_index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='startIndex')

    end_index = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='endIndex')



class TextWithLanguage(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('text', 'language')
    text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='text')

    language = sgqlc.types.Field(sgqlc.types.non_null(TextAnalyticsLanguage), graphql_name='language')



class ThresholdCriteria(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class TimeOfTheDay(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class TransitionResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class Unit(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'identifier', 'name', 'tz', 'timezone', 'unit_groups', 'field_data', 'field_data_list', 'street_address', 'city', 'postal_code')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    identifier = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='identifier')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    tz = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='tz')

    timezone = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='timezone')

    unit_groups = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UnitGroup'))), graphql_name='unitGroups')

    field_data = sgqlc.types.Field(FieldData, graphql_name='fieldData', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(FieldData)), graphql_name='fieldDataList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    street_address = sgqlc.types.Field(String, graphql_name='streetAddress')

    city = sgqlc.types.Field(String, graphql_name='city')

    postal_code = sgqlc.types.Field(String, graphql_name='postalCode')



class UnitConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class UnitGroup(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('identifier', 'name', 'parent', 'children', 'field_data', 'field_data_list')
    identifier = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='identifier')

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='name')

    parent = sgqlc.types.Field('UnitGroup', graphql_name='parent')

    children = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null('UnitGroup'))), graphql_name='children')

    field_data = sgqlc.types.Field(FieldData, graphql_name='fieldData', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(FieldData)), graphql_name='fieldDataList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''



class User(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'username', 'firstname', 'lastname', 'fullname', 'email', 'primary_role', 'primary_access', 'last_login', 'employee_unit')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    username = sgqlc.types.Field(String, graphql_name='username')

    firstname = sgqlc.types.Field(String, graphql_name='firstname')

    lastname = sgqlc.types.Field(String, graphql_name='lastname')

    fullname = sgqlc.types.Field(String, graphql_name='fullname')

    email = sgqlc.types.Field(String, graphql_name='email')

    primary_role = sgqlc.types.Field(Role, graphql_name='primaryRole')

    primary_access = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='primaryAccess')

    last_login = sgqlc.types.Field(DateTime, graphql_name='lastLogin')

    employee_unit = sgqlc.types.Field(Unit, graphql_name='employeeUnit')



class UserActivityConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null('UserActivityRecord')), graphql_name='nodes')

    page_info = sgqlc.types.Field(PageInfo, graphql_name='pageInfo')

    total_count = sgqlc.types.Field(Long, graphql_name='totalCount')



class UserActivityRecord(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'field_data', 'field_data_list', 'field_value', 'field_value_list', 'field_values', 'field_values_list', 'field_numeric_value', 'field_numeric_value_list', 'field_numeric_values', 'field_numeric_values_list', 'field_labels', 'field_labels_list')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    field_data = sgqlc.types.Field(FieldData, graphql_name='fieldData', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_data_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(FieldData)), graphql_name='fieldDataList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''

    field_value = sgqlc.types.Field(String, graphql_name='fieldValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_value_list = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_values = sgqlc.types.Field(sgqlc.types.list_of(String), graphql_name='fieldValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_value = sgqlc.types.Field(Int, graphql_name='fieldNumericValue', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_value_list = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValueList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_numeric_values = sgqlc.types.Field(sgqlc.types.list_of(Int), graphql_name='fieldNumericValues', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_numeric_values_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(Int))), graphql_name='fieldNumericValuesList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''

    field_labels = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(String)), graphql_name='fieldLabels', args=sgqlc.types.ArgDict((
        ('field_id', sgqlc.types.Arg(sgqlc.types.non_null(ID), graphql_name='fieldId', default=None)),
))
    )
    '''Arguments:

    * `field_id` (`ID!`)
    '''

    field_labels_list = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.list_of(String))), graphql_name='fieldLabelsList', args=sgqlc.types.ArgDict((
        ('field_ids', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name='fieldIds', default=None)),
))
    )
    '''Arguments:

    * `field_ids` (`[ID!]!`)
    '''



class UserConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ('nodes', 'page_info', 'total_count')
    nodes = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(User))), graphql_name='nodes')

    page_info = sgqlc.types.Field(sgqlc.types.non_null(PageInfo), graphql_name='pageInfo')

    total_count = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='totalCount')



class UserMessage(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class UserMessageConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class UserMessagePayloadAttribute(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ValueCalculations(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('count', 'percentage_of_row', 'percentage_of_column')
    count = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='count')

    percentage_of_row = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='percentageOfRow')

    percentage_of_column = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='percentageOfColumn')



class VoiceChannelAnalytics(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class VttLine(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class WatchlistHierarchyChildConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class WatchlistHierarchyChildNode(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class WatchlistHierarchyRootNode(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class WatchlistListNode(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class WatchlistListNodesConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class WatchlistNode(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class WatchlistSubscription(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class WatchlistSubscriptionConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class WaveStage(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class WeeklyFrequency(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class WordcloudItem(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('word', 'search_expression', 'frequency', 'sentiment')
    word = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='word')

    search_expression = sgqlc.types.Field(String, graphql_name='searchExpression')

    frequency = sgqlc.types.Field(WordcloudSize, graphql_name='frequency')

    sentiment = sgqlc.types.Field(WordcloudSentiment, graphql_name='sentiment')



class XStatsAnalysis(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('id', 'workbench_id', 'status', 'error', 'finish_time')
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='id')

    workbench_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name='workbenchId')

    status = sgqlc.types.Field(sgqlc.types.non_null(XStatsAnalysisStatus), graphql_name='status')

    error = sgqlc.types.Field('XStatsError', graphql_name='error')

    finish_time = sgqlc.types.Field('ZoneDateTime', graphql_name='finishTime')



class XStatsAnalysisConnection(sgqlc.types.relay.Connection):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsAnalysisField(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsDatasetInfo(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsDatasetTimePeriodProperties(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsError(sgqlc.types.Interface):
    __schema__ = medallia_schema
    __field_names__ = ('code',)
    code = sgqlc.types.Field(sgqlc.types.non_null(XStatsErrorCode), graphql_name='code')



class XStatsFieldError(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsWorkbench(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsWorkbenchPreview(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsWorkbenchResult(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ()


class ZoneDateTime(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('date_time', 'zone', 'utc_instant')
    date_time = sgqlc.types.Field(sgqlc.types.non_null(DateTime), graphql_name='dateTime')

    zone = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='zone')

    utc_instant = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name='utcInstant')



class ZoneDateTimeInterval(sgqlc.types.Type):
    __schema__ = medallia_schema
    __field_names__ = ('from_', 'to')
    from_ = sgqlc.types.Field(ZoneDateTime, graphql_name='from')

    to = sgqlc.types.Field(ZoneDateTime, graphql_name='to')



class ActionPlanInputValidationError(sgqlc.types.Type, ActionPlanUpsertError):
    __schema__ = medallia_schema
    __field_names__ = ()


class ActionPlanVersioningError(sgqlc.types.Type, ActionPlanUpsertError):
    __schema__ = medallia_schema
    __field_names__ = ()


class AnovaFieldCorrelation(sgqlc.types.Type, FieldCorrelation):
    __schema__ = medallia_schema
    __field_names__ = ()


class Application(sgqlc.types.Type, IApplication):
    __schema__ = medallia_schema
    __field_names__ = ()


class AttachmentFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ()


class AudioFileMetadata(sgqlc.types.Type, MediaFileMetadata):
    __schema__ = medallia_schema
    __field_names__ = ()


class BaseContactAttribute(sgqlc.types.Type, ContactAttribute):
    __schema__ = medallia_schema
    __field_names__ = ('filterable',)
    filterable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='filterable')



class BaseEmployeeAttributeDefinition(sgqlc.types.Type, EmployeeAttributeDefinition):
    __schema__ = medallia_schema
    __field_names__ = ()


class BooleanContactData(sgqlc.types.Type, ContactData):
    __schema__ = medallia_schema
    __field_names__ = ()


class CategoricalLinearRegressionField(sgqlc.types.Type, LinearRegressionField):
    __schema__ = medallia_schema
    __field_names__ = ()


class CategoricalLogisticRegressionField(sgqlc.types.Type, LogisticRegressionField):
    __schema__ = medallia_schema
    __field_names__ = ()


class ChiSquaredFieldCorrelation(sgqlc.types.Type, FieldCorrelation):
    __schema__ = medallia_schema
    __field_names__ = ()


class CommentField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ()


class CommentFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ('texts_with_language', 'original_language', 'processing_language', 'translatable_languages', 'tagging_status', 'keyword_search_matches_with_languages', 'rule_topic_taggings', 'data_topic_taggings', 'sentiment_taggings', 'keyword_taggings', 'actionable_taggings', 'actions', 'matching_taggings', 'rule_topic_taggings_page', 'data_topic_taggings_page', 'sentiment_taggings_page', 'employee_recognition_regions', 'customer_effort_taggings', 'media_file_metadata')
    texts_with_language = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(TextWithLanguage))), graphql_name='textsWithLanguage')

    original_language = sgqlc.types.Field(TextAnalyticsLanguage, graphql_name='originalLanguage')

    processing_language = sgqlc.types.Field(TextAnalyticsLanguage, graphql_name='processingLanguage')

    translatable_languages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(TextAnalyticsLanguage))), graphql_name='translatableLanguages')

    tagging_status = sgqlc.types.Field(CommentTaggingsStatus, graphql_name='taggingStatus')

    keyword_search_matches_with_languages = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeywordSearchMatchesWithLanguage))), graphql_name='keywordSearchMatchesWithLanguages', args=sgqlc.types.ArgDict((
        ('search', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name='search', default=None)),
))
    )
    '''Arguments:

    * `search` (`[String!]!`)
    '''

    rule_topic_taggings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(RuleTopicTagging))), graphql_name='ruleTopicTaggings')

    data_topic_taggings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(DataTopicTagging))), graphql_name='dataTopicTaggings')

    sentiment_taggings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(SentimentTagging))), graphql_name='sentimentTaggings')

    keyword_taggings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(KeywordTagging))), graphql_name='keywordTaggings')

    actionable_taggings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ActionableTagging))), graphql_name='actionableTaggings', args=sgqlc.types.ArgDict((
        ('ids', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name='ids', default=None)),
))
    )
    '''Arguments:

    * `ids` (`[ID!]`)
    '''

    actions = sgqlc.types.Field(sgqlc.types.non_null(CommentFieldDataActions), graphql_name='actions')

    matching_taggings = sgqlc.types.Field(sgqlc.types.non_null(MatchingTagging), graphql_name='matchingTaggings', args=sgqlc.types.ArgDict((
        ('filters', sgqlc.types.Arg(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(TaggingFilter))), graphql_name='filters', default=None)),
))
    )
    '''Arguments:

    * `filters` (`[TaggingFilter!]!`)
    '''

    rule_topic_taggings_page = sgqlc.types.Field(sgqlc.types.non_null(RuleTopicTaggingConnection), graphql_name='ruleTopicTaggingsPage', args=sgqlc.types.ArgDict((
        ('filters', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(TopicTaggingFilter)), graphql_name='filters', default=None)),
        ('first', sgqlc.types.Arg(Int, graphql_name='first', default=None)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
))
    )
    '''Arguments:

    * `filters` (`[TopicTaggingFilter!]`)
    * `first` (`Int`)
    * `after` (`ID`)
    '''

    data_topic_taggings_page = sgqlc.types.Field(sgqlc.types.non_null(DataTopicTaggingConnection), graphql_name='dataTopicTaggingsPage', args=sgqlc.types.ArgDict((
        ('filters', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(TopicTaggingFilter)), graphql_name='filters', default=None)),
        ('first', sgqlc.types.Arg(Int, graphql_name='first', default=None)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
))
    )
    '''Arguments:

    * `filters` (`[TopicTaggingFilter!]`)
    * `first` (`Int`)
    * `after` (`ID`)
    '''

    sentiment_taggings_page = sgqlc.types.Field(sgqlc.types.non_null(SentimentTaggingConnection), graphql_name='sentimentTaggingsPage', args=sgqlc.types.ArgDict((
        ('filters', sgqlc.types.Arg(sgqlc.types.list_of(sgqlc.types.non_null(TaggingFilter)), graphql_name='filters', default=None)),
        ('first', sgqlc.types.Arg(Int, graphql_name='first', default=None)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
))
    )
    '''Arguments:

    * `filters` (`[TaggingFilter!]`)
    * `first` (`Int`)
    * `after` (`ID`)
    '''

    employee_recognition_regions = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(TextRegion))), graphql_name='employeeRecognitionRegions')

    customer_effort_taggings = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CustomerEffortTagging))), graphql_name='customerEffortTaggings')

    media_file_metadata = sgqlc.types.Field(MediaFileMetadata, graphql_name='mediaFileMetadata')



class ContactSegmentRuleTestResult(sgqlc.types.Type, FormattedTable):
    __schema__ = medallia_schema
    __field_names__ = ()


class CorrelationAnalysis(sgqlc.types.Type, XStatsAnalysis):
    __schema__ = medallia_schema
    __field_names__ = ()


class CustomContactSegment(sgqlc.types.Type, ContactSegment):
    __schema__ = medallia_schema
    __field_names__ = ()


class DateAttributeData(sgqlc.types.Type, AttributeData):
    __schema__ = medallia_schema
    __field_names__ = ()


class DateContactData(sgqlc.types.Type, ContactData):
    __schema__ = medallia_schema
    __field_names__ = ()


class DateField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ()


class DateFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ()


class DateTimeField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ()


class DateTimeFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ('zoned_dates',)
    zoned_dates = sgqlc.types.Field(sgqlc.types.list_of(ZoneDateTime), graphql_name='zonedDates')



class DescribeAnalysis(sgqlc.types.Type, XStatsAnalysis):
    __schema__ = medallia_schema
    __field_names__ = ()


class DoubleContactData(sgqlc.types.Type, ContactData):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmailActivity(sgqlc.types.Type, Activity):
    __schema__ = medallia_schema
    __field_names__ = ('subject', 'body', 'cc', 'email_attachments')
    subject = sgqlc.types.Field(String, graphql_name='subject')

    body = sgqlc.types.Field(String, graphql_name='body')

    cc = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name='cc')

    email_attachments = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(FileAttachment)), graphql_name='emailAttachments')



class EmailField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ()


class EmployeeProgramApplication(sgqlc.types.Type, INavigationableApplication, IApplication):
    __schema__ = medallia_schema
    __field_names__ = ()


class EnumAttributeData(sgqlc.types.Type, AttributeData):
    __schema__ = medallia_schema
    __field_names__ = ('numeric_values', 'options')
    numeric_values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Int)), graphql_name='numericValues')

    options = sgqlc.types.Field(sgqlc.types.list_of(EnumOption), graphql_name='options')



class EnumContactAttribute(sgqlc.types.Type, ContactAttribute):
    __schema__ = medallia_schema
    __field_names__ = ('filterable', 'search_options')
    filterable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='filterable')

    search_options = sgqlc.types.Field(sgqlc.types.non_null(OptionConnection), graphql_name='searchOptions', args=sgqlc.types.ArgDict((
        ('q', sgqlc.types.Arg(String, graphql_name='q', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
))
    )
    '''Arguments:

    * `q` (`String`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    '''



class EnumContactData(sgqlc.types.Type, ContactData):
    __schema__ = medallia_schema
    __field_names__ = ('options',)
    options = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(EnumOption)), graphql_name='options')



class EnumEmployeeAttributeDefinition(sgqlc.types.Type, EmployeeAttributeDefinition):
    __schema__ = medallia_schema
    __field_names__ = ()


class EnumField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ('options',)
    options = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(EnumOption)), graphql_name='options')



class EnumFieldDescription(sgqlc.types.Type, FieldDescription):
    __schema__ = medallia_schema
    __field_names__ = ()


class ExperienceProgramPage(sgqlc.types.Type, IPage):
    __schema__ = medallia_schema
    __field_names__ = ()


class ExportAsyncTask(sgqlc.types.Type, AsyncTask):
    __schema__ = medallia_schema
    __field_names__ = ()


class FeedbackActivity(sgqlc.types.Type, Activity):
    __schema__ = medallia_schema
    __field_names__ = ()


class FloatAttributeData(sgqlc.types.Type, AttributeData):
    __schema__ = medallia_schema
    __field_names__ = ('numeric_values',)
    numeric_values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Float)), graphql_name='numericValues')



class FloatField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ('min', 'max')
    min = sgqlc.types.Field(Int, graphql_name='min')

    max = sgqlc.types.Field(Int, graphql_name='max')



class ForwardResponseAsyncTask(sgqlc.types.Type, AsyncTask):
    __schema__ = medallia_schema
    __field_names__ = ()


class ImageFileMetadata(sgqlc.types.Type, MediaFileMetadata):
    __schema__ = medallia_schema
    __field_names__ = ()


class InboundMessage(sgqlc.types.Type, Message):
    __schema__ = medallia_schema
    __field_names__ = ()


class IntAttributeData(sgqlc.types.Type, AttributeData):
    __schema__ = medallia_schema
    __field_names__ = ('numeric_values',)
    numeric_values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Int)), graphql_name='numericValues')



class IntContactData(sgqlc.types.Type, ContactData):
    __schema__ = medallia_schema
    __field_names__ = ('int_values',)
    int_values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Long)), graphql_name='intValues')



class IntField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ('min', 'max')
    min = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='min')

    max = sgqlc.types.Field(sgqlc.types.non_null(Long), graphql_name='max')



class IntFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ('int_values',)
    int_values = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Long)), graphql_name='intValues')



class LinearRegressionResult(sgqlc.types.Type, RegressionResult):
    __schema__ = medallia_schema
    __field_names__ = ()


class LocalDateTimeContactData(sgqlc.types.Type, ContactData):
    __schema__ = medallia_schema
    __field_names__ = ()


class LogisticRegressionResult(sgqlc.types.Type, RegressionResult):
    __schema__ = medallia_schema
    __field_names__ = ()


class LuhnEvent(sgqlc.types.Type, MediaEvent):
    __schema__ = medallia_schema
    __field_names__ = ()


class MatrixField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ('columns', 'rows')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MatrixFieldAxis))), graphql_name='columns')

    rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MatrixFieldAxis))), graphql_name='rows')



class MatrixFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ('columns', 'rows')
    columns = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MatrixFieldDataAxis))), graphql_name='columns', args=sgqlc.types.ArgDict((
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''

    rows = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(MatrixFieldDataAxis))), graphql_name='rows', args=sgqlc.types.ArgDict((
        ('filter_unanswered', sgqlc.types.Arg(Boolean, graphql_name='filterUnanswered', default=False)),
))
    )
    '''Arguments:

    * `filter_unanswered` (`Boolean`) (default: `false`)
    '''



class MedalliaBenchmarksExportUploadTask(sgqlc.types.Type, AsyncTask):
    __schema__ = medallia_schema
    __field_names__ = ()


class MultinomialRegressionResult(sgqlc.types.Type, RegressionResult):
    __schema__ = medallia_schema
    __field_names__ = ()


class NavigationableApplication(sgqlc.types.Type, INavigationableApplication, IApplication):
    __schema__ = medallia_schema
    __field_names__ = ()


class NewResponsesAsyncTask(sgqlc.types.Type, AsyncTask):
    __schema__ = medallia_schema
    __field_names__ = ()


class NumericFieldDescription(sgqlc.types.Type, FieldDescription):
    __schema__ = medallia_schema
    __field_names__ = ()


class NumericLinearRegressionField(sgqlc.types.Type, LinearRegressionField):
    __schema__ = medallia_schema
    __field_names__ = ()


class NumericLogisticRegressionField(sgqlc.types.Type, LogisticRegressionField):
    __schema__ = medallia_schema
    __field_names__ = ()


class OutboundMessage(sgqlc.types.Type, Message):
    __schema__ = medallia_schema
    __field_names__ = ()


class OvertalkEvent(sgqlc.types.Type, MediaEvent):
    __schema__ = medallia_schema
    __field_names__ = ()


class Page(sgqlc.types.Type, IPage):
    __schema__ = medallia_schema
    __field_names__ = ()


class PearsonFieldCorrelation(sgqlc.types.Type, FieldCorrelation):
    __schema__ = medallia_schema
    __field_names__ = ()


class PersonalizedAlertAsyncTask(sgqlc.types.Type, AsyncTask):
    __schema__ = medallia_schema
    __field_names__ = ()


class PublishedSocialActivity(sgqlc.types.Type, Activity):
    __schema__ = medallia_schema
    __field_names__ = ('author_title', 'author_name', 'publication_date', 'response_text')
    author_title = sgqlc.types.Field(String, graphql_name='authorTitle')

    author_name = sgqlc.types.Field(String, graphql_name='authorName')

    publication_date = sgqlc.types.Field(DateTime, graphql_name='publicationDate')

    response_text = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name='responseText')



class RankingEnumFieldData(sgqlc.types.Type, EnumFieldData, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ('unranked_options',)
    unranked_options = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(EnumOption))), graphql_name='unrankedOptions')



class RegressionAnalysis(sgqlc.types.Type, XStatsAnalysis):
    __schema__ = medallia_schema
    __field_names__ = ()


class SilenceEvent(sgqlc.types.Type, MediaEvent):
    __schema__ = medallia_schema
    __field_names__ = ()


class SimpleEnumFieldData(sgqlc.types.Type, EnumFieldData, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ()


class SocialFeedbackExternalReplySettings(sgqlc.types.Type, SocialReplySettings):
    __schema__ = medallia_schema
    __field_names__ = ()


class SocialFeedbackIntegratedReplySettings(sgqlc.types.Type, SocialReplySettings):
    __schema__ = medallia_schema
    __field_names__ = ()


class SocialFeedbackRapidResponseReplySettings(sgqlc.types.Type, SocialReplySettings):
    __schema__ = medallia_schema
    __field_names__ = ()


class StandardContactSegment(sgqlc.types.Type, ContactSegment):
    __schema__ = medallia_schema
    __field_names__ = ()


class StringAttributeData(sgqlc.types.Type, AttributeData):
    __schema__ = medallia_schema
    __field_names__ = ()


class StringContactData(sgqlc.types.Type, ContactData):
    __schema__ = medallia_schema
    __field_names__ = ()


class StringField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ('format',)
    format = sgqlc.types.Field(sgqlc.types.non_null(TextFormat), graphql_name='format')



class StringFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ()


class SystemGeneratedLinearRegressionField(sgqlc.types.Type, LinearRegressionField):
    __schema__ = medallia_schema
    __field_names__ = ()


class SystemGeneratedLogisticRegressionField(sgqlc.types.Type, LogisticRegressionField):
    __schema__ = medallia_schema
    __field_names__ = ()


class TimeField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ()


class TimeFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ()


class UnitAttributeData(sgqlc.types.Type, AttributeData):
    __schema__ = medallia_schema
    __field_names__ = ('units',)
    units = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(Unit)), graphql_name='units')



class UnitContactAttribute(sgqlc.types.Type, ContactAttribute):
    __schema__ = medallia_schema
    __field_names__ = ('filterable', 'search_options')
    filterable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='filterable')

    search_options = sgqlc.types.Field(sgqlc.types.non_null(OptionConnection), graphql_name='searchOptions', args=sgqlc.types.ArgDict((
        ('q', sgqlc.types.Arg(String, graphql_name='q', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
))
    )
    '''Arguments:

    * `q` (`String`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    '''



class UnitContactData(sgqlc.types.Type, ContactData):
    __schema__ = medallia_schema
    __field_names__ = ('units',)
    units = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Unit))), graphql_name='units')



class UnitField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ()


class UnitFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ('units',)
    units = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(Unit))), graphql_name='units')



class UnitGroupContactAttribute(sgqlc.types.Type, ContactAttribute):
    __schema__ = medallia_schema
    __field_names__ = ('filterable', 'search_options')
    filterable = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name='filterable')

    search_options = sgqlc.types.Field(sgqlc.types.non_null(OptionConnection), graphql_name='searchOptions', args=sgqlc.types.ArgDict((
        ('q', sgqlc.types.Arg(String, graphql_name='q', default=None)),
        ('first', sgqlc.types.Arg(sgqlc.types.non_null(Int), graphql_name='first', default=30)),
        ('after', sgqlc.types.Arg(ID, graphql_name='after', default=None)),
))
    )
    '''Arguments:

    * `q` (`String`)
    * `first` (`Int!`) (default: `30`)
    * `after` (`ID`)
    '''



class UnitGroupField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ()


class UnitGroupFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ('unit_groups',)
    unit_groups = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(UnitGroup))), graphql_name='unitGroups')



class UrlField(sgqlc.types.Type, Field):
    __schema__ = medallia_schema
    __field_names__ = ()


class UserFieldData(sgqlc.types.Type, FieldData):
    __schema__ = medallia_schema
    __field_names__ = ('users',)
    users = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(User))), graphql_name='users')



class VideoFileMetadata(sgqlc.types.Type, MediaFileMetadata):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsAnalysisAsyncTask(sgqlc.types.Type, AsyncTask):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsBasicError(sgqlc.types.Type, XStatsError):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsFieldsError(sgqlc.types.Type, XStatsError):
    __schema__ = medallia_schema
    __field_names__ = ()


class XStatsWorkbenchAsyncTask(sgqlc.types.Type, AsyncTask):
    __schema__ = medallia_schema
    __field_names__ = ()



########################################################################
# Unions
########################################################################
class ExportSchedulingFrequency(sgqlc.types.Union):
    __schema__ = medallia_schema
    __types__ = (DailyFrequency, WeeklyFrequency, MonthlyFrequency)


class InfinitableFloat(sgqlc.types.Union):
    __schema__ = medallia_schema
    __types__ = (FiniteFloat, InfiniteFloat)


class PersonalizedAlertCriteria(sgqlc.types.Union):
    __schema__ = medallia_schema
    __types__ = (ThresholdCriteria, PercentageCriteria, FeedbackRecordLevelCriteria)


class PersonalizedAlertFrequency(sgqlc.types.Union):
    __schema__ = medallia_schema
    __types__ = (HourlyFrequency, DailyFrequency, WeeklyFrequency, MonthlyFrequency)



########################################################################
# Schema Entry Points
########################################################################
medallia_schema.query_type = Query
medallia_schema.mutation_type = Mutation
medallia_schema.subscription_type = None

