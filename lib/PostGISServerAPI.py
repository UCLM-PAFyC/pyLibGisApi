# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os, sys
import requests
import json
from urllib.parse import urlparse
import re
from datetime import datetime

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_path, '..'))

from pyLibProcesses.defs import defs_processes as processes_defs_processes
from pyLibGisApi.defs import defs_server_api
from pyLibGisApi.defs import defs_processes
from pyLibParameters import defs_pars
from pyLibProject.defs import defs_layers_groups as defs_layers_groups

def email_validator(email):
    pattern = (r"^(?!\.)(?!.*\.\.)[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
               r"@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$")
    return re.match(pattern, email) is not None

class PostGISServerAPI():
    def __init__(self,
                 settings):
        self.settings = settings
        self.token = None
        self.project_by_id = {}
        self.user_by_email = {}
        self.url = None
        self.user = None
        self.password = None
        self.layers_group_id_by_name = None # dict
        self.layer_id_by_table_name = None # dict
        self.current_project_id = None

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
        url_post = self.url + defs_server_api.URL_PROJECTS_USERS_SUFFIX + '?project_id=' + str(project_id)
        url_post += ('&user_id=' + str(user_id))
        url_post += ('&role=' + role)
        payload = {}
        headers_as_dict = {}
        # headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        headers = headers_as_dict
        response = requests.request("POST", url_post, headers=headers, data=payload)#, data=payload)
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

    def create_folder(self, project_id, path, folder):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        if not isinstance(project_id, int):
            str_error = 'project_id must be an integer'
            return str_error
        if not isinstance(path, str):
            str_error = 'path must be a string'
            return str_error
        if not isinstance(folder, str):
            str_error = 'folder must be a string'
            return str_error
        url_post = self.url + defs_server_api.URL_FILE_MANAGER_FOLDER_SUFFIX
        payload_as_dict = {}
        payload_as_dict[defs_server_api.PROJECT_TAG_ID_WITH_PROJECT] = str(project_id)
        payload_as_dict[defs_server_api.FILE_MANAGER_TAG_ACTION] = defs_server_api.FILE_MANAGER_TAG_ACTION_CREATE
        payload_as_dict[defs_server_api.PATH_TAG] = path
        payload_as_dict[defs_server_api.FOLDER_TAG] = folder
        payload = json.dumps(payload_as_dict)
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_post, headers=headers, data=payload)#, data=payload)
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
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'get request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        return str_error

    def create_layer(self, project_id, layer_as_dict):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        if not isinstance(project_id, int):
            str_error = 'project_id must be an integer'
            return str_error
        if not isinstance(layer_as_dict, dict):
            str_error = 'layer_as_dict must be a dictionary'
            return str_error
        url_post = self.url + defs_server_api.URL_LAYERS + '/' + str(project_id)
        payload = json.dumps(layer_as_dict)
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_post, headers=headers, data=payload)#, data=payload)
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
        str_error = self.get_layers(project_id)
        if str_error:
            str_error = ('Creating layer, error:\n{}'.format(str_error))
            return str_error
        return str_error

    def create_layers_group(self, project_id, layers_group_as_dict):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        if not isinstance(project_id, int):
            str_error = 'project_id must be an integer'
            return str_error
        if not isinstance(layers_group_as_dict, dict):
            str_error = 'layers_group_as_dict must be a dictionary'
            return str_error
        url_post = self.url + defs_server_api.URL_LAYERS_GROUPS + '/' + str(project_id)
        payload = json.dumps(layers_group_as_dict)
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_post, headers=headers, data=payload)#, data=payload)
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
        str_error = self.get_layers_groups(project_id)
        if str_error:
            str_error = ('Creating layers group, error:\n{}'.format(str_error))
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
        url_post = self.url + defs_server_api.URL_PROJECTS_SUFFIX
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
        response = requests.request("POST", url_post, headers=headers, data=payload)#, data=payload)
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
        url_delete = self.url + defs_server_api.URL_PROJECTS_SUFFIX
        url_get_with_parameter = url_delete + '/' + str(project[defs_server_api.PROJECTS_TAG_ID])
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
        url_post = self.url + defs_server_api.URL_DB_SQL
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
        response = requests.request("POST", url_post, headers=headers, data=payload)  # , data=payload)
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
        url_post = url + defs_server_api.URL_LOGIN_SUFFIX
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
        response = requests.request("POST", url_post, headers=headers, data=payload)
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

    def get_layers(self, project_id):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        if not isinstance(project_id, int):
            str_error = 'project_id must be an integer'
            return str_error
        url_get = self.url + defs_server_api.URL_LAYERS + '/' + str(project_id)
        payload = {}
        headers_as_dict = {}
        # headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
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
        if not defs_server_api.RESPONSE_TEXT_TAG_DATA in response_text_as_dict:
            str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_DATA)
            return str_error
        data = response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_DATA]
        if self.layer_id_by_table_name is not None:
            del self.layer_id_by_table_name
            self.layer_id_by_table_name = None
        self.layer_id_by_table_name = {}
        for layers_group in data:
            layers_group_db_id = layers_group[defs_server_api.LAYER_LAYERS_GROUPS_TAG_ID]
            layers_group_name = layers_group[defs_server_api.LAYER_LAYERS_GROUPS_TAG_NAME]
            layers = layers_group[defs_server_api.LAYER_LAYERS_GROUPS_TAG_LAYERS]
            for i in range(len(layers)):
                layer = layers[i]
                layer_name = layer[defs_server_api.LAYER_TAG_TABLE_NAME]
                layer_db_id = layer[defs_server_api.LAYER_TAG_ID]
                self.layer_id_by_table_name[layer_name] = layer_db_id
        return str_error

    def get_layers_groups(self, project_id):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        if not isinstance(project_id, int):
            str_error = 'project_id must be an integer'
            return str_error
        url_get = self.url + defs_server_api.URL_LAYERS_GROUPS + '/' + str(project_id)
        payload = {}
        headers_as_dict = {}
        # headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
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
        if not defs_server_api.RESPONSE_TEXT_TAG_DATA in response_text_as_dict:
            str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_DATA)
            return str_error
        data = response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_DATA]
        if self.layers_group_id_by_name is not None:
            del self.layers_group_id_by_name
            self.layers_group_id_by_name = None
        self.layers_group_id_by_name = {}
        for layers_group in data:
            name = layers_group[defs_server_api.LAYERS_GROUPS_TAG_NAME]
            id = layers_group[defs_server_api.LAYERS_GROUPS_TAG_ID]
            self.layers_group_id_by_name[name] = id
        return str_error

    def get_layer_id_by_table_name(self, project_id, table_name):
        str_error = ''
        id = None
        if self.layer_id_by_table_name is None:
            str_error = self.get_layers(project_id)
            if str_error:
                return str_error, id
        # if not table_name in self.layer_id_by_table_name:
        #     str_error = ('Not exists layer: {}'.format(table_name))
        #     return str_error, id
        if table_name in self.layer_id_by_table_name:
            id = self.layer_id_by_table_name[table_name]
        return str_error, id

    def get_layers_group_id_by_name(self, project_id, layers_group_name):
        str_error = ''
        id = None
        if self.layers_group_id_by_name is None:
            str_error = self.get_layers_groups(project_id)
            if str_error:
                return str_error, id
        # if not layers_group_name in self.layers_group_id_by_name:
        #     str_error = ('Not exists layers group: {}'.format(layers_group_name))
        #     return str_error, id
        if layers_group_name in self.layers_group_id_by_name:
            id = self.layers_group_id_by_name[layers_group_name]
        return str_error, id

    def get_folder_structure(self, project_id, folder):
        str_error = ''
        data = None
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error, data
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error, data
        if not isinstance(project_id, int):
            str_error = 'project_id must be an integer'
            return str_error, data
        if not isinstance(folder, str):
            str_error = 'folder must be a string'
            return str_error, data
        url_post = self.url + defs_server_api.URL_FILE_MANAGER_SCAN_SUFFIX
        payload_as_dict = {}
        payload_as_dict[defs_server_api.PROJECT_TAG_ID_WITH_PROJECT] = str(project_id)
        payload_as_dict[defs_server_api.PATH_TAG] = folder
        payload = json.dumps(payload_as_dict)
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_post, headers=headers, data=payload)#, data=payload)
        if response.status_code == 400:
            str_error = 'post request failed: not found'
            return str_error, data
        response_text_as_dict = json.loads(response.text)
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error, data
            str_error = 'post request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error, data
        if not defs_server_api.RESPONSE_TEXT_TAG_DATA in response_text_as_dict:
            str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_DATA)
            return str_error, data
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

    def move_folder_or_file(self, project_id, source_path, target_path):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        if not isinstance(project_id, int):
            str_error = 'project_id must be an integer'
            return str_error
        if not isinstance(source_path, str):
            str_error = 'path must be a string'
            return str_error
        if not isinstance(target_path, str):
            str_error = 'path must be a string'
            return str_error
        url_post = self.url + defs_server_api.URL_FILE_MANAGER_MOVE
        payload_as_dict = {}
        payload_as_dict[defs_server_api.PROJECT_TAG_ID_WITH_PROJECT] = str(project_id)
        payload_as_dict[defs_server_api.FILE_MANAGER_TAG_SOURCE_PATH] = source_path
        payload_as_dict[defs_server_api.FILE_MANAGER_TAG_TARGET_PATH] = target_path
        payload = json.dumps(payload_as_dict)
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_post, headers=headers, data=payload)#, data=payload)
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
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'get request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        return str_error

    def process_publish_layers_set(self,
                                   process,
                                   dialog = None):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        end_date_time = None
        log = None
        if self.current_project_id is None:
            str_error = 'current project id is none. Set before'
            return str_error, end_date_time, log
        name = process[processes_defs_processes.PROCESS_FIELD_NAME]
        parametes_manager = process[processes_defs_processes.PROCESS_FIELD_PARAMETERS]
        if not defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_UPLOAD_FOLDER in parametes_manager.parameters:
            str_error = ('Process: {} does not have parameter: {}'.
                         format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_UPLOAD_FOLDER))
            return str_error, end_date_time, log
        if not defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET in parametes_manager.parameters:
            str_error = ('Process: {} does not have parameter: {}'.
                         format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET))
            return str_error, end_date_time, log
        if not defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_NAME in parametes_manager.parameters:
            str_error = ('Process: {} does not have parameter: {}'.
                         format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_NAME))
            return str_error, end_date_time, log
        parameter_name= parametes_manager.parameters[defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_NAME]
        publish_name = str(parameter_name)
        # make upload folder
        parameter_upload_folder= parametes_manager.parameters[defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_UPLOAD_FOLDER]
        root_path = defs_server_api.ROOT_PATH
        str_error, data = self.get_folder_structure(self.current_project_id, root_path)
        if str_error:
            str_error = ('Process: {}, for project: {}, error getting folders structure:\n{}'.
                         format(name, str(project_id), str_error))
            return str_error, end_date_time, log
        upload_folder = str(parameter_upload_folder)
        folders = []
        if '/' in upload_folder:
            folders = upload_folder.split('/')
        else:
            folders.append(upload_folder)
        files_in_uploads_folder = []
        files_in_target_folder = []
        if defs_server_api.UPLOADS_FOLDER in data:
            files_in_uploads_folder = data[defs_server_api.UPLOADS_FOLDER]
        data_base = data
        for i in range(len(folders)):
            folder = folders[i]
            if not folder in data_base:
                str_error = self.create_folder(self.current_project_id, defs_server_api.ROOT_PATH,
                                               upload_folder)
                if str_error:
                    str_error = ('Process: {}, for project: {}, error getting folders structure:\n{}'.
                                 format(name, str(project_id), str_error))
                    return str_error, end_date_time, log
                break
            data_base = data_base[folder]
            if i == len(folders) - 1:
                files_in_target_folder = data_base
        # upload file
        parameter_layers_set= parametes_manager.parameters[defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET]
        layers_set_as_str = str(parameter_layers_set)
        layer_set_as_dict = json.loads(layers_set_as_str)
        if not defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_LAYER_PARAMETER_FILE_PATH in layer_set_as_dict:
            str_error = ('Process: {}, in parameter: {} not exists parameter: {}'.
                         format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_LAYER_PARAMETER_FILE_PATH))
            return str_error, end_date_time, log
        file_path = layer_set_as_dict[defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_LAYER_PARAMETER_FILE_PATH]
        if not os.path.exists(file_path):
            str_error = ('Process: {}, in parameter: {} in parameter: {}\nnot exists file:\n{}'.
                         format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_LAYER_PARAMETER_FILE_PATH,
                                file_path))
            return str_error, end_date_time, log
        file_basename = os.path.basename(file_path)
        file_path_in_uploads_folder = '/' + defs_server_api.UPLOADS_FOLDER + '/' + file_basename
        file_path_in_target_folder = '/' + upload_folder + '/' + file_basename
        target_folder = '/' + upload_folder
        if not defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_LAYER_PARAMETER_LAYERS in layer_set_as_dict:
            str_error = ('Process: {}, in parameter: {} not exists parameter: {}'.
                         format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_LAYER_PARAMETER_LAYERS))
            return str_error, end_date_time, log
        layers = layer_set_as_dict[defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_LAYER_PARAMETER_LAYERS]
        if not isinstance(layers, list):
            str_error = ('Process: {}, in parameter: {} parameter: {} must be a list'.
                         format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_LAYER_PARAMETER_LAYERS))
            return str_error, end_date_time, log
        if len(layers) == 0:
            str_error = ('Process: {}, in parameter: {} parameter: {} is an empty list'.
                         format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_LAYER_PARAMETER_LAYERS))
            return str_error, end_date_time, log
        publish_content_as_dict = {}
        publish_content_as_dict['name'] = publish_name
        publish_content_as_dict['project_id'] = self.current_project_id
        publish_content_as_dict['path'] = file_path_in_target_folder
        publish_layers_content = []
        layers_groups_pos_order = 1
        for i in range(len(layers)):
            layer = layers[i]
            if not isinstance(layer, list):
                str_error = ('Process: {}, in parameter: {} parameter: {} in position: {} must be a list'.
                             format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                    str(i+1), defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_LAYER_PARAMETER_LAYERS))
                return str_error, end_date_time, log
            field_value_by_source_tag = {}
            for j in range(len(layer)):
                layer_field = layer[j]
                if not defs_pars.PARAMETER_FIELD_LABEL in layer_field:
                    str_error = ('Process: {}, in parameter: {} in layer position: {}\nnot exists field: {}'.
                                 format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                        str(i+1), defs_pars.PARAMETER_FIELD_LABEL))
                    return str_error, end_date_time, log
                field_name = layer[j][defs_pars.PARAMETER_FIELD_LABEL]
                if not defs_pars.PARAMETER_FIELD_VALUE in layer_field:
                    str_error = ('Process: {}, in parameter: {} in layer position: {}\nnot exists field: {}'.
                                 format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                        str(i+1), defs_pars.PARAMETER_FIELD_VALUE))
                    return str_error, end_date_time, log
                field_value = layer[j][defs_pars.PARAMETER_FIELD_VALUE]
                if field_name.casefold() == defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SOURCE_TAG_DATE.casefold():
                    date_in_publish_format = field_value[0:4] + '-' + field_value[4:6] + '-' + field_value[6:9]
                    field_value = date_in_publish_format
                elif field_name.casefold() == defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SOURCE_TAG_CRS.casefold():
                    field_value = field_value.replace('EPSG:','')
                elif field_name.casefold() == defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SOURCE_TAG_TYPE.casefold():
                    if field_value.casefold() == defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SOURCE_TAG_TYPE_VECTOR.casefold():
                        field_value = defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_TARGET_TAG_TYPE_VECTOR
                    elif field_value.casefold() == defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SOURCE_TAG_TYPE_RASTER.casefold():
                        field_value = defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_TARGET_TAG_TYPE_RASTER
                if field_name.casefold() == defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SOURCE_TAG_GROUP_NAME.casefold():
                    if field_value:# no empty
                        str_error = self.get_layers_groups(self.current_project_id)
                        if str_error:
                            str_error = ('Process: {}, for project: {}, getting layers groups, error:\n{}'.
                                        format(name, str(project_id), str_error))
                            return str_error, end_date_time, log
                        if not field_value in self.layers_group_id_by_name:
                            layers_group_as_dict = {}
                            layers_group_as_dict[defs_layers_groups.LAYERS_GROUP_FIELD_NAME] = field_value
                            layers_group_as_dict[defs_layers_groups.LAYERS_GROUP_FIELD_DESCRIPTION] = 'From publish product process'
                            layers_group_as_dict[defs_layers_groups.LAYERS_GROUP_FIELD_VISIBILITY] = True
                            layers_group_as_dict[defs_layers_groups.LAYERS_GROUP_FIELD_POS_ORDER] = layers_groups_pos_order
                            layers_groups_pos_order = layers_groups_pos_order + 1
                            layers_group_as_dict[defs_layers_groups.LAYERS_GROUP_FIELD_MIN_ZOOM] = defs_layers_groups.LAYERS_GROUP_FIELD_MIN_ZOOM_DEFAULT_VALUE
                            layers_group_as_dict[defs_layers_groups.LAYERS_GROUP_FIELD_MAX_ZOOM] = defs_layers_groups.LAYERS_GROUP_FIELD_MAX_ZOOM_DEFAULT_VALUE
                            layers_group_as_dict[defs_layers_groups.LAYERS_GROUP_FIELD_OPEN_IN_LAYERS_WITCHER] = True
                            str_error = self.create_layers_group(self.current_project_id, layers_group_as_dict)
                            if str_error:
                                str_error = ('Process: {}, in parameter: {} in layer position: {}'
                                             '\nmaking layers group: {}\nerror:\n{}'.
                                             format(name,
                                                    defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                                    str(i + 1), field_value, str_error))
                                return str_error, end_date_time, log
                            str_error = self.get_layers_groups(self.current_project_id)
                            if str_error:
                                str_error = ('Process: {}, for project: {}, getting layers groups, error:\n{}'.
                                            format(name, str(project_id), str_error))
                                return str_error, end_date_time, log
                        str_error, layer_group_id = self.get_layers_group_id_by_name(self.current_project_id, field_value)
                        if str_error:
                            str_error = ('Process: {}, in parameter: {} in layer position: {}'
                                         '\ngetting layers group id for layer group: {}\nerror:\n{}'.
                                         format(name,
                                                defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                                str(i + 1), field_value, str_error))
                            return str_error, end_date_time, log
                        field_value = layer_group_id
                field_value_by_source_tag[field_name] = field_value
            publish_layer_content = {}
            for source_tag in defs_processes.process_publish_layer_target_tag_by_source_tag:
                target_tag = defs_processes.process_publish_layer_target_tag_by_source_tag[source_tag]
                if not source_tag in field_value_by_source_tag:
                    str_error = ('Process: {}, in parameter: {} in layer position: {}\nnot exists field: {}'.
                                 format(name, defs_processes.PROCESS_FUNCTION_PUBLISH_LAYERS_SET_PARAMETER_LAYERS_SET,
                                        str(i+1), source_tag))
                    return str_error, end_date_time, log
                publish_layer_content[target_tag] = field_value_by_source_tag[source_tag]
            publish_layers_content.append(publish_layer_content)
        publish_content_as_dict['layers'] = publish_layers_content

        # error upload
        # if exists file in uploads folder, first remove it
        if file_basename in files_in_uploads_folder:
            file_path_to_remove = '/' + defs_server_api.UPLOADS_FOLDER + '/' + file_basename
            str_error = self.remove_folder_or_file(self.current_project_id, file_path_to_remove)
            if str_error:
                str_error = ('Process: {}, for project: {}, removing:\n{}\nerror:\n{}'.
                             format(name, str(project_id), file_path_to_remove, str_error))
                return str_error, end_date_time, log
        str_error = self.upload_file(self.current_project_id, file_path)
        if str_error:
            str_error = ('Process: {}, for project: {}, uploading:\n{}\nerror:\n{}'.
                         format(name, str(project_id), file_path, str_error))
            return str_error, end_date_time, log
        # error upload

        # if exists file in target folder, first remove it
        if file_basename in files_in_target_folder:
            file_path_to_remove = '/' + upload_folder + '/' + file_basename
            str_error = self.remove_folder_or_file(self.current_project_id, file_path_to_remove)
            if str_error:
                str_error = ('Process: {}, for project: {}, removing:\n{}\nerror:\n{}'.
                             format(name, str(project_id), file_path_to_remove, str_error))
                return str_error, end_date_time, log
        # move file to target folder
        str_error = self.move_folder_or_file(self.current_project_id, file_path_in_uploads_folder,
                                             target_folder)
        if str_error:
            str_error = ('Process: {}, for project: {}, moving from:\n{}\nto:\n{}\nerror:\n{}'.
                         format(name, str(project_id), file_path_in_uploads_folder,
                                file_path_in_target_folder, str_error))
            return str_error, end_date_time, log

        # publicar
        url_post = self.url + defs_server_api.URL_PRODUCT_PUBLISH
        payload = json.dumps(publish_content_as_dict)
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_post, headers=headers, data=payload)#, data=payload)
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
        end_date_time = datetime.datetime.now()
        return str_error, end_date_time, log

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
        url_post = url + defs_server_api.URL_REGISTER_SUFFIX
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
        response = requests.request("POST", url_post, headers=headers, data=payload)
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

    def remove_folder_or_file(self, project_id, path):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        if not isinstance(project_id, int):
            str_error = 'project_id must be an integer'
            return str_error
        if not isinstance(path, str):
            str_error = 'path must be a string'
            return str_error
        url_post = self.url + defs_server_api.URL_FILE_MANAGER_DELETE
        payload_as_dict = {}
        payload_as_dict[defs_server_api.PROJECT_TAG_ID_WITH_PROJECT] = str(project_id)
        payload_as_dict[defs_server_api.FILE_MANAGER_TAG_ACTION] = defs_server_api.FILE_MANAGER_TAG_ACTION_CREATE
        payload_as_dict[defs_server_api.PATH_TAG] = path
        payload = json.dumps(payload_as_dict)
        headers_as_dict = {}
        headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_post, headers=headers, data=payload)#, data=payload)
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
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'get request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        return str_error

    def remove_user_from_project(self, project_id, user_id):
        str_error = ''
        data = None
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        url_delete = self.url + defs_server_api.URL_PROJECTS_USERS_SUFFIX + '/' + str(project_id)
        url_delete += ('/' + str(user_id))
        payload = {}
        headers_as_dict = {}
        # headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_DEFAULT_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        headers = headers_as_dict
        response = requests.request("DELETE", url_delete, headers=headers, data=payload)#, data=payload)
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

    def set_current_project_id(self, project_id):
        self.current_project_id = project_id

    def upload_file(self, project_id, file_path):
        str_error = ''
        if self.url is None:
            str_error = 'url is none. Connect before'
            return str_error
        if self.token is None:
            str_error = 'token is none. Connect before'
            return str_error
        if not isinstance(project_id, int):
            str_error = 'project_id must be an integer'
            return str_error
        if not isinstance(file_path, str):
            str_error = 'path must be a string'
            return str_error
        file_basename = os.path.basename(file_path)
        url_post = self.url + defs_server_api.URL_FILE_MANAGER_UPLOADS
        payload_as_dict = {}
        payload_as_dict[defs_server_api.PROJECT_TAG_ID_WITH_PROJECT] = str(project_id)
        # payload_as_dict[defs_server_api.PROJECT_TAG_ID_WITH_PROJECT] = '\'' + str(project_id) + '\''
        # payload_as_dict[defs_server_api.PROJECT_TAG_ID_WITH_PROJECT] = project_id
        # payload_as_dict[defs_server_api.PROJECT_TAG_ID_WITH_PROJECT] = 'project_' + str(project_id)
        # payload = json.dumps(payload_as_dict)
        payload = payload_as_dict
        files = [
            # ('file', ('file', open(file_path, 'rb'), 'application/octet-stream'))
            ('file', (file_basename, open(file_path, 'rb'), 'application/octet-stream'))
        ]
        headers_as_dict = {}
        # headers_as_dict[defs_server_api.HEADERS_TAG_CONTENT] = defs_server_api.HEADERS_CONTENT_UPLOAD_FILE_VALUE
        headers_as_dict[defs_server_api.HEADERS_TAG_AUTHORIZATION] = (defs_server_api.HEADERS_TAG_AUTHORIZATION_BEARER
                                                                      + self.token)
        # headers_as_dict[defs_server_api.HEADERS_TAG_ACCEPT] = defs_server_api.HEADERS_ACCEPT_DEFAULT_VALUE
        # headers = json.dumps(headers_as_dict)
        headers = headers_as_dict
        response = requests.request("POST", url_post, headers=headers, data=payload, files=files)#, data=payload)
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
        # if not defs_server_api.RESPONSE_TEXT_TAG_DATA in response_text_as_dict:
        #     str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_DATA)
        #     return str_error
        if not response.ok:
            if not defs_server_api.RESPONSE_TEXT_TAG_MESSAGE in response_text_as_dict:
                str_error = 'Not exists {} tag in response'.format(defs_server_api.RESPONSE_TEXT_TAG_MESSAGE)
                return str_error
            str_error = 'get request failed: {}'.format(response_text_as_dict[defs_server_api.RESPONSE_TEXT_TAG_MESSAGE])
            return str_error
        return str_error
