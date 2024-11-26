############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2016 Peter Buckley <dx-pbuckley@users.noreply.github.com>          #
# Copyright 2018 Wan Liuyang <tsfdye@gmail.com>                                #
# Copyright 2018 sfdye <tsfdye@gmail.com>                                      #
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

import github.GithubObject


class InputGitTreeElement:
    """
    This class represents InputGitTreeElements
    """

    def __init__(
        self,
        path,
        mode,
        type,
        content=github.GithubObject.NotSet,
        sha=github.GithubObject.NotSet,
    ):
        """
        :param path: string
        :param mode: string
        :param type: string
        :param content: string
        :param sha: string or None
        """

        assert isinstance(path, str), path
        assert isinstance(mode, str), mode
        assert isinstance(type, str), type
        assert content is github.GithubObject.NotSet or isinstance(
            content, str
        ), content
        assert (
            sha is github.GithubObject.NotSet or sha is None or isinstance(sha, str)
        ), sha
        self.__path = path
        self.__mode = mode
        self.__type = type
        self.__content = content
        self.__sha = sha

    @property
    def _identity(self):
        identity = {
            "path": self.__path,
            "mode": self.__mode,
            "type": self.__type,
        }
        if self.__sha is not github.GithubObject.NotSet:
            identity["sha"] = self.__sha
        if self.__content is not github.GithubObject.NotSet:
            identity["content"] = self.__content
        return identity
