# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os, sys
import requests
import json
from urllib.parse import urlparse
import re

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_path, '..'))

from pyLibGisApi.defs import defs_server_api

def email_validator(email):
    pattern = (r"^(?!\.)(?!.*\.\.)[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
               r"@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$")
    return re.match(pattern, email) is not None

class PostGISServerConnection():
    def __init__(self,
                 settings):
        self.settings = settings
        self.token = None
        self.project_by_id = {}
        self.user_by_email = {}
        self.url = None
        self.user = None
        self.password = None

    def add_user_to_project(self, project_id, user_id, role):
        str_error = ''
        data = None
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        url_get = self.url + defs_server_api.URL_PROJECTS_USERS_SUFFIX + '?project_id=' + str(project_id)
        url_get += ('&user_id=' + str(user_id))
        url_get += ('&role=' + role)
        payload = {}
        headers_as_dict = {}
        # headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        headers = headers_as_dict
        response = requests.request("POST", url_get, headers=headers, data=payload)#, data=payload)
        if response.status_code == 400:
            str_error = 'post request failed: not found'
            return str_error
        response_text_as_dict = json.loads(response.text)
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'get request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        return str_error

    def create_project(self, name, description, start_date, end_date, type):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        if not isinstance(name, str):
            str_error = 'name must be a string'
            return str_error
        if not isinstance(description, str):
            str_error = 'description must be a string'
            return str_error
        if not isinstance(start_date, str):
            str_error = ('start_date must be a valid date time string: {}'
                         .format(defs_server_api.PROJECT_DATE_TIME_FORMAT))
            return str_error
        if not isinstance(end_date, str):
            str_error = ('end_date must be a valid date time string: {}'
                         .format(defs_server_api.PROJECT_DATE_TIME_FORMAT))
            return str_error
        if not isinstance(type, str):
            str_error = 'type must be a type'
            return str_error
        if type.casefold() != defs_server_api.PROJECT_TYPE_DEFAULT.casefold():
            str_error = ('type must be: {}'.format(defs_server_api.PROJECT_TYPE_DEFAULT))
            return str_error
        url_get = self.url + defs_server_api.URL_PROJECTS_SUFFIX
        payload_as_dict = {}
        payload_as_dict[defs_server_api.PROJECT_TAG_NAME] = name
        payload_as_dict[defs_server_api.PROJECT_TAG_DESCRIPTION] = description
        payload_as_dict[defs_server_api.PROJECT_TAG_START_DATE] = start_date
        payload_as_dict[defs_server_api.PROJECT_TAG_END_DATE] = end_date
        payload_as_dict[defs_server_api.PROJECT_TAG_TYPE] = type
        payload = json.dumps(payload_as_dict)
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_get, headers=headers, data=payload)#, data=payload)
        if response.status_code == 400:
            str_error = 'post request failed: not found'
            return str_error
        response_text_as_dict = json.loads(response.text)
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'post request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        if not defs_server_api.RESPONSE_TEXT_TAG_DATA in response_text_as_dict:
            str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_DATA)
            return str_error
        # data = response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_DATA]
        # if not defs_server_api.PROJECT_TAG_ID in data:
        #     str_error = 'Not exists {} tag in response {}'.format(defs_server_api.PROJECT_TAG_ID,
        #                                                           defs_server_api.RESPONSE_TEXT_TAG_DATA)
        #     return str_error
        # project_id = data[defs_server_api.PROJECT_TAG_ID]
        str_error = self.get_projects()
        if str_error:
            str_error = ('Creating project: {}, error:\n{}'.format(name, str_error))
            return str_error
        # if bool(self.project_by_id):
        #     self.project_by_id.clear()
        #     self.project_by_id = {}
        # for project in data:
        #     id = project[defs_server_api.PROJECTS_TAG_ID]
        #     self.project_by_id[id] = project
        return str_error

    def delete_project_by_name(self, name):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        if not isinstance(name, str):
            str_error = 'name must be a string'
            return str_error
        str_error, project = self.get_project_by_name(name)
        if str_error:
            str_error = ('Recovering project: {}, error:\n{}'.format(name, str_error))
            return str_error
        if project is None:
            str_error = ('Not exists project: {}'.format(name))
            return str_error
        url_get = self.url + defs_server_api.URL_PROJECTS_SUFFIX
        url_get_with_parameter = url_get + '/' + str(project[defs_server_api.PROJECTS_TAG_ID])
        payload = ""
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("DELETE", url_get_with_parameter, headers=headers, data=payload)#, data=payload)
        if response.status_code == 400:
            str_error = 'post request failed: not found'
            return str_error
        response_text_as_dict = json.loads(response.text)
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'post request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        str_error = self.get_projects()
        if str_error:
            str_error = ('Deleting project: {}, error:\n{}'.format(name, str_error))
            return str_error
        return str_error

    def execute_sqls(self, project_id, sqls):
        str_error = ''
        data = None
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error, data
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error, data
        if not isinstance(sqls, list):
            str_error = 'sqls must be a list of string'
            return str_error, data
        if not isinstance(project_id, int):
            str_error = 'project_id must be an integer'
            return str_error, data
        for sql in sqls:
            if not isinstance(sql, str):
                str_error = 'sql must be a string'
                return str_error, data
        url_get = self.url + defs_server_api.URL_DB_SQL
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        sql_sentence = ''
        if len(sqls) > 1:
            sql_sentence += "BEGIN;\n" #  TRANSACTION
        for sql in sqls:
            sql_sentence += (sql + ';\n')
        if len(sqls) > 1:
            sql_sentence += 'COMMIT;\n'
        # else: # no funciona, hace cada ejecucion
        #     sqls.insert(0, 'BEGIN;')
        #     sqls.append('COMMIT;')
        payload_as_dict = {}
        payload_as_dict[defs_server_api.DB_TAG_SQL_COMMAND] = sql_sentence
        payload_as_dict[defs_server_api.DB_TAG_PROJECT_ID] = str(project_id)
        payload = json.dumps(payload_as_dict)
        response = requests.request("POST", url_get, headers=headers, data=payload)  # , data=payload)
        if response.status_code == 400:
            str_error = 'post request failed: not found'
            return str_error, data
        response_text_as_dict = json.loads(response.text)
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error, data
            str_error = 'post request failed: {}'.format(
                response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            if defs_server_api.RESPONSE_TEXT_TAG_ERRORS in response_text_as_dict:
                str_error = str_error + (
                    '\nError:\n{}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_ERRORS]))
                return str_error, data
        if not defs_server_api.RESPONSE_TEXT_TAG_DATA in response_text_as_dict:
            str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_DATA)
            return str_error, data
        data = response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_DATA]
        if not data is None:
            if isinstance(data, list):
                if len(data) == 0:
                    data = None
        return str_error, data

    def login(self, url, email, password):
        str_error = ''
        self.token = None
        self.user_by_email.clear()
        self.url = None
        self.user = None
        self.user_password = None
        if not isinstance(url, str):
            str_error = 'url must be a string'
            return str_error
        parsed_url = urlparse(url)
        if not bool(parsed_url.scheme):
            # parsed_url.geturl()
            # "no.scheme.com/math/12345.png"
            # parsed_url = parsed_url._replace(**{"scheme": "http"})
            # parsed_url.geturl()
            # 'http:///no.scheme.com/math/12345.png'
            str_error = ('url is not a valid value:\n{}'.format(url))
            return str_error
        url_login = url + defs_server_api.URL_LOGIN_SUFFIX
        if not isinstance(email, str):
            str_error = 'email must be a string'
            return str_error
        user_is_email = email_validator(email)
        if not user_is_email:
            str_error = ('value is email is not an email:\n{}'.format(email))
            return str_error
        if not isinstance(password, str):
            str_error = 'password must be a string'
            return str_error
        payload_as_dict = {}
        payload_as_dict[defs_server_api.LOGIN_TAG_EMAIL] = email
        payload_as_dict[defs_server_api.LOGIN_TAG_PASSWORD] = password
        payload = json.dumps(payload_as_dict)
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_login, headers=headers, data=payload)
        if response.status_code == 400:
            str_error = 'post request failed: not found'
            return str_error
        response_text_as_dict = json.loads(response.text)
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'post request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        if not defs_server_api.RESPONSE_TEXT_TAG_TOKEN in response_text_as_dict:
            str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_TOKEN)
            return str_error
        self.token = response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_TOKEN]
        self.url = url
        str_error = self.get_users()
        if str_error:
            return str_error
        str_error = self.get_projects()
        if str_error:
            return str_error
        if not email in self.user_by_email:
            str_error = 'User email: {} not found'.format(email)
            return str_error
        self.user = self.user_by_email[email]
        self.password = password
        return str_error

    def get_exists_project_by_name(self, project_name):
        str_error = ''
        exists_project = False
        for project_id in self.project_by_id:
            if project_name.casefold() == self.project_by_id[project_id][defs_server_api.PROJECTS_TAG_NAME].casefold():
                exists_project = True
                return str_error, exists_project
        return str_error, exists_project

    def get_project_by_name(self, project_name):
        str_error = ''
        project = None
        for project_id in self.project_by_id:
            if project_name.casefold() == self.project_by_id[project_id][defs_server_api.PROJECTS_TAG_NAME].casefold():
                project = self.project_by_id[project_id]
                return str_error, project
        return str_error, project

    def get_project_data(self, project_id):
        str_error = ''
        data = None
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error, data
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error, data
        url_get = self.url + defs_server_api.URL_PROJECTS_SUFFIX + '/' + str(project_id)
        payload = {}
        headers_as_dict = {}
        # headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        headers = headers_as_dict
        response = requests.request("GET", url_get, headers=headers, data=payload)#, data=payload)
        if response.status_code == 400:
            str_error = 'post request failed: not found'
            return str_error, data
        response_text_as_dict = json.loads(response.text)
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error, data
            str_error = 'get request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error, data
        if not defs_server_api.RESPONSE_TEXT_TAG_DATA in response_text_as_dict:
            str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_DATA)
            return str_error, data
        data = response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_DATA]
        return str_error, data

    def get_project_names(self):
        str_error = ''
        project_names = []
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error, project_names
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error, project_names
        if self.user is None:
            str_error = 'user is none. Connect before'
            return str_error, project_names
        for project_id in self.project_by_id:
            project_name = self.project_by_id[project_id][defs_server_api.PROJECTS_TAG_NAME]
            project_names.append(project_name)
        return str_error, project_names

    def get_project_role_by_name(self, name):
        str_error = ''
        role = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error, role
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error, role
        if not isinstance(name, str):
            str_error = 'name must be a string'
            return str_error, role
        str_error, project = self.get_project_by_name(name)
        if str_error:
            str_error = ('Recovering project: {}, error:\n{}'.format(name, str_error))
            return str_error, role
        if project is None:
            str_error = ('Not exists project: {}'.format(name))
            return str_error, role
        role = project[defs_server_api.PROJECTS_TAG_ROLE]
        return str_error, role

    def get_projects(self):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        url_get = self.url + defs_server_api.URL_PROJECTS_SUFFIX
        payload = {}
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        headers = headers_as_dict
        response = requests.request("GET", url_get, headers=headers, data=payload)#, data=payload)
        if response.status_code == 400:
            str_error = 'post request failed: not found'
            return str_error
        response_text_as_dict = json.loads(response.text)
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'post request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        if not defs_server_api.RESPONSE_TEXT_TAG_DATA in response_text_as_dict:
            str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_DATA)
            return str_error
        data = response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_DATA]
        if bool(self.project_by_id):
            self.project_by_id.clear()
            self.project_by_id = {}
        for project in data:
            id = project[defs_server_api.PROJECTS_TAG_ID]
            self.project_by_id[id] = project
        return str_error

    def get_users(self):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        url_get = self.url + defs_server_api.URL_USERS_SUFFIX
        payload = {}
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        headers = headers_as_dict
        response = requests.request("GET", url_get, headers=headers, data=payload)#, data=payload)
        if response.status_code == 400:
            str_error = 'post request failed: not found'
            return str_error
        response_text_as_dict = json.loads(response.text)
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'post request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        if not defs_server_api.RESPONSE_TEXT_TAG_DATA in response_text_as_dict:
            str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_DATA)
            return str_error
        data = response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_DATA]
        if bool(self.user_by_email):
            self.user_by_email.clear()
            self.user_by_email = {}
        for user in data:
            if defs_server_api.ignore_user_admin:
                username = user[defs_server_api.USERS_TAG_NAME]
                if username.casefold() == defs_server_api.USER_ADMIN_NAME.casefold():
                    continue
            usermail = user[defs_server_api.USERS_TAG_EMAIL]
            self.user_by_email[usermail] = user
        return str_error

    def register(self, url, name, email, password):
        str_error = ''
        # self.token = None
        # self.user_by_email.clear()
        # self.url = None
        # self.user = None
        # self.user_password = None
        if not isinstance(url, str):
            str_error = 'url must be a string'
            return str_error
        parsed_url = urlparse(url)
        if not bool(parsed_url.scheme):
            # parsed_url.geturl()
            # "no.scheme.com/math/12345.png"
            # parsed_url = parsed_url._replace(**{"scheme": "http"})
            # parsed_url.geturl()
            # 'http:///no.scheme.com/math/12345.png'
            str_error = ('url is not a valid value:\n{}'.format(url))
            return str_error
        url_register = url + defs_server_api.URL_REGISTER_SUFFIX
        if not isinstance(name, str):
            str_error = 'name must be a string'
            return str_error
        if not isinstance(email, str):
            str_error = 'email must be a string'
            return str_error
        user_is_email = email_validator(email)
        if not user_is_email:
            str_error = ('email value is not an email:\n{}'.format(user))
            return str_error
        if not isinstance(password, str):
            str_error = 'password must be a string'
            return str_error
        payload_as_dict = {}
        payload_as_dict[defs_server_api.REGISTER_TAG_NAME] = name
        payload_as_dict[defs_server_api.REGISTER_TAG_EMAIL] = email
        payload_as_dict[defs_server_api.REGISTER_TAG_PASSWORD] = password
        payload = json.dumps(payload_as_dict)
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_register, headers=headers, data=payload)
        if response.status_code == 400:
            str_error = 'post request failed: not found'
            return str_error
        response_text_as_dict = json.loads(response.text)
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'post request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        # message_login_success = response_text_as_dict['message']
        # if not message_login_success.casefold() == "User logged in successfully.".casefold():
        #     str_error = 'post request failed: {}'.format(message_login_success)
        #     return str_error
        if not defs_server_api.RESPONSE_TEXT_TAG_TOKEN in response_text_as_dict:
            str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_TOKEN)
            return str_error
        self.token = response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_TOKEN]
        self.url = url
        str_error = self.get_users()
        if str_error:
            return str_error
        if not self.user is None:
            user_email = self.user[defs_server_api.USERS_TAG_EMAIL]
            if not user_email in self.user_by_email:
                self.user = None
                self.password = None
                str_error = 'Previous user email: {} not found'.format(email)
                return str_error
        return str_error

