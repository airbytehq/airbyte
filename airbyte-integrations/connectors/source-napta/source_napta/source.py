#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .authenticator import NaptaAuthenticator
from .streams import (
    ApplicationConfig,
    BusinessUnit,
    Cardlabel,
    CareerTrack,
    CareerTrackJobSheet,
    Client,
    EvaluationCampaign,
    EvaluationCampaignEvaluation,
    EvaluationCampaignEvaluationApproval,
    EvaluationCampaignEvaluationAuthor,
    EvaluationCampaignEvaluationTemplate,
    EvaluationCampaignEvaluationUserSkill,
    EvaluationCampaignEvaluationUserSkillGrade,
    Grade,
    GradeGroup,
    JobSheet,
    JobSheetSkill,
    Location,
    Log,
    MetadataField,
    MetadataFieldRight,
    MinimalUser,
    Project,
    ProjectCalendar,
    Projectcategory,
    ProjectContributor,
    ProjectLike,
    ProjectProjectTag,
    Projectstaffingcard,
    ProjectstaffingcardCardlabel,
    Projectstaffingcolumn,
    Projectstatus,
    ProjectTag,
    ProjectTagType,
    ResumeTemplate,
    RexTemplate,
    Skill,
    SkillCategory,
    Timesheet,
    TimesheetPeriod,
    User,
    UserCalendar,
    UserConfig,
    UserGroup,
    UserGroupToUserGroupRight,
    UserHoliday,
    UserHolidayCategory,
    UserJobSheet,
    UserPosition,
    UserPositionToUserProjectEvaluationTemplate,
    UserProject,
    UserProjectBusinessUnitPreference,
    UserProjectEvaluation,
    UserProjectEvaluationApproval,
    UserProjectEvaluationAuthor,
    UserProjectEvaluationTemplate,
    UserProjectEvaluationUserProjectUserSkill,
    UserProjectEvaluationUserProjectUserSkillGrade,
    UserProjectLocationPreference,
    Userprojectperiod,
    UserprojectperiodStatus,
    UserprojectStatus,
    UserProjectUserPositionPreference,
    UserProjectUserPreference,
    UserprojectUserskill,
    UserProjectUserTagPreference,
    UserSkill,
    UserskillInterest,
    UserskillUsergrade,
    UserTag,
    UserTagType,
    UserUserTag,
)


# Source
class SourceNapta(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        """
        Checks the connection by trying to connect to the application_config endpoint, which should exist even in a fresh napta install.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            logger.info("Checking connection...")
            authenticator = NaptaAuthenticator(
                client_id=config["client_id"],
                client_secret=config["client_secret"],
                token_refresh_endpoint="https://auth.napta.io/oauth/token",
            )

            url = "https://app.napta.io/v1/"
            test_path = "application_config"

            response = requests.request(
                method="GET",
                url=url + test_path,
                headers=authenticator.get_request_headers(),
            )

            response.raise_for_status()

            return (True, None)
        except Exception as e:
            return (False, e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        authenticator = NaptaAuthenticator(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            token_refresh_endpoint="https://auth.napta.io/oauth/token",
        )

        return [
            ApplicationConfig(authenticator=authenticator, config=config),
            BusinessUnit(authenticator=authenticator, config=config),
            Cardlabel(authenticator=authenticator, config=config),
            Client(authenticator=authenticator, config=config),
            Grade(authenticator=authenticator, config=config),
            GradeGroup(authenticator=authenticator, config=config),
            Location(authenticator=authenticator, config=config),
            MetadataField(authenticator=authenticator, config=config),
            MinimalUser(authenticator=authenticator, config=config),
            Project(authenticator=authenticator, config=config),
            ProjectContributor(authenticator=authenticator, config=config),
            ProjectProjectTag(authenticator=authenticator, config=config),
            ProjectTag(authenticator=authenticator, config=config),
            ProjectTagType(authenticator=authenticator, config=config),
            Projectcategory(authenticator=authenticator, config=config),
            Projectstaffingcard(authenticator=authenticator, config=config),
            ProjectstaffingcardCardlabel(authenticator=authenticator, config=config),
            Projectstaffingcolumn(authenticator=authenticator, config=config),
            Projectstatus(authenticator=authenticator, config=config),
            Skill(authenticator=authenticator, config=config),
            SkillCategory(authenticator=authenticator, config=config),
            Timesheet(authenticator=authenticator, config=config),
            TimesheetPeriod(authenticator=authenticator, config=config),
            User(authenticator=authenticator, config=config),
            UserConfig(authenticator=authenticator, config=config),
            UserGroup(authenticator=authenticator, config=config),
            UserGroupToUserGroupRight(authenticator=authenticator, config=config),
            UserHoliday(authenticator=authenticator, config=config),
            UserHolidayCategory(authenticator=authenticator, config=config),
            UserPosition(authenticator=authenticator, config=config),
            UserProject(authenticator=authenticator, config=config),
            UserProjectBusinessUnitPreference(authenticator=authenticator, config=config),
            UserProjectLocationPreference(authenticator=authenticator, config=config),
            UserProjectUserPositionPreference(authenticator=authenticator, config=config),
            UserProjectUserTagPreference(authenticator=authenticator, config=config),
            UserSkill(authenticator=authenticator, config=config),
            UserTag(authenticator=authenticator, config=config),
            UserTagType(authenticator=authenticator, config=config),
            UserUserTag(authenticator=authenticator, config=config),
            UserprojectStatus(authenticator=authenticator, config=config),
            UserprojectUserskill(authenticator=authenticator, config=config),
            Userprojectperiod(authenticator=authenticator, config=config),
            UserprojectperiodStatus(authenticator=authenticator, config=config),
            UserskillInterest(authenticator=authenticator, config=config),
        ]
