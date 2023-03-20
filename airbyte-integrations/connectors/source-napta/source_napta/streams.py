from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from airbyte_cdk.sources.streams.http.http import HttpStream


class NaptaStream(HttpStream, ABC):
    primary_key = "id"
    url_base = "https://app.napta.io/api/v1/"

    def __init__(self, authenticator: Oauth2Authenticator, config: Mapping[str, Any]) -> None:
        self.config = config
        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_json = response.json()
        next_page = response_json.get("links").get("next")
        if next_page:
            return {"next_url": next_page}
        return None

    def request_params(
        self,
        stream_state: Optional[Mapping[str, Any]],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            # Here's the pagination logic
            # As I have not found a way to insert the next url directly, I split it to get the page number
            return {"page[number]": next_page_token["next_url"].split("=")[-1], "page[size]": self.config["page_size"]}
        return {"page[size]": self.config["page_size"]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["data"]


class IncrementalNaptaStream(NaptaStream):
    pass


class UserConfig(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_config"


class RexTemplate(NaptaStream):
    def path(self, **kwargs) -> str:
        return "rex_template"


class ResumeTemplate(NaptaStream):
    def path(self, **kwargs) -> str:
        return "resume_template"


class User(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user"


class MinimalUser(NaptaStream):
    def path(self, **kwargs) -> str:
        return "minimal_user"


class UserCalendar(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_calendar"


class ProjectCalendar(NaptaStream):
    def path(self, **kwargs) -> str:
        return "project_calendar"


class Location(NaptaStream):
    def path(self, **kwargs) -> str:
        return "location"


class UserGroup(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_group"


class GradeGroup(NaptaStream):
    def path(self, **kwargs) -> str:
        return "grade_group"


class Skill(NaptaStream):
    def path(self, **kwargs) -> str:
        return "skill"


class SkillCategory(NaptaStream):
    def path(self, **kwargs) -> str:
        return "skill_category"


class Client(NaptaStream):
    def path(self, **kwargs) -> str:
        return "client"


class Project(NaptaStream):
    def path(self, **kwargs) -> str:
        return "project"


class UserSkill(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_skill"


class UserHoliday(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_holiday"


class UserHolidayCategory(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_holiday_category"


class Log(NaptaStream):
    def path(self, **kwargs) -> str:
        return "log"


class UserPosition(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_position"


class Grade(NaptaStream):
    def path(self, **kwargs) -> str:
        return "grade"


class UserProject(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project"


class UserprojectUserskill(NaptaStream):
    def path(self, **kwargs) -> str:
        return "userproject_userskill"


class UserProjectEvaluationUserProjectUserSkillGrade(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_evaluation_user_project_user_skill_grade"


class UserProjectEvaluationUserProjectUserSkill(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_evaluation_user_project_user_skill"


class UserskillUsergrade(NaptaStream):
    def path(self, **kwargs) -> str:
        return "userskill_usergrade"


class Userprojectperiod(NaptaStream):
    def path(self, **kwargs) -> str:
        return "userprojectperiod"


class UserprojectperiodStatus(NaptaStream):
    def path(self, **kwargs) -> str:
        return "userprojectperiod_status"


class ApplicationConfig(NaptaStream):
    def path(self, **kwargs) -> str:
        return "application_config"


class Projectstaffingcard(NaptaStream):
    def path(self, **kwargs) -> str:
        return "projectstaffingcard"


class Projectstaffingcolumn(NaptaStream):
    def path(self, **kwargs) -> str:
        return "projectstaffingcolumn"


class ProjectstaffingcardCardlabel(NaptaStream):
    def path(self, **kwargs) -> str:
        return "projectstaffingcard_cardlabel"


class Cardlabel(NaptaStream):
    def path(self, **kwargs) -> str:
        return "cardlabel"


class Projectstatus(NaptaStream):
    def path(self, **kwargs) -> str:
        return "projectstatus"


class Projectcategory(NaptaStream):
    def path(self, **kwargs) -> str:
        return "projectcategory"


class UserprojectStatus(NaptaStream):
    def path(self, **kwargs) -> str:
        return "userproject_status"


class MetadataField(NaptaStream):
    def path(self, **kwargs) -> str:
        return "metadata_field"


class MetadataFieldRight(NaptaStream):
    def path(self, **kwargs) -> str:
        return "metadata_field_right"


class BusinessUnit(NaptaStream):
    def path(self, **kwargs) -> str:
        return "business_unit"


class UserskillInterest(NaptaStream):
    def path(self, **kwargs) -> str:
        return "userskill_interest"


class EvaluationCampaign(NaptaStream):
    def path(self, **kwargs) -> str:
        return "evaluation_campaign"


class EvaluationCampaignEvaluation(NaptaStream):
    def path(self, **kwargs) -> str:
        return "evaluation_campaign_evaluation"


class EvaluationCampaignEvaluationAuthor(NaptaStream):
    def path(self, **kwargs) -> str:
        return "evaluation_campaign_evaluation_author"


class EvaluationCampaignEvaluationUserSkill(NaptaStream):
    def path(self, **kwargs) -> str:
        return "evaluation_campaign_evaluation_user_skill"


class EvaluationCampaignEvaluationUserSkillGrade(NaptaStream):
    def path(self, **kwargs) -> str:
        return "evaluation_campaign_evaluation_user_skill_grade"


class UserPositionToUserProjectEvaluationTemplate(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_position_to_user_project_evaluation_template"


class UserProjectEvaluation(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_evaluation"


class UserProjectEvaluationAuthor(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_evaluation_author"


class UserProjectEvaluationTemplate(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_evaluation_template"


class UserGroupToUserGroupRight(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_group_to_user_group_right"


class EvaluationCampaignEvaluationTemplate(NaptaStream):
    def path(self, **kwargs) -> str:
        return "evaluation_campaign_evaluation_template"


class UserProjectUserPreference(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_user_preference"


class UserProjectUserPositionPreference(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_user_position_preference"


class UserProjectBusinessUnitPreference(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_business_unit_preference"


class UserProjectLocationPreference(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_location_preference"


class UserUserTag(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_user_tag"


class UserTagType(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_tag_type"


class UserTag(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_tag"


class UserProjectUserTagPreference(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_user_tag_preference"


class EvaluationCampaignEvaluationApproval(NaptaStream):
    def path(self, **kwargs) -> str:
        return "evaluation_campaign_evaluation_approval"


class UserProjectEvaluationApproval(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_project_evaluation_approval"


class ProjectContributor(NaptaStream):
    def path(self, **kwargs) -> str:
        return "project_contributor"


class ProjectLike(NaptaStream):
    def path(self, **kwargs) -> str:
        return "project_like"


class ProjectProjectTag(NaptaStream):
    def path(self, **kwargs) -> str:
        return "project_project_tag"


class ProjectTagType(NaptaStream):
    def path(self, **kwargs) -> str:
        return "project_tag_type"


class ProjectTag(NaptaStream):
    def path(self, **kwargs) -> str:
        return "project_tag"


class JobSheet(NaptaStream):
    def path(self, **kwargs) -> str:
        return "job_sheet"


class JobSheetSkill(NaptaStream):
    def path(self, **kwargs) -> str:
        return "job_sheet_skill"


class UserJobSheet(NaptaStream):
    def path(self, **kwargs) -> str:
        return "user_job_sheet"


class CareerTrack(NaptaStream):
    def path(self, **kwargs) -> str:
        return "career_track"


class CareerTrackJobSheet(NaptaStream):
    def path(self, **kwargs) -> str:
        return "career_track_job_sheet"


class Timesheet(NaptaStream):
    def path(self, **kwargs) -> str:
        return "timesheet"


class TimesheetPeriod(NaptaStream):
    def path(self, **kwargs) -> str:
        return "timesheet_period"
