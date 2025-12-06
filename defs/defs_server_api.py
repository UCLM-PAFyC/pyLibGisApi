# authors:
# David Hernandez Lopez, david.hernandez@uclm.es
import os
import sys

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(current_path, '..'))

RESPONSE_TEXT_TAG_DATA = 'data'
RESPONSE_TEXT_TAG_MESSAGE = 'message'
RESPONSE_TEXT_TAG_TOKEN = 'token'
RESPONSE_TEXT_TAG_ERRORS = 'errors'

HEADERS_TAG_CONTENT = 'Content-Type'
HEADERS_CONTENT_DEFAULT_VALUE = 'application/json'
HEADERS_TAG_AUTHORIZATION = 'Authorization'
HEADERS_TAG_AUTHORIZATION_BEARER = 'Bearer '# one space after
HEADERS_TAG_ACCEPT = 'Accept'
HEADERS_ACCEPT_DEFAULT_VALUE = 'application/json'

URL_LOGIN_SUFFIX = '/api/auth/login'
URL_USERS_SUFFIX = '/api/users'
URL_REGISTER_SUFFIX = '/api/auth/register'
URL_PROJECTS_SUFFIX = '/api/projects'
URL_DB_SQL = '/api/db/sql'
URL_PROJECTS_USERS_SUFFIX = '/api/projects/users'

LOGIN_TAG_EMAIL = 'email'
LOGIN_TAG_PASSWORD = 'password'

PROJECTS_TAG_ID = 'id'
PROJECTS_TAG_NAME = 'name'
PROJECTS_TAG_DESCRIPTION = 'description'
PROJECTS_TAG_ROLE = 'role'
PROJECTS_TAG_WMS_SERVICE = 'wms_service'
PROJECTS_TAG_URL_VIEWER = 'url_viewer'

PROJECT_TAG_NAME = 'name'
PROJECT_TAG_DESCRIPTION = 'description'
PROJECT_TAG_START_DATE = 'start_date'
PROJECT_TAG_END_DATE = 'end_date'
PROJECT_TAG_TYPE = 'type'
PROJECT_TYPE_DEFAULT = 'default'
PROJECT_DATE_TIME_FORMAT ='yyyy-MM-dd HH:mm:ss'
PROJECT_TAG_ID = 'id'
PROJECT_SCHEMA_PREFIX = 'project_'
PROJECT_TAG_USERS = 'users'
PROJECT_TAG_USERS_ID = 'id'
PROJECT_TAG_USERS_NAME = 'name'
PROJECT_TAG_USERS_ROLE = 'role'
PROJECT_TAG_WMS_SERVICE = 'wms_service'
PROJECT_TAG_WFS_SERVICE = 'wfs_service'
PROJECT_WFS_SERVICE_TAG_URL = 'url'
PROJECT_WFS_SERVICE_TAG_USER = 'user'
PROJECT_WFS_SERVICE_TAG_PASSWORD = 'password'
PROJECT_TAG_URL_VIEWER = 'url_viewer'

REGISTER_TAG_NAME = 'name'
REGISTER_TAG_EMAIL = 'email'
REGISTER_TAG_PASSWORD = 'password'

ignore_user_admin = True
USERS_TAG_NAME = 'name'
USERS_TAG_EMAIL = 'email'
USERS_TAG_ID = 'id'
USER_ADMIN_NAME = 'Administrador'

ROLE_ADMIN = 'admin'
ROLE_OWNER = 'owner'
ROLE_EDITOR = 'editor'
ROLE_USER = 'user'
roles=[ROLE_OWNER, ROLE_ADMIN, ROLE_EDITOR, ROLE_USER]

DB_TAG_SQL_COMMAND = "sql_command"
DB_TAG_PROJECT_ID = "project_id"

