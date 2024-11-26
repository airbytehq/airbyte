############################ Copyrights and license ############################
#                                                                              #
# Copyright 2022 Eric Nieuwland <eric.nieuwland@gmail.com>                     #
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

from typing import Any, Dict
from datetime import datetime

import github.GithubObject
import github.PaginatedList
import github.CodeScanRule
import github.CodeScanTool
import github.CodeScanAlertInstance

class CodeScanAlert(github.GithubObject.NonCompletableGithubObject):
    def __repr__(self) -> str: ...
    @property
    def number(self) -> int: ...
    @property
    def rule(self) -> github.CodeScanRule.CodeScanRule: ...
    @property
    def tool(self) -> github.CodeScanTool.CodeScanTool: ...
    @property
    def created_at(self) -> datetime: ...
    @property
    def dismissed_at(self) -> datetime: ...
    @property
    def dismissed_by(self) -> dict: ...
    @property
    def dismissed_reason(self) -> str: ...
    @property
    def url(self) -> str: ...
    @property
    def html_url(self) -> str: ...
    @property
    def instances_url(self) -> str: ...
    @property
    def most_recent_instance(
        self,
    ) -> github.CodeScanAlertInstance.CodeScanAlertInstance: ...
    @property
    def state(self) -> str: ...
    def get_instances(self) -> github.PaginatedList.PaginatedList: ...
    def _initAttributes(self) -> None: ...
    def _useAttributes(self, attributes: Dict[str, Any]) -> None: ...
