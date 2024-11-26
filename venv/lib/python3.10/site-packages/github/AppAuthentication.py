############################ Copyrights and license ############################
#                                                                              #
# Copyright 2023 Denis Blanchette <denisblanchette@gmail.com>                  #
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


from typing import Dict, Optional, Union

import deprecated

from github.Auth import AppAuth, AppInstallationAuth


@deprecated.deprecated("Use github.Auth.AppInstallationAuth instead")
class AppAuthentication(AppInstallationAuth):
    def __init__(
        self,
        app_id: Union[int, str],
        private_key: str,
        installation_id: int,
        token_permissions: Optional[Dict[str, str]] = None,
    ):
        super().__init__(
            app_auth=AppAuth(app_id, private_key),
            installation_id=installation_id,
            token_permissions=token_permissions,
        )
