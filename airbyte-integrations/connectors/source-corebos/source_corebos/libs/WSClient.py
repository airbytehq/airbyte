# -*- coding: utf-8 -*-
'''
Copyright (c) 2015, David Fernández González, All rights reserved.

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library.
'''

import urllib.request
import urllib.parse
import hashlib
import json
import re

__author__ = 'David Fernández González'
__license__ = 'LGPL'
__version__ = '0.1.2'
__maintainer__ = 'David Fernández González'
__email__ = 'dfernandez.parking@gmail.com'
__status__ = 'Development'
__credits__ = []


def md5sum(s):
    m = hashlib.md5(str(s).encode('utf-8'))
    return m.hexdigest()


class WebserviceException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return "VtigerWebserviceException(%s, %s)" % (self.code, self.message)


def exception(response):
    result = response['error']
    return WebserviceException(result['code'], result['message'])


class WSClient:
    """
    Connect to a vtiger instance.
    """

    def __init__(self, service_url):
        """
        @param service_url:
        """
        self.__servicebase = 'webservice.php'
        self.__service_url = self.get_webservice_url(service_url)

        self.__serviceuser = ''
        self.__servicekey = ''

        self.__servertime = 0
        self.__expiretime = 0
        self.__servicetoken = 0

        self.__sessionid = False
        self.__userid = False

    def __do_get(self, **params):
        """
        @param params:
        @return:
        """
        param_string = urllib.parse.urlencode(params)
        response = urllib.request.urlopen('%s?%s' % (self.__service_url, param_string))
        content = response.read()
        return json.loads(content.decode("utf8"))

    def __do_post(self, **parameters):
        """
        @param params:
        @return:
        """
        data = urllib.parse.urlencode(parameters)
        response = urllib.request.urlopen(self.__service_url, data.encode('utf-8'))
        content = response.read()
        return json.loads(content.decode("utf8"))

    # Get the URL for sending webservice request.
    def get_webservice_url(self, url):
        """
        @param url:
        @return:
        """
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)

        if len(url) >= 1:
            url = url[0]
            if str(url).find(self.__servicebase) < 0:
                if str(url[len(url) - 1:]) != '/':
                    url += str('/')
                url += self.__servicebase
        else:
            raise Exception('Invalid URL')

        return url

    def get(self, operation, **parameters):
        """
        @param operation:
        @param parameters:
        @return: @raise exception:
        """
        response = self.__do_get(
            operation=operation,
            sessionName=self.__sessionid,
            **parameters
        )

        if response['success']:
            return response['result']
        else:
            raise exception(response)

    def post(self, operation, **parameters):
        """
        @param operation:
        @param parameters:
        @return: @raise exception:
        """
        response = self.__do_post(
            operation=operation,
            sessionName=self.__sessionid,
            **parameters)

        if response['success']:
            return response['result']
        else:
            raise exception(response)

    # Check and perform login if requried.
    def __check_login(self):
        if self.__sessionid != 0:
            return True
        else:
            return False

    # Perform the challenge
    def __do_challenge(self, user_name):
        """
        @return: @raise exception:
        """
        response = self.__do_get(
            operation='getchallenge',
            username=user_name
        )

        if response['success']:
            self.__servicetoken = response['result']['token']
            self.__servertime = response['result']['serverTime']
            self.__expiretime = response['result']['expireTime']
            return True
        else:
            raise exception(response)

    # Do Login Operation
    def do_login(self, user_name, user_accesskey, withpassword=False):
        """
        @param user_name:
        @param user_accesskey:
        @return:
        """
        if not self.__do_challenge(user_name):
            return False

        response = self.__do_post(
            operation='login',
            username=user_name,
            accessKey=self.__servicetoken + user_accesskey if withpassword else md5sum(
                self.__servicetoken + user_accesskey)
        )

        if response['success']:
            self.__sessionid = response['result']['sessionName']
            self.__userid = response['result']['userId']
            self.__serviceuser = user_name
            self.__servicekey = user_accesskey
            return True
        else:
            raise exception(response)

    def logout(self):
        if self.__sessionid != 0:
            self.post('logout')

    # List types available Modules.
    @property
    def do_listtypes(self):
        if not self.__check_login():
            raise Exception('Login error')

        return self.get('listtypes')

    # Describe Module Fields.
    def do_describe(self, name):
        """
        @param name:
        @return:
        """
        if not self.__check_login():
            raise Exception('Login error')

        return self.get(
            'describe',
            elementType=name
        )

    # Do Create Operation
    def do_create(self, entity, params):
        """
        @param entity:
        @param params:
        @return:
        """
        if not self.__check_login():
            raise Exception('Login error')

        json_data = json.dumps(params)
        return self.post(
            'create',
            elementType=entity,
            element=json_data
        )

    # Retrieve details of record.
    def do_retrieve(self, id):
        """
        @param id:
        @return:
        """
        if not self.__check_login():
            raise Exception('Login error')

        return self.get(
            'retrieve',
            id=id
        )

    # Do Update Operation
    def do_update(self, params):
        """
        @param params:
        @return:
        """
        if not self.__check_login():
            raise Exception('Login error')

        json_data = json.dumps(params)
        return self.post(
            'update',
            element=json_data
        )

    #Do Delete Operation
    def do_delete(self, id):
        """
        @param id:
        @return:
        """
        if not self.__check_login():
            raise Exception('Login error')

        return self.post(
            'delete',
            id=id
        )

    #Do Query Operation
    def do_query(self, query):
        """
        @param query:
        @return:
        """
        if not self.__check_login():
            raise Exception('Login error')

        return self.get(
            'query',
            query=query
        )

    #Invoke custom operation
    def do_invoke(self, metod, params, metod_type='POST'):
        """
        @param metod:
        @param params:
        @param metod_type:
        @return:
        """
        if not self.__check_login():
            raise Exception('Login error')

        if metod_type.upper() == 'POST':
            response = self.post(metod, **params)
        else:
            response = self.get(metod, **params)

        return response

    def do_get_related_records(self, record, module, relatedmodule, queryparameters):
        """
        * Retrieve related records.

        :param module:
        :param relatedmodule:
        :param queryparameters:
        :raise 'Login error':
        """
        if not self.__check_login():
            raise Exception('Login error')

        params = dict(
            id=record,
            module=module,
            relatedModule=relatedmodule,
            queryParameters=queryparameters
        )
        response = self.post('getRelatedRecords', **params)
        return response

    def do_set_related(self, relate_this_id, with_this_ids):
        """
        * Set relation between records.
	    * param relate_this_id string ID of record we want to related other records with
	    * param with_this_ids string/array either a string with one unique ID or an array of IDs to relate to the first parameter

        :param relate_this_id:
        :param with_this_ids:
        :raise 'Login error':
        """
        if not self.__check_login():
            raise Exception('Login error')

        params = dict(
            relate_this_id=relate_this_id,
            with_these_ids=with_this_ids
        )
        response = self.post('SetRelation', **params)
        return response
