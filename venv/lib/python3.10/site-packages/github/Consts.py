############################ Copyrights and license ############################
#                                                                              #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2016 Jakub Wilk <jwilk@jwilk.net>                                  #
# Copyright 2016 Peter Buckley <dx-pbuckley@users.noreply.github.com>          #
# Copyright 2018 Maarten Fonville <mfonville@users.noreply.github.com>         #
# Copyright 2018 Wan Liuyang <tsfdye@gmail.com>                                #
# Copyright 2018 sfdye <tsfdye@gmail.com>                                      #
# Copyright 2019 Nick Campbell <nicholas.j.campbell@gmail.com>                 #
# Copyright 2020 Pascal Hofmann <mail@pascalhofmann.de>                        #
#                                                                              #
# This file is part of PyGithub.                                               #
# http://pygithub.readthedocs.io/                                              #
#                                                                              #
# PyGithub is free software: you can redistribute it and/or modify it under    #
# the terms of the GNU Lesser General Public License as published by the Free  #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# PyGithub is distributed in the hope that it will be useful, but WITHOUT ANY  #
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS    #
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more #
# details.                                                                     #
#                                                                              #
# You should have received a copy of the GNU Lesser General Public License     #
# along with PyGithub. If not, see <http://www.gnu.org/licenses/>.             #
#                                                                              #
################################################################################


REQ_IF_NONE_MATCH = "If-None-Match"
REQ_IF_MODIFIED_SINCE = "If-Modified-Since"
PROCESSING_202_WAIT_TIME = 2

# ##############################################################################
# Response Header                                                              #
# (Lower Case)                                                                 #
# ##############################################################################
RES_ETAG = "etag"
RES_LAST_MODIFIED = "last-modified"

# Inspired by https://github.com/google/go-github

# Headers

headerRateLimit = "x-ratelimit-limit"
headerRateRemaining = "x-ratelimit-remaining"
headerRateReset = "x-ratelimit-reset"
headerOAuthScopes = "x-oauth-scopes"
headerOTP = "x-github-otp"

defaultMediaType = "application/octet-stream"

# Custom media type for preview API

# https://developer.github.com/changes/2014-12-09-new-attributes-for-stars-api/
mediaTypeStarringPreview = "application/vnd.github.v3.star+json"

# https://developer.github.com/changes/2016-02-19-source-import-preview-api/
mediaTypeImportPreview = "application/vnd.github.barred-rock-preview"

# https://developer.github.com/changes/2016-05-12-reactions-api-preview/
mediaTypeReactionsPreview = "application/vnd.github.squirrel-girl-preview"

# https://developer.github.com/changes/2016-09-14-Integrations-Early-Access/
mediaTypeIntegrationPreview = "application/vnd.github.machine-man-preview+json"

# https://developer.github.com/changes/2016-09-14-projects-api/
mediaTypeProjectsPreview = "application/vnd.github.inertia-preview+json"

# https://developer.github.com/changes/2017-01-05-commit-search-api/
mediaTypeCommitSearchPreview = "application/vnd.github.cloak-preview"

# https://developer.github.com/changes/2017-02-28-user-blocking-apis-and-webhook/
mediaTypeBlockUsersPreview = "application/vnd.github.giant-sentry-fist-preview+json"

# https://developer.github.com/changes/2017-07-17-update-topics-on-repositories/
mediaTypeTopicsPreview = "application/vnd.github.mercy-preview+json"

# https://developer.github.com/changes/2018-02-22-label-description-search-preview/
mediaTypeLabelDescriptionSearchPreview = "application/vnd.github.symmetra-preview+json"

# https://developer.github.com/changes/2018-01-10-lock-reason-api-preview/
mediaTypeLockReasonPreview = "application/vnd.github.sailor-v-preview+json"

# https://developer.github.com/changes/2018-01-25-organization-invitation-api-preview/
mediaTypeOrganizationInvitationPreview = "application/vnd.github.dazzler-preview+json"

# https://developer.github.com/changes/2018-02-07-team-discussions-api
mediaTypeTeamDiscussionsPreview = "application/vnd.github.echo-preview+json"

# https://developer.github.com/changes/2018-03-16-protected-branches-required-approving-reviews/
mediaTypeRequireMultipleApprovingReviews = (
    "application/vnd.github.luke-cage-preview+json"
)

# https://developer.github.com/changes/2018-05-24-user-migration-api/
mediaTypeMigrationPreview = "application/vnd.github.wyandotte-preview+json"

# https://developer.github.com/changes/2019-07-16-repository-templates-api/
mediaTypeTemplatesPreview = "application/vnd.github.baptiste-preview+json"

# https://docs.github.com/en/rest/reference/search#highlighting-code-search-results-1
highLightSearchPreview = "application/vnd.github.v3.text-match+json"

# https://developer.github.com/changes/2018-02-22-protected-branches-required-signatures/
signaturesProtectedBranchesPreview = "application/vnd.github.zzzax-preview+json"

# https://developer.github.com/changes/2019-04-24-vulnerability-alerts/
vulnerabilityAlertsPreview = "application/vnd.github.dorian-preview+json"

# https://developer.github.com/changes/2019-06-04-automated-security-fixes/
automatedSecurityFixes = "application/vnd.github.london-preview+json"

# https://developer.github.com/changes/2019-05-29-update-branch-api/
updateBranchPreview = "application/vnd.github.lydian-preview+json"

# https://developer.github.com/changes/2016-05-23-timeline-preview-api/
issueTimelineEventsPreview = "application/vnd.github.mockingbird-preview"

# https://docs.github.com/en/rest/reference/teams#check-if-a-team-manages-a-repository
teamRepositoryPermissions = "application/vnd.github.v3.repository+json"

# https://developer.github.com/changes/2016-04-06-deployment-and-deployment-status-enhancements/
deploymentEnhancementsPreview = "application/vnd.github.ant-man-preview+json"

# https://developer.github.com/changes/2018-10-16-deployments-environments-states-and-auto-inactive-updates/
deploymentStatusEnhancementsPreview = "application/vnd.github.flash-preview+json"

# https://developer.github.com/changes/2019-12-03-internal-visibility-changes/
repoVisibilityPreview = "application/vnd.github.nebula-preview+json"

DEFAULT_BASE_URL = "https://api.github.com"
DEFAULT_STATUS_URL = "https://status.github.com"
DEFAULT_USER_AGENT = "PyGithub/Python"
# As of 2018-05-17, Github imposes a 10s limit for completion of API requests.
# Thus, the timeout should be slightly > 10s to account for network/front-end
# latency.
DEFAULT_TIMEOUT = 15
DEFAULT_PER_PAGE = 30

# JWT expiry in seconds. Could be set for max 600 seconds (10 minutes).
# https://docs.github.com/en/developers/apps/building-github-apps/authenticating-with-github-apps#authenticating-as-a-github-app
DEFAULT_JWT_EXPIRY = 300
MIN_JWT_EXPIRY = 15
MAX_JWT_EXPIRY = 600
# https://docs.github.com/en/developers/apps/building-github-apps/authenticating-with-github-apps#generating-a-json-web-token-jwt
# "The time the JWT was created. To protect against clock drift, we recommend you set this 60 seconds in the past."
DEFAULT_JWT_ISSUED_AT = -60
# https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-json-web-token-jwt-for-a-github-app
# "Your JWT must be signed using the RS256 algorithm"
DEFAULT_JWT_ALGORITHM = "RS256"
