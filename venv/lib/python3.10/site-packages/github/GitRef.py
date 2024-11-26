############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2016 Jannis Gebauer <ja.geb@me.com>                                #
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
import github.GitObject


class GitRef(github.GithubObject.CompletableGithubObject):
    """
    This class represents GitRefs. The reference can be found here https://docs.github.com/en/rest/reference/git#references
    """

    def __repr__(self):
        return self.get__repr__({"ref": self._ref.value})

    @property
    def object(self):
        """
        :type: :class:`github.GitObject.GitObject`
        """
        self._completeIfNotSet(self._object)
        return self._object.value

    @property
    def ref(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._ref)
        return self._ref.value

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    def delete(self):
        """
        :calls: `DELETE /repos/{owner}/{repo}/git/refs/{ref} <https://docs.github.com/en/rest/reference/git#references>`_
        :rtype: None
        """
        headers, data = self._requester.requestJsonAndCheck("DELETE", self.url)

    def edit(self, sha, force=github.GithubObject.NotSet):
        """
        :calls: `PATCH /repos/{owner}/{repo}/git/refs/{ref} <https://docs.github.com/en/rest/reference/git#references>`_
        :param sha: string
        :param force: bool
        :rtype: None
        """
        assert isinstance(sha, str), sha
        assert force is github.GithubObject.NotSet or isinstance(force, bool), force
        post_parameters = {
            "sha": sha,
        }
        if force is not github.GithubObject.NotSet:
            post_parameters["force"] = force
        headers, data = self._requester.requestJsonAndCheck(
            "PATCH", self.url, input=post_parameters
        )
        self._useAttributes(data)

    def _initAttributes(self):
        self._object = github.GithubObject.NotSet
        self._ref = github.GithubObject.NotSet
        self._url = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "object" in attributes:  # pragma no branch
            self._object = self._makeClassAttribute(
                github.GitObject.GitObject, attributes["object"]
            )
        if "ref" in attributes:  # pragma no branch
            self._ref = self._makeStringAttribute(attributes["ref"])
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
