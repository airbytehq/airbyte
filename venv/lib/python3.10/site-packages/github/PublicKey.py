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

# https://docs.github.com/en/rest/reference/actions#example-encrypting-a-secret-using-python
from base64 import b64encode

from nacl import encoding, public

import github.GithubObject


def encrypt(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


class PublicKey(github.GithubObject.CompletableGithubObject):
    """
    This class represents either an organization public key or a repository public key.
    The reference can be found here https://docs.github.com/en/rest/reference/actions#get-an-organization-public-key
    or here https://docs.github.com/en/rest/reference/actions#get-a-repository-public-key
    """

    def __repr__(self):
        return self.get__repr__({"key_id": self._key_id.value, "key": self._key.value})

    @property
    def key(self):
        """
        :type: string
        """
        self._completeIfNotSet(self._key)
        return self._key.value

    @property
    def key_id(self):
        """
        :type: string or int
        """
        self._completeIfNotSet(self._key_id)
        return self._key_id.value

    def _initAttributes(self):
        self._key = github.GithubObject.NotSet
        self._key_id = github.GithubObject.NotSet

    def _useAttributes(self, attributes):
        if "key" in attributes:  # pragma no branch
            self._key = self._makeStringAttribute(attributes["key"])
        if "key_id" in attributes:  # pragma no branch
            if type(attributes["key_id"]) == str:
                self._key_id = self._makeStringAttribute(attributes["key_id"])
            else:
                self._key_id = self._makeIntAttribute(attributes["key_id"])

    def encrypt(self, unencrypted_value):
        return encrypt(self._key.value, unencrypted_value)
