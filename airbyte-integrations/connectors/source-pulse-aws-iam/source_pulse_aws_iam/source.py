from typing import Any, List, Mapping, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_pulse_aws_iam.streams import ListAccountsStream, RolePoliciesStream, GroupPoliciesStream, UserPoliciesStream

from .streams import UsersStream, GroupsStream, RolesStream, PoliciesStream, AccessKeysStream, CloudTrailEventsStream, \
    AccessAnalyzersStream, AnalyzerFindingsStream, CredentialReportStream, OrganizationDetailsStream, IdentityProvidersStream


class SourcePulseAwsIam(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        try:
            stream = UsersStream(config=config)
            next(stream.read_records(sync_mode=None))
            return True, None
        except Exception as e:
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [UsersStream(config=config),
                GroupsStream(config=config),
                RolesStream(config=config),
                PoliciesStream(config=config),
                AccessKeysStream(config=config),
                CloudTrailEventsStream(config=config),
                AccessAnalyzersStream(config=config),
                AnalyzerFindingsStream(config=config),
                CredentialReportStream(config=config),
                OrganizationDetailsStream(config=config),
                IdentityProvidersStream(config=config),
                ListAccountsStream(config=config),
                RolePoliciesStream(config=config),
                GroupPoliciesStream(config=config),
                UserPoliciesStream(config=config),
                ]
