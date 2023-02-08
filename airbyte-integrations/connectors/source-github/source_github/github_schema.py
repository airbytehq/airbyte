#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sgqlc.types
import sgqlc.types.datetime
import sgqlc.types.relay

github_schema = sgqlc.types.Schema()


# Unexport Node/PageInfo, let schema re-declare them
github_schema -= sgqlc.types.relay.Node
github_schema -= sgqlc.types.relay.PageInfo


__docformat__ = "markdown"


########################################################################
# Scalars and Enumerations
########################################################################
class ActorType(sgqlc.types.Enum):
    """The actor's type.

    Enumeration Choices:

    * `TEAM`: Indicates a team actor.
    * `USER`: Indicates a user actor.
    """

    __schema__ = github_schema
    __choices__ = ("TEAM", "USER")


class AuditLogOrderField(sgqlc.types.Enum):
    """Properties by which Audit Log connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order audit log entries by timestamp
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class Base64String(sgqlc.types.Scalar):
    """A (potentially binary) string encoded using base64."""

    __schema__ = github_schema


Boolean = sgqlc.types.Boolean


class CheckAnnotationLevel(sgqlc.types.Enum):
    """Represents an annotation's information level.

    Enumeration Choices:

    * `FAILURE`: An annotation indicating an inescapable error.
    * `NOTICE`: An annotation indicating some information.
    * `WARNING`: An annotation indicating an ignorable error.
    """

    __schema__ = github_schema
    __choices__ = ("FAILURE", "NOTICE", "WARNING")


class CheckConclusionState(sgqlc.types.Enum):
    """The possible states for a check suite or run conclusion.

    Enumeration Choices:

    * `ACTION_REQUIRED`: The check suite or run requires action.
    * `CANCELLED`: The check suite or run has been cancelled.
    * `FAILURE`: The check suite or run has failed.
    * `NEUTRAL`: The check suite or run was neutral.
    * `SKIPPED`: The check suite or run was skipped.
    * `STALE`: The check suite or run was marked stale by GitHub. Only
      GitHub can use this conclusion.
    * `STARTUP_FAILURE`: The check suite or run has failed at startup.
    * `SUCCESS`: The check suite or run has succeeded.
    * `TIMED_OUT`: The check suite or run has timed out.
    """

    __schema__ = github_schema
    __choices__ = ("ACTION_REQUIRED", "CANCELLED", "FAILURE", "NEUTRAL", "SKIPPED", "STALE", "STARTUP_FAILURE", "SUCCESS", "TIMED_OUT")


class CheckRunType(sgqlc.types.Enum):
    """The possible types of check runs.

    Enumeration Choices:

    * `ALL`: Every check run available.
    * `LATEST`: The latest check run.
    """

    __schema__ = github_schema
    __choices__ = ("ALL", "LATEST")


class CheckStatusState(sgqlc.types.Enum):
    """The possible states for a check suite or run status.

    Enumeration Choices:

    * `COMPLETED`: The check suite or run has been completed.
    * `IN_PROGRESS`: The check suite or run is in progress.
    * `PENDING`: The check suite or run is in pending state.
    * `QUEUED`: The check suite or run has been queued.
    * `REQUESTED`: The check suite or run has been requested.
    * `WAITING`: The check suite or run is in waiting state.
    """

    __schema__ = github_schema
    __choices__ = ("COMPLETED", "IN_PROGRESS", "PENDING", "QUEUED", "REQUESTED", "WAITING")


class CollaboratorAffiliation(sgqlc.types.Enum):
    """Collaborators affiliation level with a subject.

    Enumeration Choices:

    * `ALL`: All collaborators the authenticated user can see.
    * `DIRECT`: All collaborators with permissions to an organization-
      owned subject, regardless of organization membership status.
    * `OUTSIDE`: All outside collaborators of an organization-owned
      subject.
    """

    __schema__ = github_schema
    __choices__ = ("ALL", "DIRECT", "OUTSIDE")


class CommentAuthorAssociation(sgqlc.types.Enum):
    """A comment author association with repository.

    Enumeration Choices:

    * `COLLABORATOR`: Author has been invited to collaborate on the
      repository.
    * `CONTRIBUTOR`: Author has previously committed to the
      repository.
    * `FIRST_TIMER`: Author has not previously committed to GitHub.
    * `FIRST_TIME_CONTRIBUTOR`: Author has not previously committed to
      the repository.
    * `MANNEQUIN`: Author is a placeholder for an unclaimed user.
    * `MEMBER`: Author is a member of the organization that owns the
      repository.
    * `NONE`: Author has no association with the repository.
    * `OWNER`: Author is the owner of the repository.
    """

    __schema__ = github_schema
    __choices__ = ("COLLABORATOR", "CONTRIBUTOR", "FIRST_TIMER", "FIRST_TIME_CONTRIBUTOR", "MANNEQUIN", "MEMBER", "NONE", "OWNER")


class CommentCannotUpdateReason(sgqlc.types.Enum):
    """The possible errors that will prevent a user from updating a
    comment.

    Enumeration Choices:

    * `ARCHIVED`: Unable to create comment because repository is
      archived.
    * `DENIED`: You cannot update this comment
    * `INSUFFICIENT_ACCESS`: You must be the author or have write
      access to this repository to update this comment.
    * `LOCKED`: Unable to create comment because issue is locked.
    * `LOGIN_REQUIRED`: You must be logged in to update this comment.
    * `MAINTENANCE`: Repository is under maintenance.
    * `VERIFIED_EMAIL_REQUIRED`: At least one email address must be
      verified to update this comment.
    """

    __schema__ = github_schema
    __choices__ = ("ARCHIVED", "DENIED", "INSUFFICIENT_ACCESS", "LOCKED", "LOGIN_REQUIRED", "MAINTENANCE", "VERIFIED_EMAIL_REQUIRED")


class CommitContributionOrderField(sgqlc.types.Enum):
    """Properties by which commit contribution connections can be
    ordered.

    Enumeration Choices:

    * `COMMIT_COUNT`: Order commit contributions by how many commits
      they represent.
    * `OCCURRED_AT`: Order commit contributions by when they were
      made.
    """

    __schema__ = github_schema
    __choices__ = ("COMMIT_COUNT", "OCCURRED_AT")


class ContributionLevel(sgqlc.types.Enum):
    """Varying levels of contributions from none to many.

    Enumeration Choices:

    * `FIRST_QUARTILE`: Lowest 25% of days of contributions.
    * `FOURTH_QUARTILE`: Highest 25% of days of contributions. More
      contributions than the third quartile.
    * `NONE`: No contributions occurred.
    * `SECOND_QUARTILE`: Second lowest 25% of days of contributions.
      More contributions than the first quartile.
    * `THIRD_QUARTILE`: Second highest 25% of days of contributions.
      More contributions than second quartile, less than the fourth
      quartile.
    """

    __schema__ = github_schema
    __choices__ = ("FIRST_QUARTILE", "FOURTH_QUARTILE", "NONE", "SECOND_QUARTILE", "THIRD_QUARTILE")


Date = sgqlc.types.datetime.Date

DateTime = sgqlc.types.datetime.DateTime


class DefaultRepositoryPermissionField(sgqlc.types.Enum):
    """The possible base permissions for repositories.

    Enumeration Choices:

    * `ADMIN`: Can read, write, and administrate repos by default
    * `NONE`: No access
    * `READ`: Can read repos by default
    * `WRITE`: Can read and write repos by default
    """

    __schema__ = github_schema
    __choices__ = ("ADMIN", "NONE", "READ", "WRITE")


class DependencyGraphEcosystem(sgqlc.types.Enum):
    """The possible ecosystems of a dependency graph package.

    Enumeration Choices:

    * `ACTIONS`: GitHub Actions
    * `COMPOSER`: PHP packages hosted at packagist.org
    * `GO`: Go modules
    * `MAVEN`: Java artifacts hosted at the Maven central repository
    * `NPM`: JavaScript packages hosted at npmjs.com
    * `NUGET`: .NET packages hosted at the NuGet Gallery
    * `PIP`: Python packages hosted at PyPI.org
    * `RUBYGEMS`: Ruby gems hosted at RubyGems.org
    * `RUST`: Rust crates
    """

    __schema__ = github_schema
    __choices__ = ("ACTIONS", "COMPOSER", "GO", "MAVEN", "NPM", "NUGET", "PIP", "RUBYGEMS", "RUST")


class DeploymentOrderField(sgqlc.types.Enum):
    """Properties by which deployment connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order collection by creation time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class DeploymentProtectionRuleType(sgqlc.types.Enum):
    """The possible protection rule types.

    Enumeration Choices:

    * `REQUIRED_REVIEWERS`: Required reviewers
    * `WAIT_TIMER`: Wait timer
    """

    __schema__ = github_schema
    __choices__ = ("REQUIRED_REVIEWERS", "WAIT_TIMER")


class DeploymentReviewState(sgqlc.types.Enum):
    """The possible states for a deployment review.

    Enumeration Choices:

    * `APPROVED`: The deployment was approved.
    * `REJECTED`: The deployment was rejected.
    """

    __schema__ = github_schema
    __choices__ = ("APPROVED", "REJECTED")


class DeploymentState(sgqlc.types.Enum):
    """The possible states in which a deployment can be.

    Enumeration Choices:

    * `ABANDONED`: The pending deployment was not updated after 30
      minutes.
    * `ACTIVE`: The deployment is currently active.
    * `DESTROYED`: An inactive transient deployment.
    * `ERROR`: The deployment experienced an error.
    * `FAILURE`: The deployment has failed.
    * `INACTIVE`: The deployment is inactive.
    * `IN_PROGRESS`: The deployment is in progress.
    * `PENDING`: The deployment is pending.
    * `QUEUED`: The deployment has queued
    * `WAITING`: The deployment is waiting.
    """

    __schema__ = github_schema
    __choices__ = ("ABANDONED", "ACTIVE", "DESTROYED", "ERROR", "FAILURE", "INACTIVE", "IN_PROGRESS", "PENDING", "QUEUED", "WAITING")


class DeploymentStatusState(sgqlc.types.Enum):
    """The possible states for a deployment status.

    Enumeration Choices:

    * `ERROR`: The deployment experienced an error.
    * `FAILURE`: The deployment has failed.
    * `INACTIVE`: The deployment is inactive.
    * `IN_PROGRESS`: The deployment is in progress.
    * `PENDING`: The deployment is pending.
    * `QUEUED`: The deployment is queued
    * `SUCCESS`: The deployment was successful.
    * `WAITING`: The deployment is waiting.
    """

    __schema__ = github_schema
    __choices__ = ("ERROR", "FAILURE", "INACTIVE", "IN_PROGRESS", "PENDING", "QUEUED", "SUCCESS", "WAITING")


class DiffSide(sgqlc.types.Enum):
    """The possible sides of a diff.

    Enumeration Choices:

    * `LEFT`: The left side of the diff.
    * `RIGHT`: The right side of the diff.
    """

    __schema__ = github_schema
    __choices__ = ("LEFT", "RIGHT")


class DiscussionOrderField(sgqlc.types.Enum):
    """Properties by which discussion connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order discussions by creation time.
    * `UPDATED_AT`: Order discussions by most recent modification
      time.
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "UPDATED_AT")


class DiscussionPollOptionOrderField(sgqlc.types.Enum):
    """Properties by which discussion poll option connections can be
    ordered.

    Enumeration Choices:

    * `AUTHORED_ORDER`: Order poll options by the order that the poll
      author specified when creating the poll.
    * `VOTE_COUNT`: Order poll options by the number of votes it has.
    """

    __schema__ = github_schema
    __choices__ = ("AUTHORED_ORDER", "VOTE_COUNT")


class DismissReason(sgqlc.types.Enum):
    """The possible reasons that a Dependabot alert was dismissed.

    Enumeration Choices:

    * `FIX_STARTED`: A fix has already been started
    * `INACCURATE`: This alert is inaccurate or incorrect
    * `NOT_USED`: Vulnerable code is not actually used
    * `NO_BANDWIDTH`: No bandwidth to fix this
    * `TOLERABLE_RISK`: Risk is tolerable to this project
    """

    __schema__ = github_schema
    __choices__ = ("FIX_STARTED", "INACCURATE", "NOT_USED", "NO_BANDWIDTH", "TOLERABLE_RISK")


class EnterpriseAdministratorInvitationOrderField(sgqlc.types.Enum):
    """Properties by which enterprise administrator invitation
    connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order enterprise administrator member invitations
      by creation time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class EnterpriseAdministratorRole(sgqlc.types.Enum):
    """The possible administrator roles in an enterprise account.

    Enumeration Choices:

    * `BILLING_MANAGER`: Represents a billing manager of the
      enterprise account.
    * `OWNER`: Represents an owner of the enterprise account.
    """

    __schema__ = github_schema
    __choices__ = ("BILLING_MANAGER", "OWNER")


class EnterpriseDefaultRepositoryPermissionSettingValue(sgqlc.types.Enum):
    """The possible values for the enterprise base repository permission
    setting.

    Enumeration Choices:

    * `ADMIN`: Organization members will be able to clone, pull, push,
      and add new collaborators to all organization repositories.
    * `NONE`: Organization members will only be able to clone and pull
      public repositories.
    * `NO_POLICY`: Organizations in the enterprise choose base
      repository permissions for their members.
    * `READ`: Organization members will be able to clone and pull all
      organization repositories.
    * `WRITE`: Organization members will be able to clone, pull, and
      push all organization repositories.
    """

    __schema__ = github_schema
    __choices__ = ("ADMIN", "NONE", "NO_POLICY", "READ", "WRITE")


class EnterpriseEnabledDisabledSettingValue(sgqlc.types.Enum):
    """The possible values for an enabled/disabled enterprise setting.

    Enumeration Choices:

    * `DISABLED`: The setting is disabled for organizations in the
      enterprise.
    * `ENABLED`: The setting is enabled for organizations in the
      enterprise.
    * `NO_POLICY`: There is no policy set for organizations in the
      enterprise.
    """

    __schema__ = github_schema
    __choices__ = ("DISABLED", "ENABLED", "NO_POLICY")


class EnterpriseEnabledSettingValue(sgqlc.types.Enum):
    """The possible values for an enabled/no policy enterprise setting.

    Enumeration Choices:

    * `ENABLED`: The setting is enabled for organizations in the
      enterprise.
    * `NO_POLICY`: There is no policy set for organizations in the
      enterprise.
    """

    __schema__ = github_schema
    __choices__ = ("ENABLED", "NO_POLICY")


class EnterpriseMemberOrderField(sgqlc.types.Enum):
    """Properties by which enterprise member connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order enterprise members by creation time
    * `LOGIN`: Order enterprise members by login
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "LOGIN")


class EnterpriseMembersCanCreateRepositoriesSettingValue(sgqlc.types.Enum):
    """The possible values for the enterprise members can create
    repositories setting.

    Enumeration Choices:

    * `ALL`: Members will be able to create public and private
      repositories.
    * `DISABLED`: Members will not be able to create public or private
      repositories.
    * `NO_POLICY`: Organization administrators choose whether to allow
      members to create repositories.
    * `PRIVATE`: Members will be able to create only private
      repositories.
    * `PUBLIC`: Members will be able to create only public
      repositories.
    """

    __schema__ = github_schema
    __choices__ = ("ALL", "DISABLED", "NO_POLICY", "PRIVATE", "PUBLIC")


class EnterpriseMembersCanMakePurchasesSettingValue(sgqlc.types.Enum):
    """The possible values for the members can make purchases setting.

    Enumeration Choices:

    * `DISABLED`: The setting is disabled for organizations in the
      enterprise.
    * `ENABLED`: The setting is enabled for organizations in the
      enterprise.
    """

    __schema__ = github_schema
    __choices__ = ("DISABLED", "ENABLED")


class EnterpriseServerInstallationOrderField(sgqlc.types.Enum):
    """Properties by which Enterprise Server installation connections can
    be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order Enterprise Server installations by creation
      time
    * `CUSTOMER_NAME`: Order Enterprise Server installations by
      customer name
    * `HOST_NAME`: Order Enterprise Server installations by host name
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "CUSTOMER_NAME", "HOST_NAME")


class EnterpriseServerUserAccountEmailOrderField(sgqlc.types.Enum):
    """Properties by which Enterprise Server user account email
    connections can be ordered.

    Enumeration Choices:

    * `EMAIL`: Order emails by email
    """

    __schema__ = github_schema
    __choices__ = ("EMAIL",)


class EnterpriseServerUserAccountOrderField(sgqlc.types.Enum):
    """Properties by which Enterprise Server user account connections can
    be ordered.

    Enumeration Choices:

    * `LOGIN`: Order user accounts by login
    * `REMOTE_CREATED_AT`: Order user accounts by creation time on the
      Enterprise Server installation
    """

    __schema__ = github_schema
    __choices__ = ("LOGIN", "REMOTE_CREATED_AT")


class EnterpriseServerUserAccountsUploadOrderField(sgqlc.types.Enum):
    """Properties by which Enterprise Server user accounts upload
    connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order user accounts uploads by creation time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class EnterpriseServerUserAccountsUploadSyncState(sgqlc.types.Enum):
    """Synchronization state of the Enterprise Server user accounts
    upload

    Enumeration Choices:

    * `FAILURE`: The synchronization of the upload failed.
    * `PENDING`: The synchronization of the upload is pending.
    * `SUCCESS`: The synchronization of the upload succeeded.
    """

    __schema__ = github_schema
    __choices__ = ("FAILURE", "PENDING", "SUCCESS")


class EnterpriseUserAccountMembershipRole(sgqlc.types.Enum):
    """The possible roles for enterprise membership.

    Enumeration Choices:

    * `MEMBER`: The user is a member of an organization in the
      enterprise.
    * `OWNER`: The user is an owner of an organization in the
      enterprise.
    """

    __schema__ = github_schema
    __choices__ = ("MEMBER", "OWNER")


class EnterpriseUserDeployment(sgqlc.types.Enum):
    """The possible GitHub Enterprise deployments where this user can
    exist.

    Enumeration Choices:

    * `CLOUD`: The user is part of a GitHub Enterprise Cloud
      deployment.
    * `SERVER`: The user is part of a GitHub Enterprise Server
      deployment.
    """

    __schema__ = github_schema
    __choices__ = ("CLOUD", "SERVER")


class FileViewedState(sgqlc.types.Enum):
    """The possible viewed states of a file .

    Enumeration Choices:

    * `DISMISSED`: The file has new changes since last viewed.
    * `UNVIEWED`: The file has not been marked as viewed.
    * `VIEWED`: The file has been marked as viewed.
    """

    __schema__ = github_schema
    __choices__ = ("DISMISSED", "UNVIEWED", "VIEWED")


Float = sgqlc.types.Float


class FundingPlatform(sgqlc.types.Enum):
    """The possible funding platforms for repository funding links.

    Enumeration Choices:

    * `COMMUNITY_BRIDGE`: Community Bridge funding platform.
    * `CUSTOM`: Custom funding platform.
    * `GITHUB`: GitHub funding platform.
    * `ISSUEHUNT`: IssueHunt funding platform.
    * `KO_FI`: Ko-fi funding platform.
    * `LFX_CROWDFUNDING`: LFX Crowdfunding funding platform.
    * `LIBERAPAY`: Liberapay funding platform.
    * `OPEN_COLLECTIVE`: Open Collective funding platform.
    * `OTECHIE`: Otechie funding platform.
    * `PATREON`: Patreon funding platform.
    * `TIDELIFT`: Tidelift funding platform.
    """

    __schema__ = github_schema
    __choices__ = (
        "COMMUNITY_BRIDGE",
        "CUSTOM",
        "GITHUB",
        "ISSUEHUNT",
        "KO_FI",
        "LFX_CROWDFUNDING",
        "LIBERAPAY",
        "OPEN_COLLECTIVE",
        "OTECHIE",
        "PATREON",
        "TIDELIFT",
    )


class GistOrderField(sgqlc.types.Enum):
    """Properties by which gist connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order gists by creation time
    * `PUSHED_AT`: Order gists by push time
    * `UPDATED_AT`: Order gists by update time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "PUSHED_AT", "UPDATED_AT")


class GistPrivacy(sgqlc.types.Enum):
    """The privacy of a Gist

    Enumeration Choices:

    * `ALL`: Gists that are public and secret
    * `PUBLIC`: Public
    * `SECRET`: Secret
    """

    __schema__ = github_schema
    __choices__ = ("ALL", "PUBLIC", "SECRET")


class GitObjectID(sgqlc.types.Scalar):
    """A Git object ID."""

    __schema__ = github_schema


class GitSSHRemote(sgqlc.types.Scalar):
    """Git SSH string"""

    __schema__ = github_schema


class GitSignatureState(sgqlc.types.Enum):
    """The state of a Git signature.

    Enumeration Choices:

    * `BAD_CERT`: The signing certificate or its chain could not be
      verified
    * `BAD_EMAIL`: Invalid email used for signing
    * `EXPIRED_KEY`: Signing key expired
    * `GPGVERIFY_ERROR`: Internal error - the GPG verification service
      misbehaved
    * `GPGVERIFY_UNAVAILABLE`: Internal error - the GPG verification
      service is unavailable at the moment
    * `INVALID`: Invalid signature
    * `MALFORMED_SIG`: Malformed signature
    * `NOT_SIGNING_KEY`: The usage flags for the key that signed this
      don't allow signing
    * `NO_USER`: Email used for signing not known to GitHub
    * `OCSP_ERROR`: Valid signature, though certificate revocation
      check failed
    * `OCSP_PENDING`: Valid signature, pending certificate revocation
      checking
    * `OCSP_REVOKED`: One or more certificates in chain has been
      revoked
    * `UNKNOWN_KEY`: Key used for signing not known to GitHub
    * `UNKNOWN_SIG_TYPE`: Unknown signature type
    * `UNSIGNED`: Unsigned
    * `UNVERIFIED_EMAIL`: Email used for signing unverified on GitHub
    * `VALID`: Valid signature and verified by GitHub
    """

    __schema__ = github_schema
    __choices__ = (
        "BAD_CERT",
        "BAD_EMAIL",
        "EXPIRED_KEY",
        "GPGVERIFY_ERROR",
        "GPGVERIFY_UNAVAILABLE",
        "INVALID",
        "MALFORMED_SIG",
        "NOT_SIGNING_KEY",
        "NO_USER",
        "OCSP_ERROR",
        "OCSP_PENDING",
        "OCSP_REVOKED",
        "UNKNOWN_KEY",
        "UNKNOWN_SIG_TYPE",
        "UNSIGNED",
        "UNVERIFIED_EMAIL",
        "VALID",
    )


class GitTimestamp(sgqlc.types.Scalar):
    """An ISO-8601 encoded date string. Unlike the DateTime type,
    GitTimestamp is not converted in UTC.
    """

    __schema__ = github_schema


class HTML(sgqlc.types.Scalar):
    """A string containing HTML code."""

    __schema__ = github_schema


ID = sgqlc.types.ID


class IdentityProviderConfigurationState(sgqlc.types.Enum):
    """The possible states in which authentication can be configured with
    an identity provider.

    Enumeration Choices:

    * `CONFIGURED`: Authentication with an identity provider is
      configured but not enforced.
    * `ENFORCED`: Authentication with an identity provider is
      configured and enforced.
    * `UNCONFIGURED`: Authentication with an identity provider is not
      configured.
    """

    __schema__ = github_schema
    __choices__ = ("CONFIGURED", "ENFORCED", "UNCONFIGURED")


Int = sgqlc.types.Int


class IpAllowListEnabledSettingValue(sgqlc.types.Enum):
    """The possible values for the IP allow list enabled setting.

    Enumeration Choices:

    * `DISABLED`: The setting is disabled for the owner.
    * `ENABLED`: The setting is enabled for the owner.
    """

    __schema__ = github_schema
    __choices__ = ("DISABLED", "ENABLED")


class IpAllowListEntryOrderField(sgqlc.types.Enum):
    """Properties by which IP allow list entry connections can be
    ordered.

    Enumeration Choices:

    * `ALLOW_LIST_VALUE`: Order IP allow list entries by the allow
      list value.
    * `CREATED_AT`: Order IP allow list entries by creation time.
    """

    __schema__ = github_schema
    __choices__ = ("ALLOW_LIST_VALUE", "CREATED_AT")


class IpAllowListForInstalledAppsEnabledSettingValue(sgqlc.types.Enum):
    """The possible values for the IP allow list configuration for
    installed GitHub Apps setting.

    Enumeration Choices:

    * `DISABLED`: The setting is disabled for the owner.
    * `ENABLED`: The setting is enabled for the owner.
    """

    __schema__ = github_schema
    __choices__ = ("DISABLED", "ENABLED")


class IssueClosedStateReason(sgqlc.types.Enum):
    """The possible state reasons of a closed issue.

    Enumeration Choices:

    * `COMPLETED`: An issue that has been closed as completed
    * `NOT_PLANNED`: An issue that has been closed as not planned
    """

    __schema__ = github_schema
    __choices__ = ("COMPLETED", "NOT_PLANNED")


class IssueCommentOrderField(sgqlc.types.Enum):
    """Properties by which issue comment connections can be ordered.

    Enumeration Choices:

    * `UPDATED_AT`: Order issue comments by update time
    """

    __schema__ = github_schema
    __choices__ = ("UPDATED_AT",)


class IssueOrderField(sgqlc.types.Enum):
    """Properties by which issue connections can be ordered.

    Enumeration Choices:

    * `COMMENTS`: Order issues by comment count
    * `CREATED_AT`: Order issues by creation time
    * `UPDATED_AT`: Order issues by update time
    """

    __schema__ = github_schema
    __choices__ = ("COMMENTS", "CREATED_AT", "UPDATED_AT")


class IssueState(sgqlc.types.Enum):
    """The possible states of an issue.

    Enumeration Choices:

    * `CLOSED`: An issue that has been closed
    * `OPEN`: An issue that is still open
    """

    __schema__ = github_schema
    __choices__ = ("CLOSED", "OPEN")


class IssueStateReason(sgqlc.types.Enum):
    """The possible state reasons of an issue.

    Enumeration Choices:

    * `COMPLETED`: An issue that has been closed as completed
    * `NOT_PLANNED`: An issue that has been closed as not planned
    * `REOPENED`: An issue that has been reopened
    """

    __schema__ = github_schema
    __choices__ = ("COMPLETED", "NOT_PLANNED", "REOPENED")


class IssueTimelineItemsItemType(sgqlc.types.Enum):
    """The possible item types found in a timeline.

    Enumeration Choices:

    * `ADDED_TO_PROJECT_EVENT`: Represents a 'added_to_project' event
      on a given issue or pull request.
    * `ASSIGNED_EVENT`: Represents an 'assigned' event on any
      assignable object.
    * `CLOSED_EVENT`: Represents a 'closed' event on any `Closable`.
    * `COMMENT_DELETED_EVENT`: Represents a 'comment_deleted' event on
      a given issue or pull request.
    * `CONNECTED_EVENT`: Represents a 'connected' event on a given
      issue or pull request.
    * `CONVERTED_NOTE_TO_ISSUE_EVENT`: Represents a
      'converted_note_to_issue' event on a given issue or pull
      request.
    * `CONVERTED_TO_DISCUSSION_EVENT`: Represents a
      'converted_to_discussion' event on a given issue.
    * `CROSS_REFERENCED_EVENT`: Represents a mention made by one issue
      or pull request to another.
    * `DEMILESTONED_EVENT`: Represents a 'demilestoned' event on a
      given issue or pull request.
    * `DISCONNECTED_EVENT`: Represents a 'disconnected' event on a
      given issue or pull request.
    * `ISSUE_COMMENT`: Represents a comment on an Issue.
    * `LABELED_EVENT`: Represents a 'labeled' event on a given issue
      or pull request.
    * `LOCKED_EVENT`: Represents a 'locked' event on a given issue or
      pull request.
    * `MARKED_AS_DUPLICATE_EVENT`: Represents a 'marked_as_duplicate'
      event on a given issue or pull request.
    * `MENTIONED_EVENT`: Represents a 'mentioned' event on a given
      issue or pull request.
    * `MILESTONED_EVENT`: Represents a 'milestoned' event on a given
      issue or pull request.
    * `MOVED_COLUMNS_IN_PROJECT_EVENT`: Represents a
      'moved_columns_in_project' event on a given issue or pull
      request.
    * `PINNED_EVENT`: Represents a 'pinned' event on a given issue or
      pull request.
    * `REFERENCED_EVENT`: Represents a 'referenced' event on a given
      `ReferencedSubject`.
    * `REMOVED_FROM_PROJECT_EVENT`: Represents a
      'removed_from_project' event on a given issue or pull request.
    * `RENAMED_TITLE_EVENT`: Represents a 'renamed' event on a given
      issue or pull request
    * `REOPENED_EVENT`: Represents a 'reopened' event on any
      `Closable`.
    * `SUBSCRIBED_EVENT`: Represents a 'subscribed' event on a given
      `Subscribable`.
    * `TRANSFERRED_EVENT`: Represents a 'transferred' event on a given
      issue or pull request.
    * `UNASSIGNED_EVENT`: Represents an 'unassigned' event on any
      assignable object.
    * `UNLABELED_EVENT`: Represents an 'unlabeled' event on a given
      issue or pull request.
    * `UNLOCKED_EVENT`: Represents an 'unlocked' event on a given
      issue or pull request.
    * `UNMARKED_AS_DUPLICATE_EVENT`: Represents an
      'unmarked_as_duplicate' event on a given issue or pull request.
    * `UNPINNED_EVENT`: Represents an 'unpinned' event on a given
      issue or pull request.
    * `UNSUBSCRIBED_EVENT`: Represents an 'unsubscribed' event on a
      given `Subscribable`.
    * `USER_BLOCKED_EVENT`: Represents a 'user_blocked' event on a
      given user.
    """

    __schema__ = github_schema
    __choices__ = (
        "ADDED_TO_PROJECT_EVENT",
        "ASSIGNED_EVENT",
        "CLOSED_EVENT",
        "COMMENT_DELETED_EVENT",
        "CONNECTED_EVENT",
        "CONVERTED_NOTE_TO_ISSUE_EVENT",
        "CONVERTED_TO_DISCUSSION_EVENT",
        "CROSS_REFERENCED_EVENT",
        "DEMILESTONED_EVENT",
        "DISCONNECTED_EVENT",
        "ISSUE_COMMENT",
        "LABELED_EVENT",
        "LOCKED_EVENT",
        "MARKED_AS_DUPLICATE_EVENT",
        "MENTIONED_EVENT",
        "MILESTONED_EVENT",
        "MOVED_COLUMNS_IN_PROJECT_EVENT",
        "PINNED_EVENT",
        "REFERENCED_EVENT",
        "REMOVED_FROM_PROJECT_EVENT",
        "RENAMED_TITLE_EVENT",
        "REOPENED_EVENT",
        "SUBSCRIBED_EVENT",
        "TRANSFERRED_EVENT",
        "UNASSIGNED_EVENT",
        "UNLABELED_EVENT",
        "UNLOCKED_EVENT",
        "UNMARKED_AS_DUPLICATE_EVENT",
        "UNPINNED_EVENT",
        "UNSUBSCRIBED_EVENT",
        "USER_BLOCKED_EVENT",
    )


class LabelOrderField(sgqlc.types.Enum):
    """Properties by which label connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order labels by creation time
    * `NAME`: Order labels by name
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "NAME")


class LanguageOrderField(sgqlc.types.Enum):
    """Properties by which language connections can be ordered.

    Enumeration Choices:

    * `SIZE`: Order languages by the size of all files containing the
      language
    """

    __schema__ = github_schema
    __choices__ = ("SIZE",)


class LockReason(sgqlc.types.Enum):
    """The possible reasons that an issue or pull request was locked.

    Enumeration Choices:

    * `OFF_TOPIC`: The issue or pull request was locked because the
      conversation was off-topic.
    * `RESOLVED`: The issue or pull request was locked because the
      conversation was resolved.
    * `SPAM`: The issue or pull request was locked because the
      conversation was spam.
    * `TOO_HEATED`: The issue or pull request was locked because the
      conversation was too heated.
    """

    __schema__ = github_schema
    __choices__ = ("OFF_TOPIC", "RESOLVED", "SPAM", "TOO_HEATED")


class MergeStateStatus(sgqlc.types.Enum):
    """Detailed status information about a pull request merge.

    Enumeration Choices:

    * `BEHIND`: The head ref is out of date.
    * `BLOCKED`: The merge is blocked.
    * `CLEAN`: Mergeable and passing commit status.
    * `DIRTY`: The merge commit cannot be cleanly created.
    * `HAS_HOOKS`: Mergeable with passing commit status and pre-
      receive hooks.
    * `UNKNOWN`: The state cannot currently be determined.
    * `UNSTABLE`: Mergeable with non-passing commit status.
    """

    __schema__ = github_schema
    __choices__ = ("BEHIND", "BLOCKED", "CLEAN", "DIRTY", "HAS_HOOKS", "UNKNOWN", "UNSTABLE")


class MergeableState(sgqlc.types.Enum):
    """Whether or not a PullRequest can be merged.

    Enumeration Choices:

    * `CONFLICTING`: The pull request cannot be merged due to merge
      conflicts.
    * `MERGEABLE`: The pull request can be merged.
    * `UNKNOWN`: The mergeability of the pull request is still being
      calculated.
    """

    __schema__ = github_schema
    __choices__ = ("CONFLICTING", "MERGEABLE", "UNKNOWN")


class MigrationSourceType(sgqlc.types.Enum):
    """Represents the different Octoshift migration sources.

    Enumeration Choices:

    * `AZURE_DEVOPS`: An Azure DevOps migration source.
    * `BITBUCKET_SERVER`: A Bitbucket Server migration source.
    * `GITHUB`: A GitHub migration source.
    * `GITHUB_ARCHIVE`: A GitHub Migration API source.
    * `GITLAB`: A GitLab migration source.
    """

    __schema__ = github_schema
    __choices__ = ("AZURE_DEVOPS", "BITBUCKET_SERVER", "GITHUB", "GITHUB_ARCHIVE", "GITLAB")


class MigrationState(sgqlc.types.Enum):
    """The Octoshift migration state.

    Enumeration Choices:

    * `FAILED`: The Octoshift migration has failed.
    * `FAILED_VALIDATION`: The Octoshift migration has invalid
      credentials.
    * `IN_PROGRESS`: The Octoshift migration is in progress.
    * `NOT_STARTED`: The Octoshift migration has not started.
    * `PENDING_VALIDATION`: The Octoshift migration needs to have its
      credentials validated.
    * `QUEUED`: The Octoshift migration has been queued.
    * `SUCCEEDED`: The Octoshift migration has succeeded.
    """

    __schema__ = github_schema
    __choices__ = ("FAILED", "FAILED_VALIDATION", "IN_PROGRESS", "NOT_STARTED", "PENDING_VALIDATION", "QUEUED", "SUCCEEDED")


class MilestoneOrderField(sgqlc.types.Enum):
    """Properties by which milestone connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order milestones by when they were created.
    * `DUE_DATE`: Order milestones by when they are due.
    * `NUMBER`: Order milestones by their number.
    * `UPDATED_AT`: Order milestones by when they were last updated.
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "DUE_DATE", "NUMBER", "UPDATED_AT")


class MilestoneState(sgqlc.types.Enum):
    """The possible states of a milestone.

    Enumeration Choices:

    * `CLOSED`: A milestone that has been closed.
    * `OPEN`: A milestone that is still open.
    """

    __schema__ = github_schema
    __choices__ = ("CLOSED", "OPEN")


class NotificationRestrictionSettingValue(sgqlc.types.Enum):
    """The possible values for the notification restriction setting.

    Enumeration Choices:

    * `DISABLED`: The setting is disabled for the owner.
    * `ENABLED`: The setting is enabled for the owner.
    """

    __schema__ = github_schema
    __choices__ = ("DISABLED", "ENABLED")


class OIDCProviderType(sgqlc.types.Enum):
    """The OIDC identity provider type

    Enumeration Choices:

    * `AAD`: Azure Active Directory
    """

    __schema__ = github_schema
    __choices__ = ("AAD",)


class OauthApplicationCreateAuditEntryState(sgqlc.types.Enum):
    """The state of an OAuth Application when it was created.

    Enumeration Choices:

    * `ACTIVE`: The OAuth Application was active and allowed to have
      OAuth Accesses.
    * `PENDING_DELETION`: The OAuth Application was in the process of
      being deleted.
    * `SUSPENDED`: The OAuth Application was suspended from generating
      OAuth Accesses due to abuse or security concerns.
    """

    __schema__ = github_schema
    __choices__ = ("ACTIVE", "PENDING_DELETION", "SUSPENDED")


class OperationType(sgqlc.types.Enum):
    """The corresponding operation type for the action

    Enumeration Choices:

    * `ACCESS`: An existing resource was accessed
    * `AUTHENTICATION`: A resource performed an authentication event
    * `CREATE`: A new resource was created
    * `MODIFY`: An existing resource was modified
    * `REMOVE`: An existing resource was removed
    * `RESTORE`: An existing resource was restored
    * `TRANSFER`: An existing resource was transferred between
      multiple resources
    """

    __schema__ = github_schema
    __choices__ = ("ACCESS", "AUTHENTICATION", "CREATE", "MODIFY", "REMOVE", "RESTORE", "TRANSFER")


class OrderDirection(sgqlc.types.Enum):
    """Possible directions in which to order a list of items when
    provided an `orderBy` argument.

    Enumeration Choices:

    * `ASC`: Specifies an ascending order for a given `orderBy`
      argument.
    * `DESC`: Specifies a descending order for a given `orderBy`
      argument.
    """

    __schema__ = github_schema
    __choices__ = ("ASC", "DESC")


class OrgAddMemberAuditEntryPermission(sgqlc.types.Enum):
    """The permissions available to members on an Organization.

    Enumeration Choices:

    * `ADMIN`: Can read, clone, push, and add collaborators to
      repositories.
    * `READ`: Can read and clone repositories.
    """

    __schema__ = github_schema
    __choices__ = ("ADMIN", "READ")


class OrgCreateAuditEntryBillingPlan(sgqlc.types.Enum):
    """The billing plans available for organizations.

    Enumeration Choices:

    * `BUSINESS`: Team Plan
    * `BUSINESS_PLUS`: Enterprise Cloud Plan
    * `FREE`: Free Plan
    * `TIERED_PER_SEAT`: Tiered Per Seat Plan
    * `UNLIMITED`: Legacy Unlimited Plan
    """

    __schema__ = github_schema
    __choices__ = ("BUSINESS", "BUSINESS_PLUS", "FREE", "TIERED_PER_SEAT", "UNLIMITED")


class OrgEnterpriseOwnerOrderField(sgqlc.types.Enum):
    """Properties by which enterprise owners can be ordered.

    Enumeration Choices:

    * `LOGIN`: Order enterprise owners by login.
    """

    __schema__ = github_schema
    __choices__ = ("LOGIN",)


class OrgRemoveBillingManagerAuditEntryReason(sgqlc.types.Enum):
    """The reason a billing manager was removed from an Organization.

    Enumeration Choices:

    * `SAML_EXTERNAL_IDENTITY_MISSING`: SAML external identity missing
    * `SAML_SSO_ENFORCEMENT_REQUIRES_EXTERNAL_IDENTITY`: SAML SSO
      enforcement requires an external identity
    * `TWO_FACTOR_REQUIREMENT_NON_COMPLIANCE`: The organization
      required 2FA of its billing managers and this user did not have
      2FA enabled.
    """

    __schema__ = github_schema
    __choices__ = (
        "SAML_EXTERNAL_IDENTITY_MISSING",
        "SAML_SSO_ENFORCEMENT_REQUIRES_EXTERNAL_IDENTITY",
        "TWO_FACTOR_REQUIREMENT_NON_COMPLIANCE",
    )


class OrgRemoveMemberAuditEntryMembershipType(sgqlc.types.Enum):
    """The type of membership a user has with an Organization.

    Enumeration Choices:

    * `ADMIN`: Organization administrators have full access and can
      change several settings, including the names of repositories
      that belong to the Organization and Owners team membership. In
      addition, organization admins can delete the organization and
      all of its repositories.
    * `BILLING_MANAGER`: A billing manager is a user who manages the
      billing settings for the Organization, such as updating payment
      information.
    * `DIRECT_MEMBER`: A direct member is a user that is a member of
      the Organization.
    * `OUTSIDE_COLLABORATOR`: An outside collaborator is a person who
      isn't explicitly a member of the Organization, but who has Read,
      Write, or Admin permissions to one or more repositories in the
      organization.
    * `SUSPENDED`: A suspended member.
    * `UNAFFILIATED`: An unaffiliated collaborator is a person who is
      not a member of the Organization and does not have access to any
      repositories in the Organization.
    """

    __schema__ = github_schema
    __choices__ = ("ADMIN", "BILLING_MANAGER", "DIRECT_MEMBER", "OUTSIDE_COLLABORATOR", "SUSPENDED", "UNAFFILIATED")


class OrgRemoveMemberAuditEntryReason(sgqlc.types.Enum):
    """The reason a member was removed from an Organization.

    Enumeration Choices:

    * `SAML_EXTERNAL_IDENTITY_MISSING`: SAML external identity missing
    * `SAML_SSO_ENFORCEMENT_REQUIRES_EXTERNAL_IDENTITY`: SAML SSO
      enforcement requires an external identity
    * `TWO_FACTOR_ACCOUNT_RECOVERY`: User was removed from
      organization during account recovery
    * `TWO_FACTOR_REQUIREMENT_NON_COMPLIANCE`: The organization
      required 2FA of its billing managers and this user did not have
      2FA enabled.
    * `USER_ACCOUNT_DELETED`: User account has been deleted
    """

    __schema__ = github_schema
    __choices__ = (
        "SAML_EXTERNAL_IDENTITY_MISSING",
        "SAML_SSO_ENFORCEMENT_REQUIRES_EXTERNAL_IDENTITY",
        "TWO_FACTOR_ACCOUNT_RECOVERY",
        "TWO_FACTOR_REQUIREMENT_NON_COMPLIANCE",
        "USER_ACCOUNT_DELETED",
    )


class OrgRemoveOutsideCollaboratorAuditEntryMembershipType(sgqlc.types.Enum):
    """The type of membership a user has with an Organization.

    Enumeration Choices:

    * `BILLING_MANAGER`: A billing manager is a user who manages the
      billing settings for the Organization, such as updating payment
      information.
    * `OUTSIDE_COLLABORATOR`: An outside collaborator is a person who
      isn't explicitly a member of the Organization, but who has Read,
      Write, or Admin permissions to one or more repositories in the
      organization.
    * `UNAFFILIATED`: An unaffiliated collaborator is a person who is
      not a member of the Organization and does not have access to any
      repositories in the organization.
    """

    __schema__ = github_schema
    __choices__ = ("BILLING_MANAGER", "OUTSIDE_COLLABORATOR", "UNAFFILIATED")


class OrgRemoveOutsideCollaboratorAuditEntryReason(sgqlc.types.Enum):
    """The reason an outside collaborator was removed from an
    Organization.

    Enumeration Choices:

    * `SAML_EXTERNAL_IDENTITY_MISSING`: SAML external identity missing
    * `TWO_FACTOR_REQUIREMENT_NON_COMPLIANCE`: The organization
      required 2FA of its billing managers and this user did not have
      2FA enabled.
    """

    __schema__ = github_schema
    __choices__ = ("SAML_EXTERNAL_IDENTITY_MISSING", "TWO_FACTOR_REQUIREMENT_NON_COMPLIANCE")


class OrgUpdateDefaultRepositoryPermissionAuditEntryPermission(sgqlc.types.Enum):
    """The default permission a repository can have in an Organization.

    Enumeration Choices:

    * `ADMIN`: Can read, clone, push, and add collaborators to
      repositories.
    * `NONE`: No default permission value.
    * `READ`: Can read and clone repositories.
    * `WRITE`: Can read, clone and push to repositories.
    """

    __schema__ = github_schema
    __choices__ = ("ADMIN", "NONE", "READ", "WRITE")


class OrgUpdateMemberAuditEntryPermission(sgqlc.types.Enum):
    """The permissions available to members on an Organization.

    Enumeration Choices:

    * `ADMIN`: Can read, clone, push, and add collaborators to
      repositories.
    * `READ`: Can read and clone repositories.
    """

    __schema__ = github_schema
    __choices__ = ("ADMIN", "READ")


class OrgUpdateMemberRepositoryCreationPermissionAuditEntryVisibility(sgqlc.types.Enum):
    """The permissions available for repository creation on an
    Organization.

    Enumeration Choices:

    * `ALL`: All organization members are restricted from creating any
      repositories.
    * `INTERNAL`: All organization members are restricted from
      creating internal repositories.
    * `NONE`: All organization members are allowed to create any
      repositories.
    * `PRIVATE`: All organization members are restricted from creating
      private repositories.
    * `PRIVATE_INTERNAL`: All organization members are restricted from
      creating private or internal repositories.
    * `PUBLIC`: All organization members are restricted from creating
      public repositories.
    * `PUBLIC_INTERNAL`: All organization members are restricted from
      creating public or internal repositories.
    * `PUBLIC_PRIVATE`: All organization members are restricted from
      creating public or private repositories.
    """

    __schema__ = github_schema
    __choices__ = ("ALL", "INTERNAL", "NONE", "PRIVATE", "PRIVATE_INTERNAL", "PUBLIC", "PUBLIC_INTERNAL", "PUBLIC_PRIVATE")


class OrganizationInvitationRole(sgqlc.types.Enum):
    """The possible organization invitation roles.

    Enumeration Choices:

    * `ADMIN`: The user is invited to be an admin of the organization.
    * `BILLING_MANAGER`: The user is invited to be a billing manager
      of the organization.
    * `DIRECT_MEMBER`: The user is invited to be a direct member of
      the organization.
    * `REINSTATE`: The user's previous role will be reinstated.
    """

    __schema__ = github_schema
    __choices__ = ("ADMIN", "BILLING_MANAGER", "DIRECT_MEMBER", "REINSTATE")


class OrganizationInvitationType(sgqlc.types.Enum):
    """The possible organization invitation types.

    Enumeration Choices:

    * `EMAIL`: The invitation was to an email address.
    * `USER`: The invitation was to an existing user.
    """

    __schema__ = github_schema
    __choices__ = ("EMAIL", "USER")


class OrganizationMemberRole(sgqlc.types.Enum):
    """The possible roles within an organization for its members.

    Enumeration Choices:

    * `ADMIN`: The user is an administrator of the organization.
    * `MEMBER`: The user is a member of the organization.
    """

    __schema__ = github_schema
    __choices__ = ("ADMIN", "MEMBER")


class OrganizationMembersCanCreateRepositoriesSettingValue(sgqlc.types.Enum):
    """The possible values for the members can create repositories
    setting on an organization.

    Enumeration Choices:

    * `ALL`: Members will be able to create public and private
      repositories.
    * `DISABLED`: Members will not be able to create public or private
      repositories.
    * `INTERNAL`: Members will be able to create only internal
      repositories.
    * `PRIVATE`: Members will be able to create only private
      repositories.
    """

    __schema__ = github_schema
    __choices__ = ("ALL", "DISABLED", "INTERNAL", "PRIVATE")


class OrganizationOrderField(sgqlc.types.Enum):
    """Properties by which organization connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order organizations by creation time
    * `LOGIN`: Order organizations by login
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "LOGIN")


class PackageFileOrderField(sgqlc.types.Enum):
    """Properties by which package file connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order package files by creation time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class PackageOrderField(sgqlc.types.Enum):
    """Properties by which package connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order packages by creation time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class PackageType(sgqlc.types.Enum):
    """The possible types of a package.

    Enumeration Choices:

    * `DEBIAN`: A debian package.
    * `MAVEN`: A maven package.
    * `NPM`: An npm package.
    * `NUGET`: A nuget package.
    * `PYPI`: A python package.
    * `RUBYGEMS`: A rubygems package.
    """

    __schema__ = github_schema
    __choices__ = ("DEBIAN", "MAVEN", "NPM", "NUGET", "PYPI", "RUBYGEMS")


class PackageVersionOrderField(sgqlc.types.Enum):
    """Properties by which package version connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order package versions by creation time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class PatchStatus(sgqlc.types.Enum):
    """The possible types of patch statuses.

    Enumeration Choices:

    * `ADDED`: The file was added. Git status 'A'.
    * `CHANGED`: The file's type was changed. Git status 'T'.
    * `COPIED`: The file was copied. Git status 'C'.
    * `DELETED`: The file was deleted. Git status 'D'.
    * `MODIFIED`: The file's contents were changed. Git status 'M'.
    * `RENAMED`: The file was renamed. Git status 'R'.
    """

    __schema__ = github_schema
    __choices__ = ("ADDED", "CHANGED", "COPIED", "DELETED", "MODIFIED", "RENAMED")


class PinnableItemType(sgqlc.types.Enum):
    """Represents items that can be pinned to a profile page or
    dashboard.

    Enumeration Choices:

    * `GIST`: A gist.
    * `ISSUE`: An issue.
    * `ORGANIZATION`: An organization.
    * `PROJECT`: A project.
    * `PULL_REQUEST`: A pull request.
    * `REPOSITORY`: A repository.
    * `TEAM`: A team.
    * `USER`: A user.
    """

    __schema__ = github_schema
    __choices__ = ("GIST", "ISSUE", "ORGANIZATION", "PROJECT", "PULL_REQUEST", "REPOSITORY", "TEAM", "USER")


class PinnedDiscussionGradient(sgqlc.types.Enum):
    """Preconfigured gradients that may be used to style discussions
    pinned within a repository.

    Enumeration Choices:

    * `BLUE_MINT`: A gradient of blue to mint
    * `BLUE_PURPLE`: A gradient of blue to purple
    * `PINK_BLUE`: A gradient of pink to blue
    * `PURPLE_CORAL`: A gradient of purple to coral
    * `RED_ORANGE`: A gradient of red to orange
    """

    __schema__ = github_schema
    __choices__ = ("BLUE_MINT", "BLUE_PURPLE", "PINK_BLUE", "PURPLE_CORAL", "RED_ORANGE")


class PinnedDiscussionPattern(sgqlc.types.Enum):
    """Preconfigured background patterns that may be used to style
    discussions pinned within a repository.

    Enumeration Choices:

    * `CHEVRON_UP`: An upward-facing chevron pattern
    * `DOT`: A hollow dot pattern
    * `DOT_FILL`: A solid dot pattern
    * `HEART_FILL`: A heart pattern
    * `PLUS`: A plus sign pattern
    * `ZAP`: A lightning bolt pattern
    """

    __schema__ = github_schema
    __choices__ = ("CHEVRON_UP", "DOT", "DOT_FILL", "HEART_FILL", "PLUS", "ZAP")


class PreciseDateTime(sgqlc.types.Scalar):
    """An ISO-8601 encoded UTC date string with millisecond precision."""

    __schema__ = github_schema


class ProjectCardArchivedState(sgqlc.types.Enum):
    """The possible archived states of a project card.

    Enumeration Choices:

    * `ARCHIVED`: A project card that is archived
    * `NOT_ARCHIVED`: A project card that is not archived
    """

    __schema__ = github_schema
    __choices__ = ("ARCHIVED", "NOT_ARCHIVED")


class ProjectCardState(sgqlc.types.Enum):
    """Various content states of a ProjectCard

    Enumeration Choices:

    * `CONTENT_ONLY`: The card has content only.
    * `NOTE_ONLY`: The card has a note only.
    * `REDACTED`: The card is redacted.
    """

    __schema__ = github_schema
    __choices__ = ("CONTENT_ONLY", "NOTE_ONLY", "REDACTED")


class ProjectColumnPurpose(sgqlc.types.Enum):
    """The semantic purpose of the column - todo, in progress, or done.

    Enumeration Choices:

    * `DONE`: The column contains cards which are complete
    * `IN_PROGRESS`: The column contains cards which are currently
      being worked on
    * `TODO`: The column contains cards still to be worked on
    """

    __schema__ = github_schema
    __choices__ = ("DONE", "IN_PROGRESS", "TODO")


class ProjectItemType(sgqlc.types.Enum):
    """The type of a project item.

    Enumeration Choices:

    * `DRAFT_ISSUE`: Draft Issue
    * `ISSUE`: Issue
    * `PULL_REQUEST`: Pull Request
    * `REDACTED`: Redacted Item
    """

    __schema__ = github_schema
    __choices__ = ("DRAFT_ISSUE", "ISSUE", "PULL_REQUEST", "REDACTED")


class ProjectNextFieldType(sgqlc.types.Enum):
    """The type of a project next field.

    Enumeration Choices:

    * `ASSIGNEES`: Assignees
    * `DATE`: Date
    * `ITERATION`: Iteration
    * `LABELS`: Labels
    * `LINKED_PULL_REQUESTS`: Linked Pull Requests
    * `MILESTONE`: Milestone
    * `NUMBER`: Number
    * `REPOSITORY`: Repository
    * `REVIEWERS`: Reviewers
    * `SINGLE_SELECT`: Single Select
    * `TEXT`: Text
    * `TITLE`: Title
    * `TRACKS`: Tracks
    """

    __schema__ = github_schema
    __choices__ = (
        "ASSIGNEES",
        "DATE",
        "ITERATION",
        "LABELS",
        "LINKED_PULL_REQUESTS",
        "MILESTONE",
        "NUMBER",
        "REPOSITORY",
        "REVIEWERS",
        "SINGLE_SELECT",
        "TEXT",
        "TITLE",
        "TRACKS",
    )


class ProjectNextOrderField(sgqlc.types.Enum):
    """Properties by which the return project can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: The project's date and time of creation
    * `NUMBER`: The project's number
    * `TITLE`: The project's title
    * `UPDATED_AT`: The project's date and time of update
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "NUMBER", "TITLE", "UPDATED_AT")


class ProjectOrderField(sgqlc.types.Enum):
    """Properties by which project connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order projects by creation time
    * `NAME`: Order projects by name
    * `UPDATED_AT`: Order projects by update time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "NAME", "UPDATED_AT")


class ProjectState(sgqlc.types.Enum):
    """State of the project; either 'open' or 'closed'

    Enumeration Choices:

    * `CLOSED`: The project is closed.
    * `OPEN`: The project is open.
    """

    __schema__ = github_schema
    __choices__ = ("CLOSED", "OPEN")


class ProjectTemplate(sgqlc.types.Enum):
    """GitHub-provided templates for Projects

    Enumeration Choices:

    * `AUTOMATED_KANBAN_V2`: Create a board with v2 triggers to
      automatically move cards across To do, In progress and Done
      columns.
    * `AUTOMATED_REVIEWS_KANBAN`: Create a board with triggers to
      automatically move cards across columns with review automation.
    * `BASIC_KANBAN`: Create a board with columns for To do, In
      progress and Done.
    * `BUG_TRIAGE`: Create a board to triage and prioritize bugs with
      To do, priority, and Done columns.
    """

    __schema__ = github_schema
    __choices__ = ("AUTOMATED_KANBAN_V2", "AUTOMATED_REVIEWS_KANBAN", "BASIC_KANBAN", "BUG_TRIAGE")


class ProjectViewLayout(sgqlc.types.Enum):
    """The layout of a project view.

    Enumeration Choices:

    * `BOARD_LAYOUT`: Board layout
    * `TABLE_LAYOUT`: Table layout
    """

    __schema__ = github_schema
    __choices__ = ("BOARD_LAYOUT", "TABLE_LAYOUT")


class PullRequestMergeMethod(sgqlc.types.Enum):
    """Represents available types of methods to use when merging a pull
    request.

    Enumeration Choices:

    * `MERGE`: Add all commits from the head branch to the base branch
      with a merge commit.
    * `REBASE`: Add all commits from the head branch onto the base
      branch individually.
    * `SQUASH`: Combine all commits from the head branch into a single
      commit in the base branch.
    """

    __schema__ = github_schema
    __choices__ = ("MERGE", "REBASE", "SQUASH")


class PullRequestOrderField(sgqlc.types.Enum):
    """Properties by which pull_requests connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order pull_requests by creation time
    * `UPDATED_AT`: Order pull_requests by update time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "UPDATED_AT")


class PullRequestReviewCommentState(sgqlc.types.Enum):
    """The possible states of a pull request review comment.

    Enumeration Choices:

    * `PENDING`: A comment that is part of a pending review
    * `SUBMITTED`: A comment that is part of a submitted review
    """

    __schema__ = github_schema
    __choices__ = ("PENDING", "SUBMITTED")


class PullRequestReviewDecision(sgqlc.types.Enum):
    """The review status of a pull request.

    Enumeration Choices:

    * `APPROVED`: The pull request has received an approving review.
    * `CHANGES_REQUESTED`: Changes have been requested on the pull
      request.
    * `REVIEW_REQUIRED`: A review is required before the pull request
      can be merged.
    """

    __schema__ = github_schema
    __choices__ = ("APPROVED", "CHANGES_REQUESTED", "REVIEW_REQUIRED")


class PullRequestReviewEvent(sgqlc.types.Enum):
    """The possible events to perform on a pull request review.

    Enumeration Choices:

    * `APPROVE`: Submit feedback and approve merging these changes.
    * `COMMENT`: Submit general feedback without explicit approval.
    * `DISMISS`: Dismiss review so it now longer effects merging.
    * `REQUEST_CHANGES`: Submit feedback that must be addressed before
      merging.
    """

    __schema__ = github_schema
    __choices__ = ("APPROVE", "COMMENT", "DISMISS", "REQUEST_CHANGES")


class PullRequestReviewState(sgqlc.types.Enum):
    """The possible states of a pull request review.

    Enumeration Choices:

    * `APPROVED`: A review allowing the pull request to merge.
    * `CHANGES_REQUESTED`: A review blocking the pull request from
      merging.
    * `COMMENTED`: An informational review.
    * `DISMISSED`: A review that has been dismissed.
    * `PENDING`: A review that has not yet been submitted.
    """

    __schema__ = github_schema
    __choices__ = ("APPROVED", "CHANGES_REQUESTED", "COMMENTED", "DISMISSED", "PENDING")


class PullRequestState(sgqlc.types.Enum):
    """The possible states of a pull request.

    Enumeration Choices:

    * `CLOSED`: A pull request that has been closed without being
      merged.
    * `MERGED`: A pull request that has been closed by being merged.
    * `OPEN`: A pull request that is still open.
    """

    __schema__ = github_schema
    __choices__ = ("CLOSED", "MERGED", "OPEN")


class PullRequestTimelineItemsItemType(sgqlc.types.Enum):
    """The possible item types found in a timeline.

    Enumeration Choices:

    * `ADDED_TO_MERGE_QUEUE_EVENT`: Represents an
      'added_to_merge_queue' event on a given pull request.
    * `ADDED_TO_PROJECT_EVENT`: Represents a 'added_to_project' event
      on a given issue or pull request.
    * `ASSIGNED_EVENT`: Represents an 'assigned' event on any
      assignable object.
    * `AUTOMATIC_BASE_CHANGE_FAILED_EVENT`: Represents a
      'automatic_base_change_failed' event on a given pull request.
    * `AUTOMATIC_BASE_CHANGE_SUCCEEDED_EVENT`: Represents a
      'automatic_base_change_succeeded' event on a given pull request.
    * `AUTO_MERGE_DISABLED_EVENT`: Represents a 'auto_merge_disabled'
      event on a given pull request.
    * `AUTO_MERGE_ENABLED_EVENT`: Represents a 'auto_merge_enabled'
      event on a given pull request.
    * `AUTO_REBASE_ENABLED_EVENT`: Represents a 'auto_rebase_enabled'
      event on a given pull request.
    * `AUTO_SQUASH_ENABLED_EVENT`: Represents a 'auto_squash_enabled'
      event on a given pull request.
    * `BASE_REF_CHANGED_EVENT`: Represents a 'base_ref_changed' event
      on a given issue or pull request.
    * `BASE_REF_DELETED_EVENT`: Represents a 'base_ref_deleted' event
      on a given pull request.
    * `BASE_REF_FORCE_PUSHED_EVENT`: Represents a
      'base_ref_force_pushed' event on a given pull request.
    * `CLOSED_EVENT`: Represents a 'closed' event on any `Closable`.
    * `COMMENT_DELETED_EVENT`: Represents a 'comment_deleted' event on
      a given issue or pull request.
    * `CONNECTED_EVENT`: Represents a 'connected' event on a given
      issue or pull request.
    * `CONVERTED_NOTE_TO_ISSUE_EVENT`: Represents a
      'converted_note_to_issue' event on a given issue or pull
      request.
    * `CONVERTED_TO_DISCUSSION_EVENT`: Represents a
      'converted_to_discussion' event on a given issue.
    * `CONVERT_TO_DRAFT_EVENT`: Represents a 'convert_to_draft' event
      on a given pull request.
    * `CROSS_REFERENCED_EVENT`: Represents a mention made by one issue
      or pull request to another.
    * `DEMILESTONED_EVENT`: Represents a 'demilestoned' event on a
      given issue or pull request.
    * `DEPLOYED_EVENT`: Represents a 'deployed' event on a given pull
      request.
    * `DEPLOYMENT_ENVIRONMENT_CHANGED_EVENT`: Represents a
      'deployment_environment_changed' event on a given pull request.
    * `DISCONNECTED_EVENT`: Represents a 'disconnected' event on a
      given issue or pull request.
    * `HEAD_REF_DELETED_EVENT`: Represents a 'head_ref_deleted' event
      on a given pull request.
    * `HEAD_REF_FORCE_PUSHED_EVENT`: Represents a
      'head_ref_force_pushed' event on a given pull request.
    * `HEAD_REF_RESTORED_EVENT`: Represents a 'head_ref_restored'
      event on a given pull request.
    * `ISSUE_COMMENT`: Represents a comment on an Issue.
    * `LABELED_EVENT`: Represents a 'labeled' event on a given issue
      or pull request.
    * `LOCKED_EVENT`: Represents a 'locked' event on a given issue or
      pull request.
    * `MARKED_AS_DUPLICATE_EVENT`: Represents a 'marked_as_duplicate'
      event on a given issue or pull request.
    * `MENTIONED_EVENT`: Represents a 'mentioned' event on a given
      issue or pull request.
    * `MERGED_EVENT`: Represents a 'merged' event on a given pull
      request.
    * `MILESTONED_EVENT`: Represents a 'milestoned' event on a given
      issue or pull request.
    * `MOVED_COLUMNS_IN_PROJECT_EVENT`: Represents a
      'moved_columns_in_project' event on a given issue or pull
      request.
    * `PINNED_EVENT`: Represents a 'pinned' event on a given issue or
      pull request.
    * `PULL_REQUEST_COMMIT`: Represents a Git commit part of a pull
      request.
    * `PULL_REQUEST_COMMIT_COMMENT_THREAD`: Represents a commit
      comment thread part of a pull request.
    * `PULL_REQUEST_REVIEW`: A review object for a given pull request.
    * `PULL_REQUEST_REVIEW_THREAD`: A threaded list of comments for a
      given pull request.
    * `PULL_REQUEST_REVISION_MARKER`: Represents the latest point in
      the pull request timeline for which the viewer has seen the pull
      request's commits.
    * `READY_FOR_REVIEW_EVENT`: Represents a 'ready_for_review' event
      on a given pull request.
    * `REFERENCED_EVENT`: Represents a 'referenced' event on a given
      `ReferencedSubject`.
    * `REMOVED_FROM_MERGE_QUEUE_EVENT`: Represents a
      'removed_from_merge_queue' event on a given pull request.
    * `REMOVED_FROM_PROJECT_EVENT`: Represents a
      'removed_from_project' event on a given issue or pull request.
    * `RENAMED_TITLE_EVENT`: Represents a 'renamed' event on a given
      issue or pull request
    * `REOPENED_EVENT`: Represents a 'reopened' event on any
      `Closable`.
    * `REVIEW_DISMISSED_EVENT`: Represents a 'review_dismissed' event
      on a given issue or pull request.
    * `REVIEW_REQUESTED_EVENT`: Represents an 'review_requested' event
      on a given pull request.
    * `REVIEW_REQUEST_REMOVED_EVENT`: Represents an
      'review_request_removed' event on a given pull request.
    * `SUBSCRIBED_EVENT`: Represents a 'subscribed' event on a given
      `Subscribable`.
    * `TRANSFERRED_EVENT`: Represents a 'transferred' event on a given
      issue or pull request.
    * `UNASSIGNED_EVENT`: Represents an 'unassigned' event on any
      assignable object.
    * `UNLABELED_EVENT`: Represents an 'unlabeled' event on a given
      issue or pull request.
    * `UNLOCKED_EVENT`: Represents an 'unlocked' event on a given
      issue or pull request.
    * `UNMARKED_AS_DUPLICATE_EVENT`: Represents an
      'unmarked_as_duplicate' event on a given issue or pull request.
    * `UNPINNED_EVENT`: Represents an 'unpinned' event on a given
      issue or pull request.
    * `UNSUBSCRIBED_EVENT`: Represents an 'unsubscribed' event on a
      given `Subscribable`.
    * `USER_BLOCKED_EVENT`: Represents a 'user_blocked' event on a
      given user.
    """

    __schema__ = github_schema
    __choices__ = (
        "ADDED_TO_MERGE_QUEUE_EVENT",
        "ADDED_TO_PROJECT_EVENT",
        "ASSIGNED_EVENT",
        "AUTOMATIC_BASE_CHANGE_FAILED_EVENT",
        "AUTOMATIC_BASE_CHANGE_SUCCEEDED_EVENT",
        "AUTO_MERGE_DISABLED_EVENT",
        "AUTO_MERGE_ENABLED_EVENT",
        "AUTO_REBASE_ENABLED_EVENT",
        "AUTO_SQUASH_ENABLED_EVENT",
        "BASE_REF_CHANGED_EVENT",
        "BASE_REF_DELETED_EVENT",
        "BASE_REF_FORCE_PUSHED_EVENT",
        "CLOSED_EVENT",
        "COMMENT_DELETED_EVENT",
        "CONNECTED_EVENT",
        "CONVERTED_NOTE_TO_ISSUE_EVENT",
        "CONVERTED_TO_DISCUSSION_EVENT",
        "CONVERT_TO_DRAFT_EVENT",
        "CROSS_REFERENCED_EVENT",
        "DEMILESTONED_EVENT",
        "DEPLOYED_EVENT",
        "DEPLOYMENT_ENVIRONMENT_CHANGED_EVENT",
        "DISCONNECTED_EVENT",
        "HEAD_REF_DELETED_EVENT",
        "HEAD_REF_FORCE_PUSHED_EVENT",
        "HEAD_REF_RESTORED_EVENT",
        "ISSUE_COMMENT",
        "LABELED_EVENT",
        "LOCKED_EVENT",
        "MARKED_AS_DUPLICATE_EVENT",
        "MENTIONED_EVENT",
        "MERGED_EVENT",
        "MILESTONED_EVENT",
        "MOVED_COLUMNS_IN_PROJECT_EVENT",
        "PINNED_EVENT",
        "PULL_REQUEST_COMMIT",
        "PULL_REQUEST_COMMIT_COMMENT_THREAD",
        "PULL_REQUEST_REVIEW",
        "PULL_REQUEST_REVIEW_THREAD",
        "PULL_REQUEST_REVISION_MARKER",
        "READY_FOR_REVIEW_EVENT",
        "REFERENCED_EVENT",
        "REMOVED_FROM_MERGE_QUEUE_EVENT",
        "REMOVED_FROM_PROJECT_EVENT",
        "RENAMED_TITLE_EVENT",
        "REOPENED_EVENT",
        "REVIEW_DISMISSED_EVENT",
        "REVIEW_REQUESTED_EVENT",
        "REVIEW_REQUEST_REMOVED_EVENT",
        "SUBSCRIBED_EVENT",
        "TRANSFERRED_EVENT",
        "UNASSIGNED_EVENT",
        "UNLABELED_EVENT",
        "UNLOCKED_EVENT",
        "UNMARKED_AS_DUPLICATE_EVENT",
        "UNPINNED_EVENT",
        "UNSUBSCRIBED_EVENT",
        "USER_BLOCKED_EVENT",
    )


class PullRequestUpdateState(sgqlc.types.Enum):
    """The possible target states when updating a pull request.

    Enumeration Choices:

    * `CLOSED`: A pull request that has been closed without being
      merged.
    * `OPEN`: A pull request that is still open.
    """

    __schema__ = github_schema
    __choices__ = ("CLOSED", "OPEN")


class ReactionContent(sgqlc.types.Enum):
    """Emojis that can be attached to Issues, Pull Requests and Comments.

    Enumeration Choices:

    * `CONFUSED`: Represents the `:confused:` emoji.
    * `EYES`: Represents the `:eyes:` emoji.
    * `HEART`: Represents the `:heart:` emoji.
    * `HOORAY`: Represents the `:hooray:` emoji.
    * `LAUGH`: Represents the `:laugh:` emoji.
    * `ROCKET`: Represents the `:rocket:` emoji.
    * `THUMBS_DOWN`: Represents the `:-1:` emoji.
    * `THUMBS_UP`: Represents the `:+1:` emoji.
    """

    __schema__ = github_schema
    __choices__ = ("CONFUSED", "EYES", "HEART", "HOORAY", "LAUGH", "ROCKET", "THUMBS_DOWN", "THUMBS_UP")


class ReactionOrderField(sgqlc.types.Enum):
    """A list of fields that reactions can be ordered by.

    Enumeration Choices:

    * `CREATED_AT`: Allows ordering a list of reactions by when they
      were created.
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class RefOrderField(sgqlc.types.Enum):
    """Properties by which ref connections can be ordered.

    Enumeration Choices:

    * `ALPHABETICAL`: Order refs by their alphanumeric name
    * `TAG_COMMIT_DATE`: Order refs by underlying commit date if the
      ref prefix is refs/tags/
    """

    __schema__ = github_schema
    __choices__ = ("ALPHABETICAL", "TAG_COMMIT_DATE")


class ReleaseOrderField(sgqlc.types.Enum):
    """Properties by which release connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order releases by creation time
    * `NAME`: Order releases alphabetically by name
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "NAME")


class RepoAccessAuditEntryVisibility(sgqlc.types.Enum):
    """The privacy of a repository

    Enumeration Choices:

    * `INTERNAL`: The repository is visible only to users in the same
      business.
    * `PRIVATE`: The repository is visible only to those with explicit
      access.
    * `PUBLIC`: The repository is visible to everyone.
    """

    __schema__ = github_schema
    __choices__ = ("INTERNAL", "PRIVATE", "PUBLIC")


class RepoAddMemberAuditEntryVisibility(sgqlc.types.Enum):
    """The privacy of a repository

    Enumeration Choices:

    * `INTERNAL`: The repository is visible only to users in the same
      business.
    * `PRIVATE`: The repository is visible only to those with explicit
      access.
    * `PUBLIC`: The repository is visible to everyone.
    """

    __schema__ = github_schema
    __choices__ = ("INTERNAL", "PRIVATE", "PUBLIC")


class RepoArchivedAuditEntryVisibility(sgqlc.types.Enum):
    """The privacy of a repository

    Enumeration Choices:

    * `INTERNAL`: The repository is visible only to users in the same
      business.
    * `PRIVATE`: The repository is visible only to those with explicit
      access.
    * `PUBLIC`: The repository is visible to everyone.
    """

    __schema__ = github_schema
    __choices__ = ("INTERNAL", "PRIVATE", "PUBLIC")


class RepoChangeMergeSettingAuditEntryMergeType(sgqlc.types.Enum):
    """The merge options available for pull requests to this repository.

    Enumeration Choices:

    * `MERGE`: The pull request is added to the base branch in a merge
      commit.
    * `REBASE`: Commits from the pull request are added onto the base
      branch individually without a merge commit.
    * `SQUASH`: The pull request's commits are squashed into a single
      commit before they are merged to the base branch.
    """

    __schema__ = github_schema
    __choices__ = ("MERGE", "REBASE", "SQUASH")


class RepoCreateAuditEntryVisibility(sgqlc.types.Enum):
    """The privacy of a repository

    Enumeration Choices:

    * `INTERNAL`: The repository is visible only to users in the same
      business.
    * `PRIVATE`: The repository is visible only to those with explicit
      access.
    * `PUBLIC`: The repository is visible to everyone.
    """

    __schema__ = github_schema
    __choices__ = ("INTERNAL", "PRIVATE", "PUBLIC")


class RepoDestroyAuditEntryVisibility(sgqlc.types.Enum):
    """The privacy of a repository

    Enumeration Choices:

    * `INTERNAL`: The repository is visible only to users in the same
      business.
    * `PRIVATE`: The repository is visible only to those with explicit
      access.
    * `PUBLIC`: The repository is visible to everyone.
    """

    __schema__ = github_schema
    __choices__ = ("INTERNAL", "PRIVATE", "PUBLIC")


class RepoRemoveMemberAuditEntryVisibility(sgqlc.types.Enum):
    """The privacy of a repository

    Enumeration Choices:

    * `INTERNAL`: The repository is visible only to users in the same
      business.
    * `PRIVATE`: The repository is visible only to those with explicit
      access.
    * `PUBLIC`: The repository is visible to everyone.
    """

    __schema__ = github_schema
    __choices__ = ("INTERNAL", "PRIVATE", "PUBLIC")


class ReportedContentClassifiers(sgqlc.types.Enum):
    """The reasons a piece of content can be reported or minimized.

    Enumeration Choices:

    * `ABUSE`: An abusive or harassing piece of content
    * `DUPLICATE`: A duplicated piece of content
    * `OFF_TOPIC`: An irrelevant piece of content
    * `OUTDATED`: An outdated piece of content
    * `RESOLVED`: The content has been resolved
    * `SPAM`: A spammy piece of content
    """

    __schema__ = github_schema
    __choices__ = ("ABUSE", "DUPLICATE", "OFF_TOPIC", "OUTDATED", "RESOLVED", "SPAM")


class RepositoryAffiliation(sgqlc.types.Enum):
    """The affiliation of a user to a repository

    Enumeration Choices:

    * `COLLABORATOR`: Repositories that the user has been added to as
      a collaborator.
    * `ORGANIZATION_MEMBER`: Repositories that the user has access to
      through being a member of an organization. This includes every
      repository on every team that the user is on.
    * `OWNER`: Repositories that are owned by the authenticated user.
    """

    __schema__ = github_schema
    __choices__ = ("COLLABORATOR", "ORGANIZATION_MEMBER", "OWNER")


class RepositoryContributionType(sgqlc.types.Enum):
    """The reason a repository is listed as 'contributed'.

    Enumeration Choices:

    * `COMMIT`: Created a commit
    * `ISSUE`: Created an issue
    * `PULL_REQUEST`: Created a pull request
    * `PULL_REQUEST_REVIEW`: Reviewed a pull request
    * `REPOSITORY`: Created the repository
    """

    __schema__ = github_schema
    __choices__ = ("COMMIT", "ISSUE", "PULL_REQUEST", "PULL_REQUEST_REVIEW", "REPOSITORY")


class RepositoryInteractionLimit(sgqlc.types.Enum):
    """A repository interaction limit.

    Enumeration Choices:

    * `COLLABORATORS_ONLY`: Users that are not collaborators will not
      be able to interact with the repository.
    * `CONTRIBUTORS_ONLY`: Users that have not previously committed to
      a repository’s default branch will be unable to interact with
      the repository.
    * `EXISTING_USERS`: Users that have recently created their account
      will be unable to interact with the repository.
    * `NO_LIMIT`: No interaction limits are enabled.
    """

    __schema__ = github_schema
    __choices__ = ("COLLABORATORS_ONLY", "CONTRIBUTORS_ONLY", "EXISTING_USERS", "NO_LIMIT")


class RepositoryInteractionLimitExpiry(sgqlc.types.Enum):
    """The length for a repository interaction limit to be enabled for.

    Enumeration Choices:

    * `ONE_DAY`: The interaction limit will expire after 1 day.
    * `ONE_MONTH`: The interaction limit will expire after 1 month.
    * `ONE_WEEK`: The interaction limit will expire after 1 week.
    * `SIX_MONTHS`: The interaction limit will expire after 6 months.
    * `THREE_DAYS`: The interaction limit will expire after 3 days.
    """

    __schema__ = github_schema
    __choices__ = ("ONE_DAY", "ONE_MONTH", "ONE_WEEK", "SIX_MONTHS", "THREE_DAYS")


class RepositoryInteractionLimitOrigin(sgqlc.types.Enum):
    """Indicates where an interaction limit is configured.

    Enumeration Choices:

    * `ORGANIZATION`: A limit that is configured at the organization
      level.
    * `REPOSITORY`: A limit that is configured at the repository
      level.
    * `USER`: A limit that is configured at the user-wide level.
    """

    __schema__ = github_schema
    __choices__ = ("ORGANIZATION", "REPOSITORY", "USER")


class RepositoryInvitationOrderField(sgqlc.types.Enum):
    """Properties by which repository invitation connections can be
    ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order repository invitations by creation time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class RepositoryLockReason(sgqlc.types.Enum):
    """The possible reasons a given repository could be in a locked
    state.

    Enumeration Choices:

    * `BILLING`: The repository is locked due to a billing related
      reason.
    * `MIGRATING`: The repository is locked due to a migration.
    * `MOVING`: The repository is locked due to a move.
    * `RENAME`: The repository is locked due to a rename.
    """

    __schema__ = github_schema
    __choices__ = ("BILLING", "MIGRATING", "MOVING", "RENAME")


class RepositoryMigrationOrderDirection(sgqlc.types.Enum):
    """Possible directions in which to order a list of repository
    migrations when provided an `orderBy` argument.

    Enumeration Choices:

    * `ASC`: Specifies an ascending order for a given `orderBy`
      argument.
    * `DESC`: Specifies a descending order for a given `orderBy`
      argument.
    """

    __schema__ = github_schema
    __choices__ = ("ASC", "DESC")


class RepositoryMigrationOrderField(sgqlc.types.Enum):
    """Properties by which repository migrations can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order mannequins why when they were created.
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class RepositoryOrderField(sgqlc.types.Enum):
    """Properties by which repository connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order repositories by creation time
    * `NAME`: Order repositories by name
    * `PUSHED_AT`: Order repositories by push time
    * `STARGAZERS`: Order repositories by number of stargazers
    * `UPDATED_AT`: Order repositories by update time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "NAME", "PUSHED_AT", "STARGAZERS", "UPDATED_AT")


class RepositoryPermission(sgqlc.types.Enum):
    """The access level to a repository

    Enumeration Choices:

    * `ADMIN`: Can read, clone, and push to this repository. Can also
      manage issues, pull requests, and repository settings, including
      adding collaborators
    * `MAINTAIN`: Can read, clone, and push to this repository. They
      can also manage issues, pull requests, and some repository
      settings
    * `READ`: Can read and clone this repository. Can also open and
      comment on issues and pull requests
    * `TRIAGE`: Can read and clone this repository. Can also manage
      issues and pull requests
    * `WRITE`: Can read, clone, and push to this repository. Can also
      manage issues and pull requests
    """

    __schema__ = github_schema
    __choices__ = ("ADMIN", "MAINTAIN", "READ", "TRIAGE", "WRITE")


class RepositoryPrivacy(sgqlc.types.Enum):
    """The privacy of a repository

    Enumeration Choices:

    * `PRIVATE`: Private
    * `PUBLIC`: Public
    """

    __schema__ = github_schema
    __choices__ = ("PRIVATE", "PUBLIC")


class RepositoryVisibility(sgqlc.types.Enum):
    """The repository's visibility level.

    Enumeration Choices:

    * `INTERNAL`: The repository is visible only to users in the same
      business.
    * `PRIVATE`: The repository is visible only to those with explicit
      access.
    * `PUBLIC`: The repository is visible to everyone.
    """

    __schema__ = github_schema
    __choices__ = ("INTERNAL", "PRIVATE", "PUBLIC")


class RepositoryVulnerabilityAlertState(sgqlc.types.Enum):
    """The possible states of an alert

    Enumeration Choices:

    * `DISMISSED`: An alert that has been manually closed by a user.
    * `FIXED`: An alert that has been resolved by a code change.
    * `OPEN`: An alert that is still open.
    """

    __schema__ = github_schema
    __choices__ = ("DISMISSED", "FIXED", "OPEN")


class RequestableCheckStatusState(sgqlc.types.Enum):
    """The possible states that can be requested when creating a check
    run.

    Enumeration Choices:

    * `COMPLETED`: The check suite or run has been completed.
    * `IN_PROGRESS`: The check suite or run is in progress.
    * `PENDING`: The check suite or run is in pending state.
    * `QUEUED`: The check suite or run has been queued.
    * `WAITING`: The check suite or run is in waiting state.
    """

    __schema__ = github_schema
    __choices__ = ("COMPLETED", "IN_PROGRESS", "PENDING", "QUEUED", "WAITING")


class RoleInOrganization(sgqlc.types.Enum):
    """Possible roles a user may have in relation to an organization.

    Enumeration Choices:

    * `DIRECT_MEMBER`: A user who is a direct member of the
      organization.
    * `OWNER`: A user with full administrative access to the
      organization.
    * `UNAFFILIATED`: A user who is unaffiliated with the
      organization.
    """

    __schema__ = github_schema
    __choices__ = ("DIRECT_MEMBER", "OWNER", "UNAFFILIATED")


class SamlDigestAlgorithm(sgqlc.types.Enum):
    """The possible digest algorithms used to sign SAML requests for an
    identity provider.

    Enumeration Choices:

    * `SHA1`: SHA1
    * `SHA256`: SHA256
    * `SHA384`: SHA384
    * `SHA512`: SHA512
    """

    __schema__ = github_schema
    __choices__ = ("SHA1", "SHA256", "SHA384", "SHA512")


class SamlSignatureAlgorithm(sgqlc.types.Enum):
    """The possible signature algorithms used to sign SAML requests for a
    Identity Provider.

    Enumeration Choices:

    * `RSA_SHA1`: RSA-SHA1
    * `RSA_SHA256`: RSA-SHA256
    * `RSA_SHA384`: RSA-SHA384
    * `RSA_SHA512`: RSA-SHA512
    """

    __schema__ = github_schema
    __choices__ = ("RSA_SHA1", "RSA_SHA256", "RSA_SHA384", "RSA_SHA512")


class SavedReplyOrderField(sgqlc.types.Enum):
    """Properties by which saved reply connections can be ordered.

    Enumeration Choices:

    * `UPDATED_AT`: Order saved reply by when they were updated.
    """

    __schema__ = github_schema
    __choices__ = ("UPDATED_AT",)


class SearchType(sgqlc.types.Enum):
    """Represents the individual results of a search.

    Enumeration Choices:

    * `DISCUSSION`: Returns matching discussions in repositories.
    * `ISSUE`: Returns results matching issues in repositories.
    * `REPOSITORY`: Returns results matching repositories.
    * `USER`: Returns results matching users and organizations on
      GitHub.
    """

    __schema__ = github_schema
    __choices__ = ("DISCUSSION", "ISSUE", "REPOSITORY", "USER")


class SecurityAdvisoryClassification(sgqlc.types.Enum):
    """Classification of the advisory.

    Enumeration Choices:

    * `GENERAL`: Classification of general advisories.
    * `MALWARE`: Classification of malware advisories.
    """

    __schema__ = github_schema
    __choices__ = ("GENERAL", "MALWARE")


class SecurityAdvisoryEcosystem(sgqlc.types.Enum):
    """The possible ecosystems of a security vulnerability's package.

    Enumeration Choices:

    * `COMPOSER`: PHP packages hosted at packagist.org
    * `GO`: Go modules
    * `MAVEN`: Java artifacts hosted at the Maven central repository
    * `NPM`: JavaScript packages hosted at npmjs.com
    * `NUGET`: .NET packages hosted at the NuGet Gallery
    * `PIP`: Python packages hosted at PyPI.org
    * `RUBYGEMS`: Ruby gems hosted at RubyGems.org
    * `RUST`: Rust crates
    """

    __schema__ = github_schema
    __choices__ = ("COMPOSER", "GO", "MAVEN", "NPM", "NUGET", "PIP", "RUBYGEMS", "RUST")


class SecurityAdvisoryIdentifierType(sgqlc.types.Enum):
    """Identifier formats available for advisories.

    Enumeration Choices:

    * `CVE`: Common Vulnerabilities and Exposures Identifier.
    * `GHSA`: GitHub Security Advisory ID.
    """

    __schema__ = github_schema
    __choices__ = ("CVE", "GHSA")


class SecurityAdvisoryOrderField(sgqlc.types.Enum):
    """Properties by which security advisory connections can be ordered.

    Enumeration Choices:

    * `PUBLISHED_AT`: Order advisories by publication time
    * `UPDATED_AT`: Order advisories by update time
    """

    __schema__ = github_schema
    __choices__ = ("PUBLISHED_AT", "UPDATED_AT")


class SecurityAdvisorySeverity(sgqlc.types.Enum):
    """Severity of the vulnerability.

    Enumeration Choices:

    * `CRITICAL`: Critical.
    * `HIGH`: High.
    * `LOW`: Low.
    * `MODERATE`: Moderate.
    """

    __schema__ = github_schema
    __choices__ = ("CRITICAL", "HIGH", "LOW", "MODERATE")


class SecurityVulnerabilityOrderField(sgqlc.types.Enum):
    """Properties by which security vulnerability connections can be
    ordered.

    Enumeration Choices:

    * `UPDATED_AT`: Order vulnerability by update time
    """

    __schema__ = github_schema
    __choices__ = ("UPDATED_AT",)


class SponsorOrderField(sgqlc.types.Enum):
    """Properties by which sponsor connections can be ordered.

    Enumeration Choices:

    * `LOGIN`: Order sponsorable entities by login (username).
    * `RELEVANCE`: Order sponsors by their relevance to the viewer.
    """

    __schema__ = github_schema
    __choices__ = ("LOGIN", "RELEVANCE")


class SponsorableOrderField(sgqlc.types.Enum):
    """Properties by which sponsorable connections can be ordered.

    Enumeration Choices:

    * `LOGIN`: Order sponsorable entities by login (username).
    """

    __schema__ = github_schema
    __choices__ = ("LOGIN",)


class SponsorsActivityAction(sgqlc.types.Enum):
    """The possible actions that GitHub Sponsors activities can
    represent.

    Enumeration Choices:

    * `CANCELLED_SPONSORSHIP`: The activity was cancelling a
      sponsorship.
    * `NEW_SPONSORSHIP`: The activity was starting a sponsorship.
    * `PENDING_CHANGE`: The activity was scheduling a downgrade or
      cancellation.
    * `REFUND`: The activity was funds being refunded to the sponsor
      or GitHub.
    * `SPONSOR_MATCH_DISABLED`: The activity was disabling matching
      for a previously matched sponsorship.
    * `TIER_CHANGE`: The activity was changing the sponsorship tier,
      either directly by the sponsor or by a scheduled/pending change.
    """

    __schema__ = github_schema
    __choices__ = ("CANCELLED_SPONSORSHIP", "NEW_SPONSORSHIP", "PENDING_CHANGE", "REFUND", "SPONSOR_MATCH_DISABLED", "TIER_CHANGE")


class SponsorsActivityOrderField(sgqlc.types.Enum):
    """Properties by which GitHub Sponsors activity connections can be
    ordered.

    Enumeration Choices:

    * `TIMESTAMP`: Order activities by when they happened.
    """

    __schema__ = github_schema
    __choices__ = ("TIMESTAMP",)


class SponsorsActivityPeriod(sgqlc.types.Enum):
    """The possible time periods for which Sponsors activities can be
    requested.

    Enumeration Choices:

    * `ALL`: Don't restrict the activity to any date range, include
      all activity.
    * `DAY`: The previous calendar day.
    * `MONTH`: The previous thirty days.
    * `WEEK`: The previous seven days.
    """

    __schema__ = github_schema
    __choices__ = ("ALL", "DAY", "MONTH", "WEEK")


class SponsorsGoalKind(sgqlc.types.Enum):
    """The different kinds of goals a GitHub Sponsors member can have.

    Enumeration Choices:

    * `MONTHLY_SPONSORSHIP_AMOUNT`: The goal is about getting a
      certain amount in USD from sponsorships each month.
    * `TOTAL_SPONSORS_COUNT`: The goal is about reaching a certain
      number of sponsors.
    """

    __schema__ = github_schema
    __choices__ = ("MONTHLY_SPONSORSHIP_AMOUNT", "TOTAL_SPONSORS_COUNT")


class SponsorsTierOrderField(sgqlc.types.Enum):
    """Properties by which Sponsors tiers connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order tiers by creation time.
    * `MONTHLY_PRICE_IN_CENTS`: Order tiers by their monthly price in
      cents
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "MONTHLY_PRICE_IN_CENTS")


class SponsorshipNewsletterOrderField(sgqlc.types.Enum):
    """Properties by which sponsorship update connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order sponsorship newsletters by when they were
      created.
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class SponsorshipOrderField(sgqlc.types.Enum):
    """Properties by which sponsorship connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order sponsorship by creation time.
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class SponsorshipPrivacy(sgqlc.types.Enum):
    """The privacy of a sponsorship

    Enumeration Choices:

    * `PRIVATE`: Private
    * `PUBLIC`: Public
    """

    __schema__ = github_schema
    __choices__ = ("PRIVATE", "PUBLIC")


class StarOrderField(sgqlc.types.Enum):
    """Properties by which star connections can be ordered.

    Enumeration Choices:

    * `STARRED_AT`: Allows ordering a list of stars by when they were
      created.
    """

    __schema__ = github_schema
    __choices__ = ("STARRED_AT",)


class StatusState(sgqlc.types.Enum):
    """The possible commit status states.

    Enumeration Choices:

    * `ERROR`: Status is errored.
    * `EXPECTED`: Status is expected.
    * `FAILURE`: Status is failing.
    * `PENDING`: Status is pending.
    * `SUCCESS`: Status is successful.
    """

    __schema__ = github_schema
    __choices__ = ("ERROR", "EXPECTED", "FAILURE", "PENDING", "SUCCESS")


String = sgqlc.types.String


class SubscriptionState(sgqlc.types.Enum):
    """The possible states of a subscription.

    Enumeration Choices:

    * `IGNORED`: The User is never notified.
    * `SUBSCRIBED`: The User is notified of all conversations.
    * `UNSUBSCRIBED`: The User is only notified when participating or
      @mentioned.
    """

    __schema__ = github_schema
    __choices__ = ("IGNORED", "SUBSCRIBED", "UNSUBSCRIBED")


class TeamDiscussionCommentOrderField(sgqlc.types.Enum):
    """Properties by which team discussion comment connections can be
    ordered.

    Enumeration Choices:

    * `NUMBER`: Allows sequential ordering of team discussion comments
      (which is equivalent to chronological ordering).
    """

    __schema__ = github_schema
    __choices__ = ("NUMBER",)


class TeamDiscussionOrderField(sgqlc.types.Enum):
    """Properties by which team discussion connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Allows chronological ordering of team discussions.
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT",)


class TeamMemberOrderField(sgqlc.types.Enum):
    """Properties by which team member connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order team members by creation time
    * `LOGIN`: Order team members by login
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "LOGIN")


class TeamMemberRole(sgqlc.types.Enum):
    """The possible team member roles; either 'maintainer' or 'member'.

    Enumeration Choices:

    * `MAINTAINER`: A team maintainer has permission to add and remove
      team members.
    * `MEMBER`: A team member has no administrative permissions on the
      team.
    """

    __schema__ = github_schema
    __choices__ = ("MAINTAINER", "MEMBER")


class TeamMembershipType(sgqlc.types.Enum):
    """Defines which types of team members are included in the returned
    list. Can be one of IMMEDIATE, CHILD_TEAM or ALL.

    Enumeration Choices:

    * `ALL`: Includes immediate and child team members for the team.
    * `CHILD_TEAM`: Includes only child team members for the team.
    * `IMMEDIATE`: Includes only immediate members of the team.
    """

    __schema__ = github_schema
    __choices__ = ("ALL", "CHILD_TEAM", "IMMEDIATE")


class TeamOrderField(sgqlc.types.Enum):
    """Properties by which team connections can be ordered.

    Enumeration Choices:

    * `NAME`: Allows ordering a list of teams by name.
    """

    __schema__ = github_schema
    __choices__ = ("NAME",)


class TeamPrivacy(sgqlc.types.Enum):
    """The possible team privacy values.

    Enumeration Choices:

    * `SECRET`: A secret team can only be seen by its members.
    * `VISIBLE`: A visible team can be seen and @mentioned by every
      member of the organization.
    """

    __schema__ = github_schema
    __choices__ = ("SECRET", "VISIBLE")


class TeamRepositoryOrderField(sgqlc.types.Enum):
    """Properties by which team repository connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order repositories by creation time
    * `NAME`: Order repositories by name
    * `PERMISSION`: Order repositories by permission
    * `PUSHED_AT`: Order repositories by push time
    * `STARGAZERS`: Order repositories by number of stargazers
    * `UPDATED_AT`: Order repositories by update time
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "NAME", "PERMISSION", "PUSHED_AT", "STARGAZERS", "UPDATED_AT")


class TeamRole(sgqlc.types.Enum):
    """The role of a user on a team.

    Enumeration Choices:

    * `ADMIN`: User has admin rights on the team.
    * `MEMBER`: User is a member of the team.
    """

    __schema__ = github_schema
    __choices__ = ("ADMIN", "MEMBER")


class TopicSuggestionDeclineReason(sgqlc.types.Enum):
    """Reason that the suggested topic is declined.

    Enumeration Choices:

    * `NOT_RELEVANT`: The suggested topic is not relevant to the
      repository.
    * `PERSONAL_PREFERENCE`: The viewer does not like the suggested
      topic.
    * `TOO_GENERAL`: The suggested topic is too general for the
      repository.
    * `TOO_SPECIFIC`: The suggested topic is too specific for the
      repository (e.g. #ruby-on-rails-version-4-2-1).
    """

    __schema__ = github_schema
    __choices__ = ("NOT_RELEVANT", "PERSONAL_PREFERENCE", "TOO_GENERAL", "TOO_SPECIFIC")


class TrackedIssueStates(sgqlc.types.Enum):
    """The possible states of a tracked issue.

    Enumeration Choices:

    * `CLOSED`: The tracked issue is closed
    * `OPEN`: The tracked issue is open
    """

    __schema__ = github_schema
    __choices__ = ("CLOSED", "OPEN")


class URI(sgqlc.types.Scalar):
    """An RFC 3986, RFC 3987, and RFC 6570 (level 4) compliant URI
    string.
    """

    __schema__ = github_schema


class UserBlockDuration(sgqlc.types.Enum):
    """The possible durations that a user can be blocked for.

    Enumeration Choices:

    * `ONE_DAY`: The user was blocked for 1 day
    * `ONE_MONTH`: The user was blocked for 30 days
    * `ONE_WEEK`: The user was blocked for 7 days
    * `PERMANENT`: The user was blocked permanently
    * `THREE_DAYS`: The user was blocked for 3 days
    """

    __schema__ = github_schema
    __choices__ = ("ONE_DAY", "ONE_MONTH", "ONE_WEEK", "PERMANENT", "THREE_DAYS")


class UserStatusOrderField(sgqlc.types.Enum):
    """Properties by which user status connections can be ordered.

    Enumeration Choices:

    * `UPDATED_AT`: Order user statuses by when they were updated.
    """

    __schema__ = github_schema
    __choices__ = ("UPDATED_AT",)


class VerifiableDomainOrderField(sgqlc.types.Enum):
    """Properties by which verifiable domain connections can be ordered.

    Enumeration Choices:

    * `CREATED_AT`: Order verifiable domains by their creation date.
    * `DOMAIN`: Order verifiable domains by the domain name.
    """

    __schema__ = github_schema
    __choices__ = ("CREATED_AT", "DOMAIN")


class X509Certificate(sgqlc.types.Scalar):
    """A valid x509 certificate string"""

    __schema__ = github_schema


########################################################################
# Input Objects
########################################################################
class AbortQueuedMigrationsInput(sgqlc.types.Input):
    """Autogenerated input type of AbortQueuedMigrations"""

    __schema__ = github_schema
    __field_names__ = ("owner_id", "client_mutation_id")
    owner_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="ownerId")
    """The ID of the organization that is running the migrations."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AcceptEnterpriseAdministratorInvitationInput(sgqlc.types.Input):
    """Autogenerated input type of
    AcceptEnterpriseAdministratorInvitation
    """

    __schema__ = github_schema
    __field_names__ = ("invitation_id", "client_mutation_id")
    invitation_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="invitationId")
    """The id of the invitation being accepted"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AcceptTopicSuggestionInput(sgqlc.types.Input):
    """Autogenerated input type of AcceptTopicSuggestion"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "name", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the repository."""

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The name of the suggested topic."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddAssigneesToAssignableInput(sgqlc.types.Input):
    """Autogenerated input type of AddAssigneesToAssignable"""

    __schema__ = github_schema
    __field_names__ = ("assignable_id", "assignee_ids", "client_mutation_id")
    assignable_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="assignableId")
    """The id of the assignable object to add assignees to."""

    assignee_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name="assigneeIds")
    """The id of users to add as assignees."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddCommentInput(sgqlc.types.Input):
    """Autogenerated input type of AddComment"""

    __schema__ = github_schema
    __field_names__ = ("subject_id", "body", "client_mutation_id")
    subject_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="subjectId")
    """The Node ID of the subject to modify."""

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="body")
    """The contents of the comment."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddDiscussionCommentInput(sgqlc.types.Input):
    """Autogenerated input type of AddDiscussionComment"""

    __schema__ = github_schema
    __field_names__ = ("discussion_id", "reply_to_id", "body", "client_mutation_id")
    discussion_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="discussionId")
    """The Node ID of the discussion to comment on."""

    reply_to_id = sgqlc.types.Field(ID, graphql_name="replyToId")
    """The Node ID of the discussion comment within this discussion to
    reply to.
    """

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="body")
    """The contents of the comment."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddDiscussionPollVoteInput(sgqlc.types.Input):
    """Autogenerated input type of AddDiscussionPollVote"""

    __schema__ = github_schema
    __field_names__ = ("poll_option_id", "client_mutation_id")
    poll_option_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pollOptionId")
    """The Node ID of the discussion poll option to vote for."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddEnterpriseSupportEntitlementInput(sgqlc.types.Input):
    """Autogenerated input type of AddEnterpriseSupportEntitlement"""

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "login", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the Enterprise which the admin belongs to."""

    login = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="login")
    """The login of a member who will receive the support entitlement."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddLabelsToLabelableInput(sgqlc.types.Input):
    """Autogenerated input type of AddLabelsToLabelable"""

    __schema__ = github_schema
    __field_names__ = ("labelable_id", "label_ids", "client_mutation_id")
    labelable_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="labelableId")
    """The id of the labelable object to add labels to."""

    label_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name="labelIds")
    """The ids of the labels to add."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddProjectCardInput(sgqlc.types.Input):
    """Autogenerated input type of AddProjectCard"""

    __schema__ = github_schema
    __field_names__ = ("project_column_id", "content_id", "note", "client_mutation_id")
    project_column_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="projectColumnId")
    """The Node ID of the ProjectColumn."""

    content_id = sgqlc.types.Field(ID, graphql_name="contentId")
    """The content of the card. Must be a member of the ProjectCardItem
    union
    """

    note = sgqlc.types.Field(String, graphql_name="note")
    """The note on the card."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddProjectColumnInput(sgqlc.types.Input):
    """Autogenerated input type of AddProjectColumn"""

    __schema__ = github_schema
    __field_names__ = ("project_id", "name", "client_mutation_id")
    project_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="projectId")
    """The Node ID of the project."""

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The name of the column."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddProjectDraftIssueInput(sgqlc.types.Input):
    """Autogenerated input type of AddProjectDraftIssue"""

    __schema__ = github_schema
    __field_names__ = ("project_id", "title", "body", "assignee_ids", "client_mutation_id")
    project_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="projectId")
    """The ID of the Project to add the draft issue to."""

    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
    """The title of the draft issue."""

    body = sgqlc.types.Field(String, graphql_name="body")
    """The body of the draft issue."""

    assignee_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="assigneeIds")
    """The IDs of the assignees of the draft issue."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddProjectNextItemInput(sgqlc.types.Input):
    """Autogenerated input type of AddProjectNextItem"""

    __schema__ = github_schema
    __field_names__ = ("project_id", "content_id", "client_mutation_id")
    project_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="projectId")
    """The ID of the Project to add the item to."""

    content_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="contentId")
    """The content id of the item (Issue or PullRequest)."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddPullRequestReviewCommentInput(sgqlc.types.Input):
    """Autogenerated input type of AddPullRequestReviewComment"""

    __schema__ = github_schema
    __field_names__ = (
        "pull_request_id",
        "pull_request_review_id",
        "commit_oid",
        "body",
        "path",
        "position",
        "in_reply_to",
        "client_mutation_id",
    )
    pull_request_id = sgqlc.types.Field(ID, graphql_name="pullRequestId")
    """The node ID of the pull request reviewing"""

    pull_request_review_id = sgqlc.types.Field(ID, graphql_name="pullRequestReviewId")
    """The Node ID of the review to modify."""

    commit_oid = sgqlc.types.Field(GitObjectID, graphql_name="commitOID")
    """The SHA of the commit to comment on."""

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="body")
    """The text of the comment."""

    path = sgqlc.types.Field(String, graphql_name="path")
    """The relative path of the file to comment on."""

    position = sgqlc.types.Field(Int, graphql_name="position")
    """The line index in the diff to comment on."""

    in_reply_to = sgqlc.types.Field(ID, graphql_name="inReplyTo")
    """The comment id to reply to."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddPullRequestReviewInput(sgqlc.types.Input):
    """Autogenerated input type of AddPullRequestReview"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "commit_oid", "body", "event", "comments", "threads", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """The Node ID of the pull request to modify."""

    commit_oid = sgqlc.types.Field(GitObjectID, graphql_name="commitOID")
    """The commit OID the review pertains to."""

    body = sgqlc.types.Field(String, graphql_name="body")
    """The contents of the review body comment."""

    event = sgqlc.types.Field(PullRequestReviewEvent, graphql_name="event")
    """The event to perform on the pull request review."""

    comments = sgqlc.types.Field(sgqlc.types.list_of("DraftPullRequestReviewComment"), graphql_name="comments")
    """The review line comments."""

    threads = sgqlc.types.Field(sgqlc.types.list_of("DraftPullRequestReviewThread"), graphql_name="threads")
    """The review line comment threads."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddPullRequestReviewThreadInput(sgqlc.types.Input):
    """Autogenerated input type of AddPullRequestReviewThread"""

    __schema__ = github_schema
    __field_names__ = (
        "path",
        "body",
        "pull_request_id",
        "pull_request_review_id",
        "line",
        "side",
        "start_line",
        "start_side",
        "client_mutation_id",
    )
    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="path")
    """Path to the file being commented on."""

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="body")
    """Body of the thread's first comment."""

    pull_request_id = sgqlc.types.Field(ID, graphql_name="pullRequestId")
    """The node ID of the pull request reviewing"""

    pull_request_review_id = sgqlc.types.Field(ID, graphql_name="pullRequestReviewId")
    """The Node ID of the review to modify."""

    line = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="line")
    """The line of the blob to which the thread refers. The end of the
    line range for multi-line comments.
    """

    side = sgqlc.types.Field(DiffSide, graphql_name="side")
    """The side of the diff on which the line resides. For multi-line
    comments, this is the side for the end of the line range.
    """

    start_line = sgqlc.types.Field(Int, graphql_name="startLine")
    """The first line of the range to which the comment refers."""

    start_side = sgqlc.types.Field(DiffSide, graphql_name="startSide")
    """The side of the diff on which the start line resides."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddReactionInput(sgqlc.types.Input):
    """Autogenerated input type of AddReaction"""

    __schema__ = github_schema
    __field_names__ = ("subject_id", "content", "client_mutation_id")
    subject_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="subjectId")
    """The Node ID of the subject to modify."""

    content = sgqlc.types.Field(sgqlc.types.non_null(ReactionContent), graphql_name="content")
    """The name of the emoji to react with."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddStarInput(sgqlc.types.Input):
    """Autogenerated input type of AddStar"""

    __schema__ = github_schema
    __field_names__ = ("starrable_id", "client_mutation_id")
    starrable_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="starrableId")
    """The Starrable ID to star."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddUpvoteInput(sgqlc.types.Input):
    """Autogenerated input type of AddUpvote"""

    __schema__ = github_schema
    __field_names__ = ("subject_id", "client_mutation_id")
    subject_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="subjectId")
    """The Node ID of the discussion or comment to upvote."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AddVerifiableDomainInput(sgqlc.types.Input):
    """Autogenerated input type of AddVerifiableDomain"""

    __schema__ = github_schema
    __field_names__ = ("owner_id", "domain", "client_mutation_id")
    owner_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="ownerId")
    """The ID of the owner to add the domain to"""

    domain = sgqlc.types.Field(sgqlc.types.non_null(URI), graphql_name="domain")
    """The URL of the domain"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ApproveDeploymentsInput(sgqlc.types.Input):
    """Autogenerated input type of ApproveDeployments"""

    __schema__ = github_schema
    __field_names__ = ("workflow_run_id", "environment_ids", "comment", "client_mutation_id")
    workflow_run_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="workflowRunId")
    """The node ID of the workflow run containing the pending
    deployments.
    """

    environment_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name="environmentIds")
    """The ids of environments to reject deployments"""

    comment = sgqlc.types.Field(String, graphql_name="comment")
    """Optional comment for approving deployments"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ApproveVerifiableDomainInput(sgqlc.types.Input):
    """Autogenerated input type of ApproveVerifiableDomain"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The ID of the verifiable domain to approve."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ArchiveRepositoryInput(sgqlc.types.Input):
    """Autogenerated input type of ArchiveRepository"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The ID of the repository to mark as archived."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class AuditLogOrder(sgqlc.types.Input):
    """Ordering options for Audit Log connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(AuditLogOrderField, graphql_name="field")
    """The field to order Audit Logs by."""

    direction = sgqlc.types.Field(OrderDirection, graphql_name="direction")
    """The ordering direction."""


class CancelEnterpriseAdminInvitationInput(sgqlc.types.Input):
    """Autogenerated input type of CancelEnterpriseAdminInvitation"""

    __schema__ = github_schema
    __field_names__ = ("invitation_id", "client_mutation_id")
    invitation_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="invitationId")
    """The Node ID of the pending enterprise administrator invitation."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CancelSponsorshipInput(sgqlc.types.Input):
    """Autogenerated input type of CancelSponsorship"""

    __schema__ = github_schema
    __field_names__ = ("sponsor_id", "sponsor_login", "sponsorable_id", "sponsorable_login", "client_mutation_id")
    sponsor_id = sgqlc.types.Field(ID, graphql_name="sponsorId")
    """The ID of the user or organization who is acting as the sponsor,
    paying for the sponsorship. Required if sponsorLogin is not given.
    """

    sponsor_login = sgqlc.types.Field(String, graphql_name="sponsorLogin")
    """The username of the user or organization who is acting as the
    sponsor, paying for the sponsorship. Required if sponsorId is not
    given.
    """

    sponsorable_id = sgqlc.types.Field(ID, graphql_name="sponsorableId")
    """The ID of the user or organization who is receiving the
    sponsorship. Required if sponsorableLogin is not given.
    """

    sponsorable_login = sgqlc.types.Field(String, graphql_name="sponsorableLogin")
    """The username of the user or organization who is receiving the
    sponsorship. Required if sponsorableId is not given.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ChangeUserStatusInput(sgqlc.types.Input):
    """Autogenerated input type of ChangeUserStatus"""

    __schema__ = github_schema
    __field_names__ = ("emoji", "message", "organization_id", "limited_availability", "expires_at", "client_mutation_id")
    emoji = sgqlc.types.Field(String, graphql_name="emoji")
    """The emoji to represent your status. Can either be a native Unicode
    emoji or an emoji name with colons, e.g., :grinning:.
    """

    message = sgqlc.types.Field(String, graphql_name="message")
    """A short description of your current status."""

    organization_id = sgqlc.types.Field(ID, graphql_name="organizationId")
    """The ID of the organization whose members will be allowed to see
    the status. If omitted, the status will be publicly visible.
    """

    limited_availability = sgqlc.types.Field(Boolean, graphql_name="limitedAvailability")
    """Whether this status should indicate you are not fully available on
    GitHub, e.g., you are away.
    """

    expires_at = sgqlc.types.Field(DateTime, graphql_name="expiresAt")
    """If set, the user status will not be shown after this date."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CheckAnnotationData(sgqlc.types.Input):
    """Information from a check run analysis to specific lines of code."""

    __schema__ = github_schema
    __field_names__ = ("path", "location", "annotation_level", "message", "title", "raw_details")
    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="path")
    """The path of the file to add an annotation to."""

    location = sgqlc.types.Field(sgqlc.types.non_null("CheckAnnotationRange"), graphql_name="location")
    """The location of the annotation"""

    annotation_level = sgqlc.types.Field(sgqlc.types.non_null(CheckAnnotationLevel), graphql_name="annotationLevel")
    """Represents an annotation's information level"""

    message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="message")
    """A short description of the feedback for these lines of code."""

    title = sgqlc.types.Field(String, graphql_name="title")
    """The title that represents the annotation."""

    raw_details = sgqlc.types.Field(String, graphql_name="rawDetails")
    """Details about this annotation."""


class CheckAnnotationRange(sgqlc.types.Input):
    """Information from a check run analysis to specific lines of code."""

    __schema__ = github_schema
    __field_names__ = ("start_line", "start_column", "end_line", "end_column")
    start_line = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="startLine")
    """The starting line of the range."""

    start_column = sgqlc.types.Field(Int, graphql_name="startColumn")
    """The starting column of the range."""

    end_line = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="endLine")
    """The ending line of the range."""

    end_column = sgqlc.types.Field(Int, graphql_name="endColumn")
    """The ending column of the range."""


class CheckRunAction(sgqlc.types.Input):
    """Possible further actions the integrator can perform."""

    __schema__ = github_schema
    __field_names__ = ("label", "description", "identifier")
    label = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="label")
    """The text to be displayed on a button in the web UI."""

    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="description")
    """A short explanation of what this action would do."""

    identifier = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="identifier")
    """A reference for the action on the integrator's system."""


class CheckRunFilter(sgqlc.types.Input):
    """The filters that are available when fetching check runs."""

    __schema__ = github_schema
    __field_names__ = ("check_type", "app_id", "check_name", "status")
    check_type = sgqlc.types.Field(CheckRunType, graphql_name="checkType")
    """Filters the check runs by this type."""

    app_id = sgqlc.types.Field(Int, graphql_name="appId")
    """Filters the check runs created by this application ID."""

    check_name = sgqlc.types.Field(String, graphql_name="checkName")
    """Filters the check runs by this name."""

    status = sgqlc.types.Field(CheckStatusState, graphql_name="status")
    """Filters the check runs by this status."""


class CheckRunOutput(sgqlc.types.Input):
    """Descriptive details about the check run."""

    __schema__ = github_schema
    __field_names__ = ("title", "summary", "text", "annotations", "images")
    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
    """A title to provide for this check run."""

    summary = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="summary")
    """The summary of the check run (supports Commonmark)."""

    text = sgqlc.types.Field(String, graphql_name="text")
    """The details of the check run (supports Commonmark)."""

    annotations = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CheckAnnotationData)), graphql_name="annotations")
    """The annotations that are made as part of the check run."""

    images = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null("CheckRunOutputImage")), graphql_name="images")
    """Images attached to the check run output displayed in the GitHub
    pull request UI.
    """


class CheckRunOutputImage(sgqlc.types.Input):
    """Images attached to the check run output displayed in the GitHub
    pull request UI.
    """

    __schema__ = github_schema
    __field_names__ = ("alt", "image_url", "caption")
    alt = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="alt")
    """The alternative text for the image."""

    image_url = sgqlc.types.Field(sgqlc.types.non_null(URI), graphql_name="imageUrl")
    """The full URL of the image."""

    caption = sgqlc.types.Field(String, graphql_name="caption")
    """A short image description."""


class CheckSuiteAutoTriggerPreference(sgqlc.types.Input):
    """The auto-trigger preferences that are available for check suites."""

    __schema__ = github_schema
    __field_names__ = ("app_id", "setting")
    app_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="appId")
    """The node ID of the application that owns the check suite."""

    setting = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="setting")
    """Set to `true` to enable automatic creation of CheckSuite events
    upon pushes to the repository.
    """


class CheckSuiteFilter(sgqlc.types.Input):
    """The filters that are available when fetching check suites."""

    __schema__ = github_schema
    __field_names__ = ("app_id", "check_name")
    app_id = sgqlc.types.Field(Int, graphql_name="appId")
    """Filters the check suites created by this application ID."""

    check_name = sgqlc.types.Field(String, graphql_name="checkName")
    """Filters the check suites by this name."""


class ClearLabelsFromLabelableInput(sgqlc.types.Input):
    """Autogenerated input type of ClearLabelsFromLabelable"""

    __schema__ = github_schema
    __field_names__ = ("labelable_id", "client_mutation_id")
    labelable_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="labelableId")
    """The id of the labelable object to clear the labels from."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CloneProjectInput(sgqlc.types.Input):
    """Autogenerated input type of CloneProject"""

    __schema__ = github_schema
    __field_names__ = ("target_owner_id", "source_id", "include_workflows", "name", "body", "public", "client_mutation_id")
    target_owner_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="targetOwnerId")
    """The owner ID to create the project under."""

    source_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="sourceId")
    """The source project to clone."""

    include_workflows = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="includeWorkflows")
    """Whether or not to clone the source project's workflows."""

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The name of the project."""

    body = sgqlc.types.Field(String, graphql_name="body")
    """The description of the project."""

    public = sgqlc.types.Field(Boolean, graphql_name="public")
    """The visibility of the project, defaults to false (private)."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CloneTemplateRepositoryInput(sgqlc.types.Input):
    """Autogenerated input type of CloneTemplateRepository"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "name", "owner_id", "description", "visibility", "include_all_branches", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the template repository."""

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The name of the new repository."""

    owner_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="ownerId")
    """The ID of the owner for the new repository."""

    description = sgqlc.types.Field(String, graphql_name="description")
    """A short description of the new repository."""

    visibility = sgqlc.types.Field(sgqlc.types.non_null(RepositoryVisibility), graphql_name="visibility")
    """Indicates the repository's visibility level."""

    include_all_branches = sgqlc.types.Field(Boolean, graphql_name="includeAllBranches")
    """Whether to copy all branches from the template to the new
    repository. Defaults to copying only the default branch of the
    template.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CloseIssueInput(sgqlc.types.Input):
    """Autogenerated input type of CloseIssue"""

    __schema__ = github_schema
    __field_names__ = ("issue_id", "state_reason", "client_mutation_id")
    issue_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="issueId")
    """ID of the issue to be closed."""

    state_reason = sgqlc.types.Field(IssueClosedStateReason, graphql_name="stateReason")
    """The reason the issue is to be closed."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ClosePullRequestInput(sgqlc.types.Input):
    """Autogenerated input type of ClosePullRequest"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """ID of the pull request to be closed."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CommitAuthor(sgqlc.types.Input):
    """Specifies an author for filtering Git commits."""

    __schema__ = github_schema
    __field_names__ = ("id", "emails")
    id = sgqlc.types.Field(ID, graphql_name="id")
    """ID of a User to filter by. If non-null, only commits authored by
    this user will be returned. This field takes precedence over
    emails.
    """

    emails = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="emails")
    """Email addresses to filter by. Commits authored by any of the
    specified email addresses will be returned.
    """


class CommitContributionOrder(sgqlc.types.Input):
    """Ordering options for commit contribution connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(CommitContributionOrderField), graphql_name="field")
    """The field by which to order commit contributions."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class CommitMessage(sgqlc.types.Input):
    """A message to include with a new commit"""

    __schema__ = github_schema
    __field_names__ = ("headline", "body")
    headline = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="headline")
    """The headline of the message."""

    body = sgqlc.types.Field(String, graphql_name="body")
    """The body of the message."""


class CommittableBranch(sgqlc.types.Input):
    """A git ref for a commit to be appended to.  The ref must be a
    branch, i.e. its fully qualified name must start with
    `refs/heads/` (although the input is not required to be fully
    qualified).  The Ref may be specified by its global node ID or by
    the repository nameWithOwner and branch name.  ### Examples
    Specify a branch using a global node ID:      { "id":
    "MDM6UmVmMTpyZWZzL2hlYWRzL21haW4=" }  Specify a branch using
    nameWithOwner and branch name:      {       "nameWithOwner":
    "github/graphql-client",       "branchName": "main"     }
    """

    __schema__ = github_schema
    __field_names__ = ("id", "repository_name_with_owner", "branch_name")
    id = sgqlc.types.Field(ID, graphql_name="id")
    """The Node ID of the Ref to be updated."""

    repository_name_with_owner = sgqlc.types.Field(String, graphql_name="repositoryNameWithOwner")
    """The nameWithOwner of the repository to commit to."""

    branch_name = sgqlc.types.Field(String, graphql_name="branchName")
    """The unqualified name of the branch to append the commit to."""


class ContributionOrder(sgqlc.types.Input):
    """Ordering options for contribution connections."""

    __schema__ = github_schema
    __field_names__ = ("direction",)
    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class ConvertProjectCardNoteToIssueInput(sgqlc.types.Input):
    """Autogenerated input type of ConvertProjectCardNoteToIssue"""

    __schema__ = github_schema
    __field_names__ = ("project_card_id", "repository_id", "title", "body", "client_mutation_id")
    project_card_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="projectCardId")
    """The ProjectCard ID to convert."""

    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The ID of the repository to create the issue in."""

    title = sgqlc.types.Field(String, graphql_name="title")
    """The title of the newly created issue. Defaults to the card's note
    text.
    """

    body = sgqlc.types.Field(String, graphql_name="body")
    """The body of the newly created issue."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ConvertPullRequestToDraftInput(sgqlc.types.Input):
    """Autogenerated input type of ConvertPullRequestToDraft"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """ID of the pull request to convert to draft"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateBranchProtectionRuleInput(sgqlc.types.Input):
    """Autogenerated input type of CreateBranchProtectionRule"""

    __schema__ = github_schema
    __field_names__ = (
        "repository_id",
        "pattern",
        "requires_approving_reviews",
        "required_approving_review_count",
        "requires_commit_signatures",
        "requires_linear_history",
        "blocks_creations",
        "allows_force_pushes",
        "allows_deletions",
        "is_admin_enforced",
        "requires_status_checks",
        "requires_strict_status_checks",
        "requires_code_owner_reviews",
        "dismisses_stale_reviews",
        "restricts_review_dismissals",
        "review_dismissal_actor_ids",
        "bypass_pull_request_actor_ids",
        "bypass_force_push_actor_ids",
        "restricts_pushes",
        "push_actor_ids",
        "required_status_check_contexts",
        "required_status_checks",
        "requires_conversation_resolution",
        "client_mutation_id",
    )
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The global relay id of the repository in which a new branch
    protection rule should be created in.
    """

    pattern = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="pattern")
    """The glob-like pattern used to determine matching branches."""

    requires_approving_reviews = sgqlc.types.Field(Boolean, graphql_name="requiresApprovingReviews")
    """Are approving reviews required to update matching branches."""

    required_approving_review_count = sgqlc.types.Field(Int, graphql_name="requiredApprovingReviewCount")
    """Number of approving reviews required to update matching branches."""

    requires_commit_signatures = sgqlc.types.Field(Boolean, graphql_name="requiresCommitSignatures")
    """Are commits required to be signed."""

    requires_linear_history = sgqlc.types.Field(Boolean, graphql_name="requiresLinearHistory")
    """Are merge commits prohibited from being pushed to this branch."""

    blocks_creations = sgqlc.types.Field(Boolean, graphql_name="blocksCreations")
    """Is branch creation a protected operation."""

    allows_force_pushes = sgqlc.types.Field(Boolean, graphql_name="allowsForcePushes")
    """Are force pushes allowed on this branch."""

    allows_deletions = sgqlc.types.Field(Boolean, graphql_name="allowsDeletions")
    """Can this branch be deleted."""

    is_admin_enforced = sgqlc.types.Field(Boolean, graphql_name="isAdminEnforced")
    """Can admins overwrite branch protection."""

    requires_status_checks = sgqlc.types.Field(Boolean, graphql_name="requiresStatusChecks")
    """Are status checks required to update matching branches."""

    requires_strict_status_checks = sgqlc.types.Field(Boolean, graphql_name="requiresStrictStatusChecks")
    """Are branches required to be up to date before merging."""

    requires_code_owner_reviews = sgqlc.types.Field(Boolean, graphql_name="requiresCodeOwnerReviews")
    """Are reviews from code owners required to update matching branches."""

    dismisses_stale_reviews = sgqlc.types.Field(Boolean, graphql_name="dismissesStaleReviews")
    """Will new commits pushed to matching branches dismiss pull request
    review approvals.
    """

    restricts_review_dismissals = sgqlc.types.Field(Boolean, graphql_name="restrictsReviewDismissals")
    """Is dismissal of pull request reviews restricted."""

    review_dismissal_actor_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="reviewDismissalActorIds")
    """A list of User, Team, or App IDs allowed to dismiss reviews on
    pull requests targeting matching branches.
    """

    bypass_pull_request_actor_ids = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="bypassPullRequestActorIds"
    )
    """A list of User, Team, or App IDs allowed to bypass pull requests
    targeting matching branches.
    """

    bypass_force_push_actor_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="bypassForcePushActorIds")
    """A list of User, Team, or App IDs allowed to bypass force push
    targeting matching branches.
    """

    restricts_pushes = sgqlc.types.Field(Boolean, graphql_name="restrictsPushes")
    """Is pushing to matching branches restricted."""

    push_actor_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="pushActorIds")
    """A list of User, Team, or App IDs allowed to push to matching
    branches.
    """

    required_status_check_contexts = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="requiredStatusCheckContexts"
    )
    """List of required status check contexts that must pass for commits
    to be accepted to matching branches.
    """

    required_status_checks = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null("RequiredStatusCheckInput")), graphql_name="requiredStatusChecks"
    )
    """The list of required status checks"""

    requires_conversation_resolution = sgqlc.types.Field(Boolean, graphql_name="requiresConversationResolution")
    """Are conversations required to be resolved before merging."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateCheckRunInput(sgqlc.types.Input):
    """Autogenerated input type of CreateCheckRun"""

    __schema__ = github_schema
    __field_names__ = (
        "repository_id",
        "name",
        "head_sha",
        "details_url",
        "external_id",
        "status",
        "started_at",
        "conclusion",
        "completed_at",
        "output",
        "actions",
        "client_mutation_id",
    )
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The node ID of the repository."""

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The name of the check."""

    head_sha = sgqlc.types.Field(sgqlc.types.non_null(GitObjectID), graphql_name="headSha")
    """The SHA of the head commit."""

    details_url = sgqlc.types.Field(URI, graphql_name="detailsUrl")
    """The URL of the integrator's site that has the full details of the
    check.
    """

    external_id = sgqlc.types.Field(String, graphql_name="externalId")
    """A reference for the run on the integrator's system."""

    status = sgqlc.types.Field(RequestableCheckStatusState, graphql_name="status")
    """The current status."""

    started_at = sgqlc.types.Field(DateTime, graphql_name="startedAt")
    """The time that the check run began."""

    conclusion = sgqlc.types.Field(CheckConclusionState, graphql_name="conclusion")
    """The final conclusion of the check."""

    completed_at = sgqlc.types.Field(DateTime, graphql_name="completedAt")
    """The time that the check run finished."""

    output = sgqlc.types.Field(CheckRunOutput, graphql_name="output")
    """Descriptive details about the run."""

    actions = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CheckRunAction)), graphql_name="actions")
    """Possible further actions the integrator can perform, which a user
    may trigger.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateCheckSuiteInput(sgqlc.types.Input):
    """Autogenerated input type of CreateCheckSuite"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "head_sha", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the repository."""

    head_sha = sgqlc.types.Field(sgqlc.types.non_null(GitObjectID), graphql_name="headSha")
    """The SHA of the head commit."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateCommitOnBranchInput(sgqlc.types.Input):
    """Autogenerated input type of CreateCommitOnBranch"""

    __schema__ = github_schema
    __field_names__ = ("branch", "file_changes", "message", "expected_head_oid", "client_mutation_id")
    branch = sgqlc.types.Field(sgqlc.types.non_null(CommittableBranch), graphql_name="branch")
    """The Ref to be updated.  Must be a branch."""

    file_changes = sgqlc.types.Field("FileChanges", graphql_name="fileChanges")
    """A description of changes to files in this commit."""

    message = sgqlc.types.Field(sgqlc.types.non_null(CommitMessage), graphql_name="message")
    """The commit message the be included with the commit."""

    expected_head_oid = sgqlc.types.Field(sgqlc.types.non_null(GitObjectID), graphql_name="expectedHeadOid")
    """The git commit oid expected at the head of the branch prior to the
    commit
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateDiscussionInput(sgqlc.types.Input):
    """Autogenerated input type of CreateDiscussion"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "title", "body", "category_id", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The id of the repository on which to create the discussion."""

    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
    """The title of the discussion."""

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="body")
    """The body of the discussion."""

    category_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="categoryId")
    """The id of the discussion category to associate with this
    discussion.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateEnterpriseOrganizationInput(sgqlc.types.Input):
    """Autogenerated input type of CreateEnterpriseOrganization"""

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "login", "profile_name", "billing_email", "admin_logins", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise owning the new organization."""

    login = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="login")
    """The login of the new organization."""

    profile_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="profileName")
    """The profile name of the new organization."""

    billing_email = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="billingEmail")
    """The email used for sending billing receipts."""

    admin_logins = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(String))), graphql_name="adminLogins")
    """The logins for the administrators of the new organization."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateEnvironmentInput(sgqlc.types.Input):
    """Autogenerated input type of CreateEnvironment"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "name", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The node ID of the repository."""

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The name of the environment."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateIpAllowListEntryInput(sgqlc.types.Input):
    """Autogenerated input type of CreateIpAllowListEntry"""

    __schema__ = github_schema
    __field_names__ = ("owner_id", "allow_list_value", "name", "is_active", "client_mutation_id")
    owner_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="ownerId")
    """The ID of the owner for which to create the new IP allow list
    entry.
    """

    allow_list_value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="allowListValue")
    """An IP address or range of addresses in CIDR notation."""

    name = sgqlc.types.Field(String, graphql_name="name")
    """An optional name for the IP allow list entry."""

    is_active = sgqlc.types.Field(sgqlc.types.non_null(Boolean), graphql_name="isActive")
    """Whether the IP allow list entry is active when an IP allow list is
    enabled.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateIssueInput(sgqlc.types.Input):
    """Autogenerated input type of CreateIssue"""

    __schema__ = github_schema
    __field_names__ = (
        "repository_id",
        "title",
        "body",
        "assignee_ids",
        "milestone_id",
        "label_ids",
        "project_ids",
        "issue_template",
        "client_mutation_id",
    )
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the repository."""

    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
    """The title for the issue."""

    body = sgqlc.types.Field(String, graphql_name="body")
    """The body for the issue description."""

    assignee_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="assigneeIds")
    """The Node ID for the user assignee for this issue."""

    milestone_id = sgqlc.types.Field(ID, graphql_name="milestoneId")
    """The Node ID of the milestone for this issue."""

    label_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="labelIds")
    """An array of Node IDs of labels for this issue."""

    project_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="projectIds")
    """An array of Node IDs for projects associated with this issue."""

    issue_template = sgqlc.types.Field(String, graphql_name="issueTemplate")
    """The name of an issue template in the repository, assigns labels
    and assignees from the template to the issue
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateMigrationSourceInput(sgqlc.types.Input):
    """Autogenerated input type of CreateMigrationSource"""

    __schema__ = github_schema
    __field_names__ = ("name", "url", "access_token", "type", "owner_id", "github_pat", "client_mutation_id")
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The Octoshift migration source name."""

    url = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="url")
    """The Octoshift migration source URL."""

    access_token = sgqlc.types.Field(String, graphql_name="accessToken")
    """The Octoshift migration source access token."""

    type = sgqlc.types.Field(sgqlc.types.non_null(MigrationSourceType), graphql_name="type")
    """The Octoshift migration source type."""

    owner_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="ownerId")
    """The ID of the organization that will own the Octoshift migration
    source.
    """

    github_pat = sgqlc.types.Field(String, graphql_name="githubPat")
    """The GitHub personal access token of the user importing to the
    target repository.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateProjectInput(sgqlc.types.Input):
    """Autogenerated input type of CreateProject"""

    __schema__ = github_schema
    __field_names__ = ("owner_id", "name", "body", "template", "repository_ids", "client_mutation_id")
    owner_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="ownerId")
    """The owner ID to create the project under."""

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The name of project."""

    body = sgqlc.types.Field(String, graphql_name="body")
    """The description of project."""

    template = sgqlc.types.Field(ProjectTemplate, graphql_name="template")
    """The name of the GitHub-provided template."""

    repository_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="repositoryIds")
    """A list of repository IDs to create as linked repositories for the
    project
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreatePullRequestInput(sgqlc.types.Input):
    """Autogenerated input type of CreatePullRequest"""

    __schema__ = github_schema
    __field_names__ = (
        "repository_id",
        "base_ref_name",
        "head_ref_name",
        "title",
        "body",
        "maintainer_can_modify",
        "draft",
        "client_mutation_id",
    )
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the repository."""

    base_ref_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="baseRefName")
    """The name of the branch you want your changes pulled into. This
    should be an existing branch on the current repository. You cannot
    update the base branch on a pull request to point to another
    repository.
    """

    head_ref_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="headRefName")
    """The name of the branch where your changes are implemented. For
    cross-repository pull requests in the same network, namespace
    `head_ref_name` with a user like this: `username:branch`.
    """

    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
    """The title of the pull request."""

    body = sgqlc.types.Field(String, graphql_name="body")
    """The contents of the pull request."""

    maintainer_can_modify = sgqlc.types.Field(Boolean, graphql_name="maintainerCanModify")
    """Indicates whether maintainers can modify the pull request."""

    draft = sgqlc.types.Field(Boolean, graphql_name="draft")
    """Indicates whether this pull request should be a draft."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateRefInput(sgqlc.types.Input):
    """Autogenerated input type of CreateRef"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "name", "oid", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the Repository to create the Ref in."""

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The fully qualified name of the new Ref (ie:
    `refs/heads/my_new_branch`).
    """

    oid = sgqlc.types.Field(sgqlc.types.non_null(GitObjectID), graphql_name="oid")
    """The GitObjectID that the new Ref shall target. Must point to a
    commit.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateRepositoryInput(sgqlc.types.Input):
    """Autogenerated input type of CreateRepository"""

    __schema__ = github_schema
    __field_names__ = (
        "name",
        "owner_id",
        "description",
        "visibility",
        "template",
        "homepage_url",
        "has_wiki_enabled",
        "has_issues_enabled",
        "team_id",
        "client_mutation_id",
    )
    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The name of the new repository."""

    owner_id = sgqlc.types.Field(ID, graphql_name="ownerId")
    """The ID of the owner for the new repository."""

    description = sgqlc.types.Field(String, graphql_name="description")
    """A short description of the new repository."""

    visibility = sgqlc.types.Field(sgqlc.types.non_null(RepositoryVisibility), graphql_name="visibility")
    """Indicates the repository's visibility level."""

    template = sgqlc.types.Field(Boolean, graphql_name="template")
    """Whether this repository should be marked as a template such that
    anyone who can access it can create new repositories with the same
    files and directory structure.
    """

    homepage_url = sgqlc.types.Field(URI, graphql_name="homepageUrl")
    """The URL for a web page about this repository."""

    has_wiki_enabled = sgqlc.types.Field(Boolean, graphql_name="hasWikiEnabled")
    """Indicates if the repository should have the wiki feature enabled."""

    has_issues_enabled = sgqlc.types.Field(Boolean, graphql_name="hasIssuesEnabled")
    """Indicates if the repository should have the issues feature
    enabled.
    """

    team_id = sgqlc.types.Field(ID, graphql_name="teamId")
    """When an organization is specified as the owner, this ID identifies
    the team that should be granted access to the new repository.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateSponsorsTierInput(sgqlc.types.Input):
    """Autogenerated input type of CreateSponsorsTier"""

    __schema__ = github_schema
    __field_names__ = (
        "sponsorable_id",
        "sponsorable_login",
        "amount",
        "is_recurring",
        "repository_id",
        "repository_owner_login",
        "repository_name",
        "welcome_message",
        "description",
        "publish",
        "client_mutation_id",
    )
    sponsorable_id = sgqlc.types.Field(ID, graphql_name="sponsorableId")
    """The ID of the user or organization who owns the GitHub Sponsors
    profile. Defaults to the current user if omitted and
    sponsorableLogin is not given.
    """

    sponsorable_login = sgqlc.types.Field(String, graphql_name="sponsorableLogin")
    """The username of the user or organization who owns the GitHub
    Sponsors profile. Defaults to the current user if omitted and
    sponsorableId is not given.
    """

    amount = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="amount")
    """The value of the new tier in US dollars. Valid values: 1-12000."""

    is_recurring = sgqlc.types.Field(Boolean, graphql_name="isRecurring")
    """Whether sponsorships using this tier should happen monthly/yearly
    or just once.
    """

    repository_id = sgqlc.types.Field(ID, graphql_name="repositoryId")
    """Optional ID of the private repository that sponsors at this tier
    should gain read-only access to. Must be owned by an organization.
    """

    repository_owner_login = sgqlc.types.Field(String, graphql_name="repositoryOwnerLogin")
    """Optional login of the organization owner of the private repository
    that sponsors at this tier should gain read-only access to.
    Necessary if repositoryName is given. Will be ignored if
    repositoryId is given.
    """

    repository_name = sgqlc.types.Field(String, graphql_name="repositoryName")
    """Optional name of the private repository that sponsors at this tier
    should gain read-only access to. Must be owned by an organization.
    Necessary if repositoryOwnerLogin is given. Will be ignored if
    repositoryId is given.
    """

    welcome_message = sgqlc.types.Field(String, graphql_name="welcomeMessage")
    """Optional message new sponsors at this tier will receive."""

    description = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="description")
    """A description of what this tier is, what perks sponsors might
    receive, what a sponsorship at this tier means for you, etc.
    """

    publish = sgqlc.types.Field(Boolean, graphql_name="publish")
    """Whether to make the tier available immediately for sponsors to
    choose. Defaults to creating a draft tier that will not be
    publicly visible.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateSponsorshipInput(sgqlc.types.Input):
    """Autogenerated input type of CreateSponsorship"""

    __schema__ = github_schema
    __field_names__ = (
        "sponsor_id",
        "sponsor_login",
        "sponsorable_id",
        "sponsorable_login",
        "tier_id",
        "amount",
        "is_recurring",
        "receive_emails",
        "privacy_level",
        "client_mutation_id",
    )
    sponsor_id = sgqlc.types.Field(ID, graphql_name="sponsorId")
    """The ID of the user or organization who is acting as the sponsor,
    paying for the sponsorship. Required if sponsorLogin is not given.
    """

    sponsor_login = sgqlc.types.Field(String, graphql_name="sponsorLogin")
    """The username of the user or organization who is acting as the
    sponsor, paying for the sponsorship. Required if sponsorId is not
    given.
    """

    sponsorable_id = sgqlc.types.Field(ID, graphql_name="sponsorableId")
    """The ID of the user or organization who is receiving the
    sponsorship. Required if sponsorableLogin is not given.
    """

    sponsorable_login = sgqlc.types.Field(String, graphql_name="sponsorableLogin")
    """The username of the user or organization who is receiving the
    sponsorship. Required if sponsorableId is not given.
    """

    tier_id = sgqlc.types.Field(ID, graphql_name="tierId")
    """The ID of one of sponsorable's existing tiers to sponsor at.
    Required if amount is not specified.
    """

    amount = sgqlc.types.Field(Int, graphql_name="amount")
    """The amount to pay to the sponsorable in US dollars. Required if a
    tierId is not specified. Valid values: 1-12000.
    """

    is_recurring = sgqlc.types.Field(Boolean, graphql_name="isRecurring")
    """Whether the sponsorship should happen monthly/yearly or just this
    one time. Required if a tierId is not specified.
    """

    receive_emails = sgqlc.types.Field(Boolean, graphql_name="receiveEmails")
    """Whether the sponsor should receive email updates from the
    sponsorable.
    """

    privacy_level = sgqlc.types.Field(SponsorshipPrivacy, graphql_name="privacyLevel")
    """Specify whether others should be able to see that the sponsor is
    sponsoring the sponsorable. Public visibility still does not
    reveal which tier is used.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateTeamDiscussionCommentInput(sgqlc.types.Input):
    """Autogenerated input type of CreateTeamDiscussionComment"""

    __schema__ = github_schema
    __field_names__ = ("discussion_id", "body", "client_mutation_id")
    discussion_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="discussionId")
    """The ID of the discussion to which the comment belongs."""

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="body")
    """The content of the comment."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class CreateTeamDiscussionInput(sgqlc.types.Input):
    """Autogenerated input type of CreateTeamDiscussion"""

    __schema__ = github_schema
    __field_names__ = ("team_id", "title", "body", "private", "client_mutation_id")
    team_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="teamId")
    """The ID of the team to which the discussion belongs."""

    title = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="title")
    """The title of the discussion."""

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="body")
    """The content of the discussion."""

    private = sgqlc.types.Field(Boolean, graphql_name="private")
    """If true, restricts the visibility of this discussion to team
    members and organization admins. If false or not specified, allows
    any organization member to view this discussion.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeclineTopicSuggestionInput(sgqlc.types.Input):
    """Autogenerated input type of DeclineTopicSuggestion"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "name", "reason", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the repository."""

    name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="name")
    """The name of the suggested topic."""

    reason = sgqlc.types.Field(sgqlc.types.non_null(TopicSuggestionDeclineReason), graphql_name="reason")
    """The reason why the suggested topic is declined."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteBranchProtectionRuleInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteBranchProtectionRule"""

    __schema__ = github_schema
    __field_names__ = ("branch_protection_rule_id", "client_mutation_id")
    branch_protection_rule_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="branchProtectionRuleId")
    """The global relay id of the branch protection rule to be deleted."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteDeploymentInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteDeployment"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The Node ID of the deployment to be deleted."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteDiscussionCommentInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteDiscussionComment"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The Node id of the discussion comment to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteDiscussionInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteDiscussion"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The id of the discussion to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteEnvironmentInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteEnvironment"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The Node ID of the environment to be deleted."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteIpAllowListEntryInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteIpAllowListEntry"""

    __schema__ = github_schema
    __field_names__ = ("ip_allow_list_entry_id", "client_mutation_id")
    ip_allow_list_entry_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="ipAllowListEntryId")
    """The ID of the IP allow list entry to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteIssueCommentInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteIssueComment"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The ID of the comment to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteIssueInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteIssue"""

    __schema__ = github_schema
    __field_names__ = ("issue_id", "client_mutation_id")
    issue_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="issueId")
    """The ID of the issue to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteProjectCardInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteProjectCard"""

    __schema__ = github_schema
    __field_names__ = ("card_id", "client_mutation_id")
    card_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="cardId")
    """The id of the card to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteProjectColumnInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteProjectColumn"""

    __schema__ = github_schema
    __field_names__ = ("column_id", "client_mutation_id")
    column_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="columnId")
    """The id of the column to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteProjectInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteProject"""

    __schema__ = github_schema
    __field_names__ = ("project_id", "client_mutation_id")
    project_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="projectId")
    """The Project ID to update."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteProjectNextItemInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteProjectNextItem"""

    __schema__ = github_schema
    __field_names__ = ("project_id", "item_id", "client_mutation_id")
    project_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="projectId")
    """The ID of the Project from which the item should be removed."""

    item_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="itemId")
    """The ID of the item to be removed."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeletePullRequestReviewCommentInput(sgqlc.types.Input):
    """Autogenerated input type of DeletePullRequestReviewComment"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The ID of the comment to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeletePullRequestReviewInput(sgqlc.types.Input):
    """Autogenerated input type of DeletePullRequestReview"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_review_id", "client_mutation_id")
    pull_request_review_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestReviewId")
    """The Node ID of the pull request review to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteRefInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteRef"""

    __schema__ = github_schema
    __field_names__ = ("ref_id", "client_mutation_id")
    ref_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="refId")
    """The Node ID of the Ref to be deleted."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteTeamDiscussionCommentInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteTeamDiscussionComment"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The ID of the comment to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteTeamDiscussionInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteTeamDiscussion"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The discussion ID to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeleteVerifiableDomainInput(sgqlc.types.Input):
    """Autogenerated input type of DeleteVerifiableDomain"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The ID of the verifiable domain to delete."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DeploymentOrder(sgqlc.types.Input):
    """Ordering options for deployment connections"""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(DeploymentOrderField), graphql_name="field")
    """The field to order deployments by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class DisablePullRequestAutoMergeInput(sgqlc.types.Input):
    """Autogenerated input type of DisablePullRequestAutoMerge"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """ID of the pull request to disable auto merge on."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DiscussionOrder(sgqlc.types.Input):
    """Ways in which lists of discussions can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(DiscussionOrderField), graphql_name="field")
    """The field by which to order discussions."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order discussions by the specified
    field.
    """


class DiscussionPollOptionOrder(sgqlc.types.Input):
    """Ordering options for discussion poll option connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(DiscussionPollOptionOrderField), graphql_name="field")
    """The field to order poll options by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class DismissPullRequestReviewInput(sgqlc.types.Input):
    """Autogenerated input type of DismissPullRequestReview"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_review_id", "message", "client_mutation_id")
    pull_request_review_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestReviewId")
    """The Node ID of the pull request review to modify."""

    message = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="message")
    """The contents of the pull request review dismissal message."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DismissRepositoryVulnerabilityAlertInput(sgqlc.types.Input):
    """Autogenerated input type of DismissRepositoryVulnerabilityAlert"""

    __schema__ = github_schema
    __field_names__ = ("repository_vulnerability_alert_id", "dismiss_reason", "client_mutation_id")
    repository_vulnerability_alert_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryVulnerabilityAlertId")
    """The Dependabot alert ID to dismiss."""

    dismiss_reason = sgqlc.types.Field(sgqlc.types.non_null(DismissReason), graphql_name="dismissReason")
    """The reason the Dependabot alert is being dismissed."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class DraftPullRequestReviewComment(sgqlc.types.Input):
    """Specifies a review comment to be left with a Pull Request Review."""

    __schema__ = github_schema
    __field_names__ = ("path", "position", "body")
    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="path")
    """Path to the file being commented on."""

    position = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="position")
    """Position in the file to leave a comment on."""

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="body")
    """Body of the comment to leave."""


class DraftPullRequestReviewThread(sgqlc.types.Input):
    """Specifies a review comment thread to be left with a Pull Request
    Review.
    """

    __schema__ = github_schema
    __field_names__ = ("path", "line", "side", "start_line", "start_side", "body")
    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="path")
    """Path to the file being commented on."""

    line = sgqlc.types.Field(sgqlc.types.non_null(Int), graphql_name="line")
    """The line of the blob to which the thread refers. The end of the
    line range for multi-line comments.
    """

    side = sgqlc.types.Field(DiffSide, graphql_name="side")
    """The side of the diff on which the line resides. For multi-line
    comments, this is the side for the end of the line range.
    """

    start_line = sgqlc.types.Field(Int, graphql_name="startLine")
    """The first line of the range to which the comment refers."""

    start_side = sgqlc.types.Field(DiffSide, graphql_name="startSide")
    """The side of the diff on which the start line resides."""

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="body")
    """Body of the comment to leave."""


class EnablePullRequestAutoMergeInput(sgqlc.types.Input):
    """Autogenerated input type of EnablePullRequestAutoMerge"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "commit_headline", "commit_body", "merge_method", "author_email", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """ID of the pull request to enable auto-merge on."""

    commit_headline = sgqlc.types.Field(String, graphql_name="commitHeadline")
    """Commit headline to use for the commit when the PR is mergable; if
    omitted, a default message will be used.
    """

    commit_body = sgqlc.types.Field(String, graphql_name="commitBody")
    """Commit body to use for the commit when the PR is mergable; if
    omitted, a default message will be used.
    """

    merge_method = sgqlc.types.Field(PullRequestMergeMethod, graphql_name="mergeMethod")
    """The merge method to use. If omitted, defaults to 'MERGE' """

    author_email = sgqlc.types.Field(String, graphql_name="authorEmail")
    """The email address to associate with this merge."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class EnterpriseAdministratorInvitationOrder(sgqlc.types.Input):
    """Ordering options for enterprise administrator invitation
    connections
    """

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseAdministratorInvitationOrderField), graphql_name="field")
    """The field to order enterprise administrator invitations by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class EnterpriseMemberOrder(sgqlc.types.Input):
    """Ordering options for enterprise member connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseMemberOrderField), graphql_name="field")
    """The field to order enterprise members by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class EnterpriseServerInstallationOrder(sgqlc.types.Input):
    """Ordering options for Enterprise Server installation connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseServerInstallationOrderField), graphql_name="field")
    """The field to order Enterprise Server installations by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class EnterpriseServerUserAccountEmailOrder(sgqlc.types.Input):
    """Ordering options for Enterprise Server user account email
    connections.
    """

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseServerUserAccountEmailOrderField), graphql_name="field")
    """The field to order emails by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class EnterpriseServerUserAccountOrder(sgqlc.types.Input):
    """Ordering options for Enterprise Server user account connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseServerUserAccountOrderField), graphql_name="field")
    """The field to order user accounts by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class EnterpriseServerUserAccountsUploadOrder(sgqlc.types.Input):
    """Ordering options for Enterprise Server user accounts upload
    connections.
    """

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseServerUserAccountsUploadOrderField), graphql_name="field")
    """The field to order user accounts uploads by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class FileAddition(sgqlc.types.Input):
    """A command to add a file at the given path with the given contents
    as part of a commit.  Any existing file at that that path will be
    replaced.
    """

    __schema__ = github_schema
    __field_names__ = ("path", "contents")
    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="path")
    """The path in the repository where the file will be located"""

    contents = sgqlc.types.Field(sgqlc.types.non_null(Base64String), graphql_name="contents")
    """The base64 encoded contents of the file"""


class FileChanges(sgqlc.types.Input):
    """A description of a set of changes to a file tree to be made as
    part of a git commit, modeled as zero or more file `additions` and
    zero or more file `deletions`.  Both fields are optional; omitting
    both will produce a commit with no file changes.  `deletions` and
    `additions` describe changes to files identified by their path in
    the git tree using unix-style path separators, i.e. `/`.  The root
    of a git tree is an empty string, so paths are not slash-prefixed.
    `path` values must be unique across all `additions` and
    `deletions` provided.  Any duplication will result in a validation
    error.  ### Encoding  File contents must be provided in full for
    each `FileAddition`.  The `contents` of a `FileAddition` must be
    encoded using RFC 4648 compliant base64, i.e. correct padding is
    required and no characters outside the standard alphabet may be
    used.  Invalid base64 encoding will be rejected with a validation
    error.  The encoded contents may be binary.  For text files, no
    assumptions are made about the character encoding of the file
    contents (after base64 decoding).  No charset transcoding or line-
    ending normalization will be performed; it is the client's
    responsibility to manage the character encoding of files they
    provide. However, for maximum compatibility we recommend using
    UTF-8 encoding and ensuring that all files in a repository use a
    consistent line-ending convention (`\n` or `\r\n`), and that all
    files end with a newline.  ### Modeling file changes  Each of the
    the five types of conceptual changes that can be made in a git
    commit can be described using the `FileChanges` type as follows:
    1. New file addition: create file `hello world\n` at path
    `docs/README.txt`:         {          "additions" [            {
    "path": "docs/README.txt",              "contents":
    base64encode("hello world\n")            }          ]        }  2.
    Existing file modification: change existing `docs/README.txt` to
    have new    content `new content here\n`:         {
    "additions" [            {              "path": "docs/README.txt",
    "contents": base64encode("new content here\n")            }
    ]        }  3. Existing file deletion: remove existing file
    `docs/README.txt`.    Note that the path is required to exist --
    specifying a    path that does not exist on the given branch will
    abort the    commit and return an error.         {
    "deletions" [            {              "path": "docs/README.txt"
    }          ]        }   4. File rename with no changes: rename
    `docs/README.txt` with    previous content `hello world\n` to the
    same content at    `newdocs/README.txt`:         {
    "deletions" [            {              "path": "docs/README.txt",
    }          ],          "additions" [            {
    "path": "newdocs/README.txt",              "contents":
    base64encode("hello world\n")            }          ]        }
    5. File rename with changes: rename `docs/README.txt` with
    previous content `hello world\n` to a file at path
    `newdocs/README.txt` with content `new contents\n`:         {
    "deletions" [            {              "path": "docs/README.txt",
    }          ],          "additions" [            {
    "path": "newdocs/README.txt",              "contents":
    base64encode("new contents\n")            }          ]        }
    """

    __schema__ = github_schema
    __field_names__ = ("deletions", "additions")
    deletions = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null("FileDeletion")), graphql_name="deletions")
    """Files to delete."""

    additions = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(FileAddition)), graphql_name="additions")
    """File to add or change."""


class FileDeletion(sgqlc.types.Input):
    """A command to delete the file at the given path as part of a
    commit.
    """

    __schema__ = github_schema
    __field_names__ = ("path",)
    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="path")
    """The path to delete"""


class FollowOrganizationInput(sgqlc.types.Input):
    """Autogenerated input type of FollowOrganization"""

    __schema__ = github_schema
    __field_names__ = ("organization_id", "client_mutation_id")
    organization_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="organizationId")
    """ID of the organization to follow."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class FollowUserInput(sgqlc.types.Input):
    """Autogenerated input type of FollowUser"""

    __schema__ = github_schema
    __field_names__ = ("user_id", "client_mutation_id")
    user_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="userId")
    """ID of the user to follow."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class GistOrder(sgqlc.types.Input):
    """Ordering options for gist connections"""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(GistOrderField), graphql_name="field")
    """The field to order repositories by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class GrantEnterpriseOrganizationsMigratorRoleInput(sgqlc.types.Input):
    """Autogenerated input type of
    GrantEnterpriseOrganizationsMigratorRole
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "login", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise to which all organizations managed by it
    will be granted the migrator role.
    """

    login = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="login")
    """The login of the user to grant the migrator role"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class GrantMigratorRoleInput(sgqlc.types.Input):
    """Autogenerated input type of GrantMigratorRole"""

    __schema__ = github_schema
    __field_names__ = ("organization_id", "actor", "actor_type", "client_mutation_id")
    organization_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="organizationId")
    """The ID of the organization that the user/team belongs to."""

    actor = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="actor")
    """The user login or Team slug to grant the migrator role."""

    actor_type = sgqlc.types.Field(sgqlc.types.non_null(ActorType), graphql_name="actorType")
    """Specifies the type of the actor, can be either USER or TEAM."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class InviteEnterpriseAdminInput(sgqlc.types.Input):
    """Autogenerated input type of InviteEnterpriseAdmin"""

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "invitee", "email", "role", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise to which you want to invite an
    administrator.
    """

    invitee = sgqlc.types.Field(String, graphql_name="invitee")
    """The login of a user to invite as an administrator."""

    email = sgqlc.types.Field(String, graphql_name="email")
    """The email of the person to invite as an administrator."""

    role = sgqlc.types.Field(EnterpriseAdministratorRole, graphql_name="role")
    """The role of the administrator."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class IpAllowListEntryOrder(sgqlc.types.Input):
    """Ordering options for IP allow list entry connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(IpAllowListEntryOrderField), graphql_name="field")
    """The field to order IP allow list entries by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class IssueCommentOrder(sgqlc.types.Input):
    """Ways in which lists of issue comments can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(IssueCommentOrderField), graphql_name="field")
    """The field in which to order issue comments by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order issue comments by the specified
    field.
    """


class IssueFilters(sgqlc.types.Input):
    """Ways in which to filter lists of issues."""

    __schema__ = github_schema
    __field_names__ = (
        "assignee",
        "created_by",
        "labels",
        "mentioned",
        "milestone",
        "milestone_number",
        "since",
        "states",
        "viewer_subscribed",
    )
    assignee = sgqlc.types.Field(String, graphql_name="assignee")
    """List issues assigned to given name. Pass in `null` for issues with
    no assigned user, and `*` for issues assigned to any user.
    """

    created_by = sgqlc.types.Field(String, graphql_name="createdBy")
    """List issues created by given name."""

    labels = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="labels")
    """List issues where the list of label names exist on the issue."""

    mentioned = sgqlc.types.Field(String, graphql_name="mentioned")
    """List issues where the given name is mentioned in the issue."""

    milestone = sgqlc.types.Field(String, graphql_name="milestone")
    """List issues by given milestone argument. If an string
    representation of an integer is passed, it should refer to a
    milestone by its database ID. Pass in `null` for issues with no
    milestone, and `*` for issues that are assigned to any milestone.
    """

    milestone_number = sgqlc.types.Field(String, graphql_name="milestoneNumber")
    """List issues by given milestone argument. If an string
    representation of an integer is passed, it should refer to a
    milestone by its number field. Pass in `null` for issues with no
    milestone, and `*` for issues that are assigned to any milestone.
    """

    since = sgqlc.types.Field(DateTime, graphql_name="since")
    """List issues that have been updated at or after the given date."""

    states = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(IssueState)), graphql_name="states")
    """List issues filtered by the list of states given."""

    viewer_subscribed = sgqlc.types.Field(Boolean, graphql_name="viewerSubscribed")
    """List issues subscribed to by viewer."""


class IssueOrder(sgqlc.types.Input):
    """Ways in which lists of issues can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(IssueOrderField), graphql_name="field")
    """The field in which to order issues by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order issues by the specified field."""


class LabelOrder(sgqlc.types.Input):
    """Ways in which lists of labels can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(LabelOrderField), graphql_name="field")
    """The field in which to order labels by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order labels by the specified field."""


class LanguageOrder(sgqlc.types.Input):
    """Ordering options for language connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(LanguageOrderField), graphql_name="field")
    """The field to order languages by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class LinkRepositoryToProjectInput(sgqlc.types.Input):
    """Autogenerated input type of LinkRepositoryToProject"""

    __schema__ = github_schema
    __field_names__ = ("project_id", "repository_id", "client_mutation_id")
    project_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="projectId")
    """The ID of the Project to link to a Repository"""

    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The ID of the Repository to link to a Project."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class LockLockableInput(sgqlc.types.Input):
    """Autogenerated input type of LockLockable"""

    __schema__ = github_schema
    __field_names__ = ("lockable_id", "lock_reason", "client_mutation_id")
    lockable_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="lockableId")
    """ID of the item to be locked."""

    lock_reason = sgqlc.types.Field(LockReason, graphql_name="lockReason")
    """A reason for why the item will be locked."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class MarkDiscussionCommentAsAnswerInput(sgqlc.types.Input):
    """Autogenerated input type of MarkDiscussionCommentAsAnswer"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The Node ID of the discussion comment to mark as an answer."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class MarkFileAsViewedInput(sgqlc.types.Input):
    """Autogenerated input type of MarkFileAsViewed"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "path", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """The Node ID of the pull request."""

    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="path")
    """The path of the file to mark as viewed"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class MarkPullRequestReadyForReviewInput(sgqlc.types.Input):
    """Autogenerated input type of MarkPullRequestReadyForReview"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """ID of the pull request to be marked as ready for review."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class MergeBranchInput(sgqlc.types.Input):
    """Autogenerated input type of MergeBranch"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "base", "head", "commit_message", "author_email", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the Repository containing the base branch that will
    be modified.
    """

    base = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="base")
    """The name of the base branch that the provided head will be merged
    into.
    """

    head = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="head")
    """The head to merge into the base branch. This can be a branch name
    or a commit GitObjectID.
    """

    commit_message = sgqlc.types.Field(String, graphql_name="commitMessage")
    """Message to use for the merge commit. If omitted, a default will be
    used.
    """

    author_email = sgqlc.types.Field(String, graphql_name="authorEmail")
    """The email address to associate with this commit."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class MergePullRequestInput(sgqlc.types.Input):
    """Autogenerated input type of MergePullRequest"""

    __schema__ = github_schema
    __field_names__ = (
        "pull_request_id",
        "commit_headline",
        "commit_body",
        "expected_head_oid",
        "merge_method",
        "author_email",
        "client_mutation_id",
    )
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """ID of the pull request to be merged."""

    commit_headline = sgqlc.types.Field(String, graphql_name="commitHeadline")
    """Commit headline to use for the merge commit; if omitted, a default
    message will be used.
    """

    commit_body = sgqlc.types.Field(String, graphql_name="commitBody")
    """Commit body to use for the merge commit; if omitted, a default
    message will be used
    """

    expected_head_oid = sgqlc.types.Field(GitObjectID, graphql_name="expectedHeadOid")
    """OID that the pull request head ref must match to allow merge; if
    omitted, no check is performed.
    """

    merge_method = sgqlc.types.Field(PullRequestMergeMethod, graphql_name="mergeMethod")
    """The merge method to use. If omitted, defaults to 'MERGE' """

    author_email = sgqlc.types.Field(String, graphql_name="authorEmail")
    """The email address to associate with this merge."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class MilestoneOrder(sgqlc.types.Input):
    """Ordering options for milestone connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(MilestoneOrderField), graphql_name="field")
    """The field to order milestones by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class MinimizeCommentInput(sgqlc.types.Input):
    """Autogenerated input type of MinimizeComment"""

    __schema__ = github_schema
    __field_names__ = ("subject_id", "classifier", "client_mutation_id")
    subject_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="subjectId")
    """The Node ID of the subject to modify."""

    classifier = sgqlc.types.Field(sgqlc.types.non_null(ReportedContentClassifiers), graphql_name="classifier")
    """The classification of comment"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class MoveProjectCardInput(sgqlc.types.Input):
    """Autogenerated input type of MoveProjectCard"""

    __schema__ = github_schema
    __field_names__ = ("card_id", "column_id", "after_card_id", "client_mutation_id")
    card_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="cardId")
    """The id of the card to move."""

    column_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="columnId")
    """The id of the column to move it into."""

    after_card_id = sgqlc.types.Field(ID, graphql_name="afterCardId")
    """Place the new card after the card with this id. Pass null to place
    it at the top.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class MoveProjectColumnInput(sgqlc.types.Input):
    """Autogenerated input type of MoveProjectColumn"""

    __schema__ = github_schema
    __field_names__ = ("column_id", "after_column_id", "client_mutation_id")
    column_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="columnId")
    """The id of the column to move."""

    after_column_id = sgqlc.types.Field(ID, graphql_name="afterColumnId")
    """Place the new column after the column with this id. Pass null to
    place it at the front.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class OrgEnterpriseOwnerOrder(sgqlc.types.Input):
    """Ordering options for an organization's enterprise owner
    connections.
    """

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(OrgEnterpriseOwnerOrderField), graphql_name="field")
    """The field to order enterprise owners by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class OrganizationOrder(sgqlc.types.Input):
    """Ordering options for organization connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(OrganizationOrderField), graphql_name="field")
    """The field to order organizations by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class PackageFileOrder(sgqlc.types.Input):
    """Ways in which lists of package files can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(PackageFileOrderField, graphql_name="field")
    """The field in which to order package files by."""

    direction = sgqlc.types.Field(OrderDirection, graphql_name="direction")
    """The direction in which to order package files by the specified
    field.
    """


class PackageOrder(sgqlc.types.Input):
    """Ways in which lists of packages can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(PackageOrderField, graphql_name="field")
    """The field in which to order packages by."""

    direction = sgqlc.types.Field(OrderDirection, graphql_name="direction")
    """The direction in which to order packages by the specified field."""


class PackageVersionOrder(sgqlc.types.Input):
    """Ways in which lists of package versions can be ordered upon
    return.
    """

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(PackageVersionOrderField, graphql_name="field")
    """The field in which to order package versions by."""

    direction = sgqlc.types.Field(OrderDirection, graphql_name="direction")
    """The direction in which to order package versions by the specified
    field.
    """


class PinIssueInput(sgqlc.types.Input):
    """Autogenerated input type of PinIssue"""

    __schema__ = github_schema
    __field_names__ = ("issue_id", "client_mutation_id")
    issue_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="issueId")
    """The ID of the issue to be pinned"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ProjectOrder(sgqlc.types.Input):
    """Ways in which lists of projects can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(ProjectOrderField), graphql_name="field")
    """The field in which to order projects by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order projects by the specified field."""


class PullRequestOrder(sgqlc.types.Input):
    """Ways in which lists of issues can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(PullRequestOrderField), graphql_name="field")
    """The field in which to order pull requests by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order pull requests by the specified
    field.
    """


class ReactionOrder(sgqlc.types.Input):
    """Ways in which lists of reactions can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(ReactionOrderField), graphql_name="field")
    """The field in which to order reactions by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order reactions by the specified field."""


class RefOrder(sgqlc.types.Input):
    """Ways in which lists of git refs can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(RefOrderField), graphql_name="field")
    """The field in which to order refs by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order refs by the specified field."""


class RegenerateEnterpriseIdentityProviderRecoveryCodesInput(sgqlc.types.Input):
    """Autogenerated input type of
    RegenerateEnterpriseIdentityProviderRecoveryCodes
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set an identity provider."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RegenerateVerifiableDomainTokenInput(sgqlc.types.Input):
    """Autogenerated input type of RegenerateVerifiableDomainToken"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The ID of the verifiable domain to regenerate the verification
    token of.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RejectDeploymentsInput(sgqlc.types.Input):
    """Autogenerated input type of RejectDeployments"""

    __schema__ = github_schema
    __field_names__ = ("workflow_run_id", "environment_ids", "comment", "client_mutation_id")
    workflow_run_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="workflowRunId")
    """The node ID of the workflow run containing the pending
    deployments.
    """

    environment_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name="environmentIds")
    """The ids of environments to reject deployments"""

    comment = sgqlc.types.Field(String, graphql_name="comment")
    """Optional comment for rejecting deployments"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ReleaseOrder(sgqlc.types.Input):
    """Ways in which lists of releases can be ordered upon return."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(ReleaseOrderField), graphql_name="field")
    """The field in which to order releases by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order releases by the specified field."""


class RemoveAssigneesFromAssignableInput(sgqlc.types.Input):
    """Autogenerated input type of RemoveAssigneesFromAssignable"""

    __schema__ = github_schema
    __field_names__ = ("assignable_id", "assignee_ids", "client_mutation_id")
    assignable_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="assignableId")
    """The id of the assignable object to remove assignees from."""

    assignee_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name="assigneeIds")
    """The id of users to remove as assignees."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RemoveEnterpriseAdminInput(sgqlc.types.Input):
    """Autogenerated input type of RemoveEnterpriseAdmin"""

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "login", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The Enterprise ID from which to remove the administrator."""

    login = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="login")
    """The login of the user to remove as an administrator."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RemoveEnterpriseIdentityProviderInput(sgqlc.types.Input):
    """Autogenerated input type of RemoveEnterpriseIdentityProvider"""

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise from which to remove the identity
    provider.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RemoveEnterpriseOrganizationInput(sgqlc.types.Input):
    """Autogenerated input type of RemoveEnterpriseOrganization"""

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "organization_id", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise from which the organization should be
    removed.
    """

    organization_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="organizationId")
    """The ID of the organization to remove from the enterprise."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RemoveEnterpriseSupportEntitlementInput(sgqlc.types.Input):
    """Autogenerated input type of RemoveEnterpriseSupportEntitlement"""

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "login", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the Enterprise which the admin belongs to."""

    login = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="login")
    """The login of a member who will lose the support entitlement."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RemoveLabelsFromLabelableInput(sgqlc.types.Input):
    """Autogenerated input type of RemoveLabelsFromLabelable"""

    __schema__ = github_schema
    __field_names__ = ("labelable_id", "label_ids", "client_mutation_id")
    labelable_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="labelableId")
    """The id of the Labelable to remove labels from."""

    label_ids = sgqlc.types.Field(sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(ID))), graphql_name="labelIds")
    """The ids of labels to remove."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RemoveOutsideCollaboratorInput(sgqlc.types.Input):
    """Autogenerated input type of RemoveOutsideCollaborator"""

    __schema__ = github_schema
    __field_names__ = ("user_id", "organization_id", "client_mutation_id")
    user_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="userId")
    """The ID of the outside collaborator to remove."""

    organization_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="organizationId")
    """The ID of the organization to remove the outside collaborator
    from.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RemoveReactionInput(sgqlc.types.Input):
    """Autogenerated input type of RemoveReaction"""

    __schema__ = github_schema
    __field_names__ = ("subject_id", "content", "client_mutation_id")
    subject_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="subjectId")
    """The Node ID of the subject to modify."""

    content = sgqlc.types.Field(sgqlc.types.non_null(ReactionContent), graphql_name="content")
    """The name of the emoji reaction to remove."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RemoveStarInput(sgqlc.types.Input):
    """Autogenerated input type of RemoveStar"""

    __schema__ = github_schema
    __field_names__ = ("starrable_id", "client_mutation_id")
    starrable_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="starrableId")
    """The Starrable ID to unstar."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RemoveUpvoteInput(sgqlc.types.Input):
    """Autogenerated input type of RemoveUpvote"""

    __schema__ = github_schema
    __field_names__ = ("subject_id", "client_mutation_id")
    subject_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="subjectId")
    """The Node ID of the discussion or comment to remove upvote."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ReopenIssueInput(sgqlc.types.Input):
    """Autogenerated input type of ReopenIssue"""

    __schema__ = github_schema
    __field_names__ = ("issue_id", "client_mutation_id")
    issue_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="issueId")
    """ID of the issue to be opened."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ReopenPullRequestInput(sgqlc.types.Input):
    """Autogenerated input type of ReopenPullRequest"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """ID of the pull request to be reopened."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RepositoryInvitationOrder(sgqlc.types.Input):
    """Ordering options for repository invitation connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(RepositoryInvitationOrderField), graphql_name="field")
    """The field to order repository invitations by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class RepositoryMigrationOrder(sgqlc.types.Input):
    """Ordering options for repository migrations."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(RepositoryMigrationOrderField), graphql_name="field")
    """The field to order repository migrations by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(RepositoryMigrationOrderDirection), graphql_name="direction")
    """The ordering direction."""


class RepositoryOrder(sgqlc.types.Input):
    """Ordering options for repository connections"""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(RepositoryOrderField), graphql_name="field")
    """The field to order repositories by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class RequestReviewsInput(sgqlc.types.Input):
    """Autogenerated input type of RequestReviews"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "user_ids", "team_ids", "union", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """The Node ID of the pull request to modify."""

    user_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="userIds")
    """The Node IDs of the user to request."""

    team_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="teamIds")
    """The Node IDs of the team to request."""

    union = sgqlc.types.Field(Boolean, graphql_name="union")
    """Add users to the set rather than replace."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RequiredStatusCheckInput(sgqlc.types.Input):
    """Specifies the attributes for a new or updated required status
    check.
    """

    __schema__ = github_schema
    __field_names__ = ("context", "app_id")
    context = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="context")
    """Status check context that must pass for commits to be accepted to
    the matching branch.
    """

    app_id = sgqlc.types.Field(ID, graphql_name="appId")
    """The ID of the App that must set the status in order for it to be
    accepted. Omit this value to use whichever app has recently been
    setting this status, or use "any" to allow any app to set the
    status.
    """


class RerequestCheckSuiteInput(sgqlc.types.Input):
    """Autogenerated input type of RerequestCheckSuite"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "check_suite_id", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the repository."""

    check_suite_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="checkSuiteId")
    """The Node ID of the check suite."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class ResolveReviewThreadInput(sgqlc.types.Input):
    """Autogenerated input type of ResolveReviewThread"""

    __schema__ = github_schema
    __field_names__ = ("thread_id", "client_mutation_id")
    thread_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="threadId")
    """The ID of the thread to resolve"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RevokeEnterpriseOrganizationsMigratorRoleInput(sgqlc.types.Input):
    """Autogenerated input type of
    RevokeEnterpriseOrganizationsMigratorRole
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "login", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise to which all organizations managed by it
    will be granted the migrator role.
    """

    login = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="login")
    """The login of the user to revoke the migrator role"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class RevokeMigratorRoleInput(sgqlc.types.Input):
    """Autogenerated input type of RevokeMigratorRole"""

    __schema__ = github_schema
    __field_names__ = ("organization_id", "actor", "actor_type", "client_mutation_id")
    organization_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="organizationId")
    """The ID of the organization that the user/team belongs to."""

    actor = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="actor")
    """The user login or Team slug to revoke the migrator role from."""

    actor_type = sgqlc.types.Field(sgqlc.types.non_null(ActorType), graphql_name="actorType")
    """Specifies the type of the actor, can be either USER or TEAM."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class SavedReplyOrder(sgqlc.types.Input):
    """Ordering options for saved reply connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(SavedReplyOrderField), graphql_name="field")
    """The field to order saved replies by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class SecurityAdvisoryIdentifierFilter(sgqlc.types.Input):
    """An advisory identifier to filter results on."""

    __schema__ = github_schema
    __field_names__ = ("type", "value")
    type = sgqlc.types.Field(sgqlc.types.non_null(SecurityAdvisoryIdentifierType), graphql_name="type")
    """The identifier type."""

    value = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="value")
    """The identifier string. Supports exact or partial matching."""


class SecurityAdvisoryOrder(sgqlc.types.Input):
    """Ordering options for security advisory connections"""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(SecurityAdvisoryOrderField), graphql_name="field")
    """The field to order security advisories by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class SecurityVulnerabilityOrder(sgqlc.types.Input):
    """Ordering options for security vulnerability connections"""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(SecurityVulnerabilityOrderField), graphql_name="field")
    """The field to order security vulnerabilities by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class SetEnterpriseIdentityProviderInput(sgqlc.types.Input):
    """Autogenerated input type of SetEnterpriseIdentityProvider"""

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "sso_url", "issuer", "idp_certificate", "signature_method", "digest_method", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set an identity provider."""

    sso_url = sgqlc.types.Field(sgqlc.types.non_null(URI), graphql_name="ssoUrl")
    """The URL endpoint for the identity provider's SAML SSO."""

    issuer = sgqlc.types.Field(String, graphql_name="issuer")
    """The Issuer Entity ID for the SAML identity provider"""

    idp_certificate = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="idpCertificate")
    """The x509 certificate used by the identity provider to sign
    assertions and responses.
    """

    signature_method = sgqlc.types.Field(sgqlc.types.non_null(SamlSignatureAlgorithm), graphql_name="signatureMethod")
    """The signature algorithm used to sign SAML requests for the
    identity provider.
    """

    digest_method = sgqlc.types.Field(sgqlc.types.non_null(SamlDigestAlgorithm), graphql_name="digestMethod")
    """The digest algorithm used to sign SAML requests for the identity
    provider.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class SetOrganizationInteractionLimitInput(sgqlc.types.Input):
    """Autogenerated input type of SetOrganizationInteractionLimit"""

    __schema__ = github_schema
    __field_names__ = ("organization_id", "limit", "expiry", "client_mutation_id")
    organization_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="organizationId")
    """The ID of the organization to set a limit for."""

    limit = sgqlc.types.Field(sgqlc.types.non_null(RepositoryInteractionLimit), graphql_name="limit")
    """The limit to set."""

    expiry = sgqlc.types.Field(RepositoryInteractionLimitExpiry, graphql_name="expiry")
    """When this limit should expire."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class SetRepositoryInteractionLimitInput(sgqlc.types.Input):
    """Autogenerated input type of SetRepositoryInteractionLimit"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "limit", "expiry", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The ID of the repository to set a limit for."""

    limit = sgqlc.types.Field(sgqlc.types.non_null(RepositoryInteractionLimit), graphql_name="limit")
    """The limit to set."""

    expiry = sgqlc.types.Field(RepositoryInteractionLimitExpiry, graphql_name="expiry")
    """When this limit should expire."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class SetUserInteractionLimitInput(sgqlc.types.Input):
    """Autogenerated input type of SetUserInteractionLimit"""

    __schema__ = github_schema
    __field_names__ = ("user_id", "limit", "expiry", "client_mutation_id")
    user_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="userId")
    """The ID of the user to set a limit for."""

    limit = sgqlc.types.Field(sgqlc.types.non_null(RepositoryInteractionLimit), graphql_name="limit")
    """The limit to set."""

    expiry = sgqlc.types.Field(RepositoryInteractionLimitExpiry, graphql_name="expiry")
    """When this limit should expire."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class SponsorOrder(sgqlc.types.Input):
    """Ordering options for connections to get sponsor entities for
    GitHub Sponsors.
    """

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(SponsorOrderField), graphql_name="field")
    """The field to order sponsor entities by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class SponsorableOrder(sgqlc.types.Input):
    """Ordering options for connections to get sponsorable entities for
    GitHub Sponsors.
    """

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(SponsorableOrderField), graphql_name="field")
    """The field to order sponsorable entities by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class SponsorsActivityOrder(sgqlc.types.Input):
    """Ordering options for GitHub Sponsors activity connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(SponsorsActivityOrderField), graphql_name="field")
    """The field to order activity by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class SponsorsTierOrder(sgqlc.types.Input):
    """Ordering options for Sponsors tiers connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(SponsorsTierOrderField), graphql_name="field")
    """The field to order tiers by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class SponsorshipNewsletterOrder(sgqlc.types.Input):
    """Ordering options for sponsorship newsletter connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(SponsorshipNewsletterOrderField), graphql_name="field")
    """The field to order sponsorship newsletters by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class SponsorshipOrder(sgqlc.types.Input):
    """Ordering options for sponsorship connections."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(SponsorshipOrderField), graphql_name="field")
    """The field to order sponsorship by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class StarOrder(sgqlc.types.Input):
    """Ways in which star connections can be ordered."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(StarOrderField), graphql_name="field")
    """The field in which to order nodes by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order nodes."""


class StartRepositoryMigrationInput(sgqlc.types.Input):
    """Autogenerated input type of StartRepositoryMigration"""

    __schema__ = github_schema
    __field_names__ = (
        "source_id",
        "owner_id",
        "source_repository_url",
        "repository_name",
        "continue_on_error",
        "git_archive_url",
        "metadata_archive_url",
        "access_token",
        "github_pat",
        "skip_releases",
        "client_mutation_id",
    )
    source_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="sourceId")
    """The ID of the Octoshift migration source."""

    owner_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="ownerId")
    """The ID of the organization that will own the imported repository."""

    source_repository_url = sgqlc.types.Field(sgqlc.types.non_null(URI), graphql_name="sourceRepositoryUrl")
    """The Octoshift migration source repository URL."""

    repository_name = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="repositoryName")
    """The name of the imported repository."""

    continue_on_error = sgqlc.types.Field(Boolean, graphql_name="continueOnError")
    """Whether to continue the migration on error"""

    git_archive_url = sgqlc.types.Field(String, graphql_name="gitArchiveUrl")
    """The signed URL to access the user-uploaded git archive"""

    metadata_archive_url = sgqlc.types.Field(String, graphql_name="metadataArchiveUrl")
    """The signed URL to access the user-uploaded metadata archive"""

    access_token = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="accessToken")
    """The Octoshift migration source access token."""

    github_pat = sgqlc.types.Field(String, graphql_name="githubPat")
    """The GitHub personal access token of the user importing to the
    target repository.
    """

    skip_releases = sgqlc.types.Field(Boolean, graphql_name="skipReleases")
    """Whether to skip migrating releases for the repository."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class SubmitPullRequestReviewInput(sgqlc.types.Input):
    """Autogenerated input type of SubmitPullRequestReview"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "pull_request_review_id", "event", "body", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(ID, graphql_name="pullRequestId")
    """The Pull Request ID to submit any pending reviews."""

    pull_request_review_id = sgqlc.types.Field(ID, graphql_name="pullRequestReviewId")
    """The Pull Request Review ID to submit."""

    event = sgqlc.types.Field(sgqlc.types.non_null(PullRequestReviewEvent), graphql_name="event")
    """The event to send to the Pull Request Review."""

    body = sgqlc.types.Field(String, graphql_name="body")
    """The text field to set on the Pull Request Review."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class TeamDiscussionCommentOrder(sgqlc.types.Input):
    """Ways in which team discussion comment connections can be ordered."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(TeamDiscussionCommentOrderField), graphql_name="field")
    """The field by which to order nodes."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order nodes."""


class TeamDiscussionOrder(sgqlc.types.Input):
    """Ways in which team discussion connections can be ordered."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(TeamDiscussionOrderField), graphql_name="field")
    """The field by which to order nodes."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order nodes."""


class TeamMemberOrder(sgqlc.types.Input):
    """Ordering options for team member connections"""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(TeamMemberOrderField), graphql_name="field")
    """The field to order team members by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class TeamOrder(sgqlc.types.Input):
    """Ways in which team connections can be ordered."""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(TeamOrderField), graphql_name="field")
    """The field in which to order nodes by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The direction in which to order nodes."""


class TeamRepositoryOrder(sgqlc.types.Input):
    """Ordering options for team repository connections"""

    __schema__ = github_schema
    __field_names__ = ("field", "direction")
    field = sgqlc.types.Field(sgqlc.types.non_null(TeamRepositoryOrderField), graphql_name="field")
    """The field to order repositories by."""

    direction = sgqlc.types.Field(sgqlc.types.non_null(OrderDirection), graphql_name="direction")
    """The ordering direction."""


class TransferIssueInput(sgqlc.types.Input):
    """Autogenerated input type of TransferIssue"""

    __schema__ = github_schema
    __field_names__ = ("issue_id", "repository_id", "client_mutation_id")
    issue_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="issueId")
    """The Node ID of the issue to be transferred"""

    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the repository the issue should be transferred to"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnarchiveRepositoryInput(sgqlc.types.Input):
    """Autogenerated input type of UnarchiveRepository"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The ID of the repository to unarchive."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnfollowOrganizationInput(sgqlc.types.Input):
    """Autogenerated input type of UnfollowOrganization"""

    __schema__ = github_schema
    __field_names__ = ("organization_id", "client_mutation_id")
    organization_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="organizationId")
    """ID of the organization to unfollow."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnfollowUserInput(sgqlc.types.Input):
    """Autogenerated input type of UnfollowUser"""

    __schema__ = github_schema
    __field_names__ = ("user_id", "client_mutation_id")
    user_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="userId")
    """ID of the user to unfollow."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnlinkRepositoryFromProjectInput(sgqlc.types.Input):
    """Autogenerated input type of UnlinkRepositoryFromProject"""

    __schema__ = github_schema
    __field_names__ = ("project_id", "repository_id", "client_mutation_id")
    project_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="projectId")
    """The ID of the Project linked to the Repository."""

    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The ID of the Repository linked to the Project."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnlockLockableInput(sgqlc.types.Input):
    """Autogenerated input type of UnlockLockable"""

    __schema__ = github_schema
    __field_names__ = ("lockable_id", "client_mutation_id")
    lockable_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="lockableId")
    """ID of the item to be unlocked."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnmarkDiscussionCommentAsAnswerInput(sgqlc.types.Input):
    """Autogenerated input type of UnmarkDiscussionCommentAsAnswer"""

    __schema__ = github_schema
    __field_names__ = ("id", "client_mutation_id")
    id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="id")
    """The Node ID of the discussion comment to unmark as an answer."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnmarkFileAsViewedInput(sgqlc.types.Input):
    """Autogenerated input type of UnmarkFileAsViewed"""

    __schema__ = github_schema
    __field_names__ = ("pull_request_id", "path", "client_mutation_id")
    pull_request_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="pullRequestId")
    """The Node ID of the pull request."""

    path = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="path")
    """The path of the file to mark as unviewed"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnmarkIssueAsDuplicateInput(sgqlc.types.Input):
    """Autogenerated input type of UnmarkIssueAsDuplicate"""

    __schema__ = github_schema
    __field_names__ = ("duplicate_id", "canonical_id", "client_mutation_id")
    duplicate_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="duplicateId")
    """ID of the issue or pull request currently marked as a duplicate."""

    canonical_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="canonicalId")
    """ID of the issue or pull request currently considered
    canonical/authoritative/original.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnminimizeCommentInput(sgqlc.types.Input):
    """Autogenerated input type of UnminimizeComment"""

    __schema__ = github_schema
    __field_names__ = ("subject_id", "client_mutation_id")
    subject_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="subjectId")
    """The Node ID of the subject to modify."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnpinIssueInput(sgqlc.types.Input):
    """Autogenerated input type of UnpinIssue"""

    __schema__ = github_schema
    __field_names__ = ("issue_id", "client_mutation_id")
    issue_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="issueId")
    """The ID of the issue to be unpinned"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UnresolveReviewThreadInput(sgqlc.types.Input):
    """Autogenerated input type of UnresolveReviewThread"""

    __schema__ = github_schema
    __field_names__ = ("thread_id", "client_mutation_id")
    thread_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="threadId")
    """The ID of the thread to unresolve"""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateBranchProtectionRuleInput(sgqlc.types.Input):
    """Autogenerated input type of UpdateBranchProtectionRule"""

    __schema__ = github_schema
    __field_names__ = (
        "branch_protection_rule_id",
        "pattern",
        "requires_approving_reviews",
        "required_approving_review_count",
        "requires_commit_signatures",
        "requires_linear_history",
        "blocks_creations",
        "allows_force_pushes",
        "allows_deletions",
        "is_admin_enforced",
        "requires_status_checks",
        "requires_strict_status_checks",
        "requires_code_owner_reviews",
        "dismisses_stale_reviews",
        "restricts_review_dismissals",
        "review_dismissal_actor_ids",
        "bypass_pull_request_actor_ids",
        "bypass_force_push_actor_ids",
        "restricts_pushes",
        "push_actor_ids",
        "required_status_check_contexts",
        "required_status_checks",
        "requires_conversation_resolution",
        "client_mutation_id",
    )
    branch_protection_rule_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="branchProtectionRuleId")
    """The global relay id of the branch protection rule to be updated."""

    pattern = sgqlc.types.Field(String, graphql_name="pattern")
    """The glob-like pattern used to determine matching branches."""

    requires_approving_reviews = sgqlc.types.Field(Boolean, graphql_name="requiresApprovingReviews")
    """Are approving reviews required to update matching branches."""

    required_approving_review_count = sgqlc.types.Field(Int, graphql_name="requiredApprovingReviewCount")
    """Number of approving reviews required to update matching branches."""

    requires_commit_signatures = sgqlc.types.Field(Boolean, graphql_name="requiresCommitSignatures")
    """Are commits required to be signed."""

    requires_linear_history = sgqlc.types.Field(Boolean, graphql_name="requiresLinearHistory")
    """Are merge commits prohibited from being pushed to this branch."""

    blocks_creations = sgqlc.types.Field(Boolean, graphql_name="blocksCreations")
    """Is branch creation a protected operation."""

    allows_force_pushes = sgqlc.types.Field(Boolean, graphql_name="allowsForcePushes")
    """Are force pushes allowed on this branch."""

    allows_deletions = sgqlc.types.Field(Boolean, graphql_name="allowsDeletions")
    """Can this branch be deleted."""

    is_admin_enforced = sgqlc.types.Field(Boolean, graphql_name="isAdminEnforced")
    """Can admins overwrite branch protection."""

    requires_status_checks = sgqlc.types.Field(Boolean, graphql_name="requiresStatusChecks")
    """Are status checks required to update matching branches."""

    requires_strict_status_checks = sgqlc.types.Field(Boolean, graphql_name="requiresStrictStatusChecks")
    """Are branches required to be up to date before merging."""

    requires_code_owner_reviews = sgqlc.types.Field(Boolean, graphql_name="requiresCodeOwnerReviews")
    """Are reviews from code owners required to update matching branches."""

    dismisses_stale_reviews = sgqlc.types.Field(Boolean, graphql_name="dismissesStaleReviews")
    """Will new commits pushed to matching branches dismiss pull request
    review approvals.
    """

    restricts_review_dismissals = sgqlc.types.Field(Boolean, graphql_name="restrictsReviewDismissals")
    """Is dismissal of pull request reviews restricted."""

    review_dismissal_actor_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="reviewDismissalActorIds")
    """A list of User, Team, or App IDs allowed to dismiss reviews on
    pull requests targeting matching branches.
    """

    bypass_pull_request_actor_ids = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="bypassPullRequestActorIds"
    )
    """A list of User, Team, or App IDs allowed to bypass pull requests
    targeting matching branches.
    """

    bypass_force_push_actor_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="bypassForcePushActorIds")
    """A list of User, Team, or App IDs allowed to bypass force push
    targeting matching branches.
    """

    restricts_pushes = sgqlc.types.Field(Boolean, graphql_name="restrictsPushes")
    """Is pushing to matching branches restricted."""

    push_actor_ids = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(ID)), graphql_name="pushActorIds")
    """A list of User, Team, or App IDs allowed to push to matching
    branches.
    """

    required_status_check_contexts = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(String)), graphql_name="requiredStatusCheckContexts"
    )
    """List of required status check contexts that must pass for commits
    to be accepted to matching branches.
    """

    required_status_checks = sgqlc.types.Field(
        sgqlc.types.list_of(sgqlc.types.non_null(RequiredStatusCheckInput)), graphql_name="requiredStatusChecks"
    )
    """The list of required status checks"""

    requires_conversation_resolution = sgqlc.types.Field(Boolean, graphql_name="requiresConversationResolution")
    """Are conversations required to be resolved before merging."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateCheckRunInput(sgqlc.types.Input):
    """Autogenerated input type of UpdateCheckRun"""

    __schema__ = github_schema
    __field_names__ = (
        "repository_id",
        "check_run_id",
        "name",
        "details_url",
        "external_id",
        "status",
        "started_at",
        "conclusion",
        "completed_at",
        "output",
        "actions",
        "client_mutation_id",
    )
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The node ID of the repository."""

    check_run_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="checkRunId")
    """The node of the check."""

    name = sgqlc.types.Field(String, graphql_name="name")
    """The name of the check."""

    details_url = sgqlc.types.Field(URI, graphql_name="detailsUrl")
    """The URL of the integrator's site that has the full details of the
    check.
    """

    external_id = sgqlc.types.Field(String, graphql_name="externalId")
    """A reference for the run on the integrator's system."""

    status = sgqlc.types.Field(RequestableCheckStatusState, graphql_name="status")
    """The current status."""

    started_at = sgqlc.types.Field(DateTime, graphql_name="startedAt")
    """The time that the check run began."""

    conclusion = sgqlc.types.Field(CheckConclusionState, graphql_name="conclusion")
    """The final conclusion of the check."""

    completed_at = sgqlc.types.Field(DateTime, graphql_name="completedAt")
    """The time that the check run finished."""

    output = sgqlc.types.Field(CheckRunOutput, graphql_name="output")
    """Descriptive details about the run."""

    actions = sgqlc.types.Field(sgqlc.types.list_of(sgqlc.types.non_null(CheckRunAction)), graphql_name="actions")
    """Possible further actions the integrator can perform, which a user
    may trigger.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateCheckSuitePreferencesInput(sgqlc.types.Input):
    """Autogenerated input type of UpdateCheckSuitePreferences"""

    __schema__ = github_schema
    __field_names__ = ("repository_id", "auto_trigger_preferences", "client_mutation_id")
    repository_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="repositoryId")
    """The Node ID of the repository."""

    auto_trigger_preferences = sgqlc.types.Field(
        sgqlc.types.non_null(sgqlc.types.list_of(sgqlc.types.non_null(CheckSuiteAutoTriggerPreference))),
        graphql_name="autoTriggerPreferences",
    )
    """The check suite preferences to modify."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateDiscussionCommentInput(sgqlc.types.Input):
    """Autogenerated input type of UpdateDiscussionComment"""

    __schema__ = github_schema
    __field_names__ = ("comment_id", "body", "client_mutation_id")
    comment_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="commentId")
    """The Node ID of the discussion comment to update."""

    body = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="body")
    """The new contents of the comment body."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateDiscussionInput(sgqlc.types.Input):
    """Autogenerated input type of UpdateDiscussion"""

    __schema__ = github_schema
    __field_names__ = ("discussion_id", "title", "body", "category_id", "client_mutation_id")
    discussion_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="discussionId")
    """The Node ID of the discussion to update."""

    title = sgqlc.types.Field(String, graphql_name="title")
    """The new discussion title."""

    body = sgqlc.types.Field(String, graphql_name="body")
    """The new contents of the discussion body."""

    category_id = sgqlc.types.Field(ID, graphql_name="categoryId")
    """The Node ID of a discussion category within the same repository to
    change this discussion to.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseAdministratorRoleInput(sgqlc.types.Input):
    """Autogenerated input type of UpdateEnterpriseAdministratorRole"""

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "login", "role", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the Enterprise which the admin belongs to."""

    login = sgqlc.types.Field(sgqlc.types.non_null(String), graphql_name="login")
    """The login of a administrator whose role is being changed."""

    role = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseAdministratorRole), graphql_name="role")
    """The new role for the Enterprise administrator."""

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseAllowPrivateRepositoryForkingSettingInput(sgqlc.types.Input):
    """Autogenerated input type of
    UpdateEnterpriseAllowPrivateRepositoryForkingSetting
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "setting_value", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set the allow private
    repository forking setting.
    """

    setting_value = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseEnabledDisabledSettingValue), graphql_name="settingValue")
    """The value for the allow private repository forking setting on the
    enterprise.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseDefaultRepositoryPermissionSettingInput(sgqlc.types.Input):
    """Autogenerated input type of
    UpdateEnterpriseDefaultRepositoryPermissionSetting
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "setting_value", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set the base repository
    permission setting.
    """

    setting_value = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseDefaultRepositoryPermissionSettingValue), graphql_name="settingValue")
    """The value for the base repository permission setting on the
    enterprise.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseMembersCanChangeRepositoryVisibilitySettingInput(sgqlc.types.Input):
    """Autogenerated input type of
    UpdateEnterpriseMembersCanChangeRepositoryVisibilitySetting
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "setting_value", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set the members can change
    repository visibility setting.
    """

    setting_value = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseEnabledDisabledSettingValue), graphql_name="settingValue")
    """The value for the members can change repository visibility setting
    on the enterprise.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseMembersCanCreateRepositoriesSettingInput(sgqlc.types.Input):
    """Autogenerated input type of
    UpdateEnterpriseMembersCanCreateRepositoriesSetting
    """

    __schema__ = github_schema
    __field_names__ = (
        "enterprise_id",
        "setting_value",
        "members_can_create_repositories_policy_enabled",
        "members_can_create_public_repositories",
        "members_can_create_private_repositories",
        "members_can_create_internal_repositories",
        "client_mutation_id",
    )
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set the members can create
    repositories setting.
    """

    setting_value = sgqlc.types.Field(EnterpriseMembersCanCreateRepositoriesSettingValue, graphql_name="settingValue")
    """Value for the members can create repositories setting on the
    enterprise. This or the granular public/private/internal allowed
    fields (but not both) must be provided.
    """

    members_can_create_repositories_policy_enabled = sgqlc.types.Field(Boolean, graphql_name="membersCanCreateRepositoriesPolicyEnabled")
    """When false, allow member organizations to set their own repository
    creation member privileges.
    """

    members_can_create_public_repositories = sgqlc.types.Field(Boolean, graphql_name="membersCanCreatePublicRepositories")
    """Allow members to create public repositories. Defaults to current
    value.
    """

    members_can_create_private_repositories = sgqlc.types.Field(Boolean, graphql_name="membersCanCreatePrivateRepositories")
    """Allow members to create private repositories. Defaults to current
    value.
    """

    members_can_create_internal_repositories = sgqlc.types.Field(Boolean, graphql_name="membersCanCreateInternalRepositories")
    """Allow members to create internal repositories. Defaults to current
    value.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseMembersCanDeleteIssuesSettingInput(sgqlc.types.Input):
    """Autogenerated input type of
    UpdateEnterpriseMembersCanDeleteIssuesSetting
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "setting_value", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set the members can delete
    issues setting.
    """

    setting_value = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseEnabledDisabledSettingValue), graphql_name="settingValue")
    """The value for the members can delete issues setting on the
    enterprise.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseMembersCanDeleteRepositoriesSettingInput(sgqlc.types.Input):
    """Autogenerated input type of
    UpdateEnterpriseMembersCanDeleteRepositoriesSetting
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "setting_value", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set the members can delete
    repositories setting.
    """

    setting_value = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseEnabledDisabledSettingValue), graphql_name="settingValue")
    """The value for the members can delete repositories setting on the
    enterprise.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseMembersCanInviteCollaboratorsSettingInput(sgqlc.types.Input):
    """Autogenerated input type of
    UpdateEnterpriseMembersCanInviteCollaboratorsSetting
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "setting_value", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set the members can invite
    collaborators setting.
    """

    setting_value = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseEnabledDisabledSettingValue), graphql_name="settingValue")
    """The value for the members can invite collaborators setting on the
    enterprise.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseMembersCanMakePurchasesSettingInput(sgqlc.types.Input):
    """Autogenerated input type of
    UpdateEnterpriseMembersCanMakePurchasesSetting
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "setting_value", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set the members can make
    purchases setting.
    """

    setting_value = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseMembersCanMakePurchasesSettingValue), graphql_name="settingValue")
    """The value for the members can make purchases setting on the
    enterprise.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseMembersCanUpdateProtectedBranchesSettingInput(sgqlc.types.Input):
    """Autogenerated input type of
    UpdateEnterpriseMembersCanUpdateProtectedBranchesSetting
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "setting_value", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set the members can update
    protected branches setting.
    """

    setting_value = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseEnabledDisabledSettingValue), graphql_name="settingValue")
    """The value for the members can update protected branches setting on
    the enterprise.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier for the client performing the mutation."""


class UpdateEnterpriseMembersCanViewDependencyInsightsSettingInput(sgqlc.types.Input):
    """Autogenerated input type of
    UpdateEnterpriseMembersCanViewDependencyInsightsSetting
    """

    __schema__ = github_schema
    __field_names__ = ("enterprise_id", "setting_value", "client_mutation_id")
    enterprise_id = sgqlc.types.Field(sgqlc.types.non_null(ID), graphql_name="enterpriseId")
    """The ID of the enterprise on which to set the members can view
    dependency insights setting.
    """

    setting_value = sgqlc.types.Field(sgqlc.types.non_null(EnterpriseEnabledDisabledSettingValue), graphql_name="settingValue")
    """The value for the members can view dependency insights setting on
    the enterprise.
    """

    client_mutation_id = sgqlc.types.Field(String, graphql_name="clientMutationId")
    """A unique identifier f