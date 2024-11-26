############################ Copyrights and license ############################
#                                                                              #
# Copyright 2012 Steve English <steve.english@navetas.com>                     #
# Copyright 2012 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2012 Zearin <zearin@gonk.net>                                      #
# Copyright 2013 AKFish <akfish@gmail.com>                                     #
# Copyright 2013 Cameron White <cawhite@pdx.edu>                               #
# Copyright 2013 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2013 poulp <mathieu.nerv@gmail.com>                                #
# Copyright 2014 Tomas Radej <tradej@redhat.com>                               #
# Copyright 2014 Vincent Jacques <vincent@vincent-jacques.net>                 #
# Copyright 2016 E. Dunham <github@edunham.net>                                #
# Copyright 2016 Jannis Gebauer <ja.geb@me.com>                                #
# Copyright 2016 Peter Buckley <dx-pbuckley@users.noreply.github.com>          #
# Copyright 2017 Balázs Rostás <rostas.balazs@gmail.com>                       #
# Copyright 2017 Jannis Gebauer <ja.geb@me.com>                                #
# Copyright 2017 Simon <spam@esemi.ru>                                         #
# Copyright 2018 Wan Liuyang <tsfdye@gmail.com>                                #
# Copyright 2018 bryanhuntesl <31992054+bryanhuntesl@users.noreply.github.com> #
# Copyright 2018 sfdye <tsfdye@gmail.com>                                      #
# Copyright 2018 itsbruce <it.is.bruce@gmail.com>                              #
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


class Membership(github.GithubObject.CompletableGithubObject):
    """
    This class represents Membership of an organization. The reference can be found here https://docs.github.com/en/rest/reference/orgs
    """

    def __repr__(self):
        return self.get__repr__({"url": self._url.value})

    @property
    def url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._url)
        return self._url.value

    @property
    def state(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._state)
        return self._state.value

    @property
    def role(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._role)
        return self._role.value

    @property
    def organization_url(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._organization_url)
        return self._organization_url.value

    @property
    def organization(self):
        """
        :type: :class:`github.Organization.Organization`
        """
        self._completeIfNotSet(self._organization)
        return self._organization.value

    @property
    def user(self):
        """
        :type: :class:`github.NamedUser.NamedUser`
        """
        self._completeIfNotSet(self._user)
        return self._user.value

    def _initAttributes(self):
        self._url = github.GithubObject.NotSet
        self._state = github.GithubObject.NotSet
        self._role = github.GithubObject.NotSet
        self._organization_url = github.GithubObject.NotSet
        self._organization = github.GithubObject.NotSet
        self._user = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "url" in attributes:  # pragma no branch
            self._url = self._makeStringAttribute(attributes["url"])
        if "state" in attributes:  # pragma no branch
            self._state = self._makeStringAttribute(attributes["state"])
        if "role" in attributes:  # pragma no branch
            self._role = self._makeStringAttribute(attributes["role"])
        if "organization_url" in attributes:  # pragma no branch
            self._organization_url = self._makeStringAttribute(
                attributes["organization_url"]
            )
        if "organization" in attributes:  # pragma no branch
            self._organization = self._makeClassAttribute(
                github.Organization.Organization, attributes["organization"]
            )
        if "user" in attributes:  # pragma no branch
            self._user = self._makeClassAttribute(
                github.NamedUser.NamedUser, attributes["user"]
            )
