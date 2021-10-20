import pytest
from mock import patch

from fastapi import status

from api.routes.workspaces import get_current_ws_user, get_current_tre_user
from models.domain.authentication import User
from models.domain.user_resource import UserResource
from models.domain.workspace import Workspace, WorkspaceRole
from models.domain.workspace_service import WorkspaceService
from resources import strings


pytestmark = pytest.mark.asyncio


WORKSPACE_ID = '933ad738-7265-4b5f-9eae-a1a62928772e'
SERVICE_ID = 'abcad738-7265-4b5f-9eae-a1a62928772e'
USER_RESOURCE_ID = 'abcad738-7265-4b5f-9eae-a1a62928772e'


def sample_workspace():
    return Workspace(id=WORKSPACE_ID, resourceTemplateName='template name', resourceTemplateVersion='1.0')


def sample_workspace_service():
    return WorkspaceService(id=SERVICE_ID, resourceTemplateName='template name', resourceTemplateVersion='1.0')


def sample_user_resource():
    return UserResource(id=USER_RESOURCE_ID, resourceTemplateName='template name', resourceTemplateVersion='1.0')


# TEMPLATES
class TestTemplateRoutesThatRequireAdminRights:
    @pytest.fixture(autouse=True, scope='class')
    def log_in_with_non_admin(self, app, non_admin_user):
        # try accessing the route with a non-admin user
        app.dependency_overrides[get_current_tre_user] = non_admin_user
        yield
        app.dependency_overrides = {}

    async def test_get_workspace_templates_requires_admin_rights(self, app, client):
        response = await client.get(app.url_path_for(strings.API_GET_WORKSPACE_TEMPLATES))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_post_workspace_templates_requires_admin_rights(self, app, client):
        response = await client.post(app.url_path_for(strings.API_CREATE_WORKSPACE_TEMPLATES), json='{}')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_post_workspace_service_templates_requires_admin_rights(self, app, client):
        response = await client.post(app.url_path_for(strings.API_CREATE_WORKSPACE_SERVICE_TEMPLATES), json='{}')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_post_user_resource_templates_requires_admin_rights(self, app, client):
        response = await client.post(app.url_path_for(strings.API_CREATE_USER_RESOURCE_TEMPLATES, service_template_name="not-important"), json='{}')
        assert response.status_code == status.HTTP_403_FORBIDDEN


# RESOURCES
class TestWorkspaceRoutesThatRequireAdminRights:
    @pytest.fixture(autouse=True, scope='class')
    def log_in_with_non_owner(self, app, non_owner_user):
        # try accessing the route with a non-owner user
        app.dependency_overrides[get_current_tre_user] = non_owner_user
        yield
        app.dependency_overrides = {}

    async def test_post_workspace_requires_admin_rights(self, app, client):
        response = await client.post(app.url_path_for(strings.API_CREATE_WORKSPACE), json='{}')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_patch_workspace_requires_admin_rights(self, app, client):
        response = await client.patch(app.url_path_for(strings.API_UPDATE_WORKSPACE, workspace_id=WORKSPACE_ID), json='{}')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_delete_workspace_requires_admin_rights(self, app, client):
        response = await client.delete(app.url_path_for(strings.API_DELETE_WORKSPACE, workspace_id=WORKSPACE_ID))
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestWorkspaceServiceOwnerRoutesAccess:
    @pytest.fixture(autouse=True, scope='class')
    def log_in_with_non_owner(self, app, non_owner_user):
        # try accessing the route with a non-admin user
        app.dependency_overrides[get_current_ws_user] = non_owner_user
        yield
        app.dependency_overrides = {}

    # [POST] /workspaces/{workspace_id}/workspace-services/
    @patch("api.dependencies.workspaces.WorkspaceServiceRepository.get_workspace_service_by_id", return_value=sample_workspace_service())
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_deployed_workspace_by_id", return_value=sample_workspace())
    async def test_post_workspace_service_raises_403_if_user_is_not_owner(self, __, ___, app, client):
        workspace_service_input = {
            "workspaceServiceType": "test-workspace-service",
            "properties": {
                "display_name": "display",
                "app_id": "f0acf127-a672-a672-a672-a15e5bf9f127"
            }
        }
        response = await client.post(app.url_path_for(strings.API_CREATE_WORKSPACE_SERVICE, workspace_id=WORKSPACE_ID), json=workspace_service_input)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("api.dependencies.workspaces.WorkspaceServiceRepository.get_workspace_service_by_id", return_value=None)
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=sample_workspace())
    async def test_delete_workspace_service_raises_403_if_user_is_not_workspace_owner(self, _, __, app, client) -> None:
        response = await client.delete(app.url_path_for(strings.API_DELETE_WORKSPACE_SERVICE, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID))
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestWorkspaceServiceOwnerOrResearcherRoutesAccess:
    @pytest.fixture(autouse=True, scope='class')
    def log_in_with_non_owner_or_researcher(self, app, no_workspace_role_user):
        # try accessing the route with a non-admin user
        app.dependency_overrides[get_current_ws_user] = no_workspace_role_user
        yield
        app.dependency_overrides = {}

    # [GET] /workspaces/{workspace_id}/workspace-services
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=None)
    @patch("api.routes.workspaces.WorkspaceServiceRepository.get_active_workspace_services_for_workspace", return_value=[])
    async def test_get_workspace_services_raises_403_if_user_is_not_owner_or_researcher_of_workspace(self, _, __, app, client):
        response = await client.get(app.url_path_for(strings.API_GET_ALL_WORKSPACE_SERVICES, workspace_id=WORKSPACE_ID))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # [GET] /workspaces/{workspace_id}/workspace-services/{service_id}
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=None)
    @patch("api.dependencies.workspaces.WorkspaceServiceRepository.get_workspace_service_by_id", return_value=sample_workspace_service())
    async def test_get_workspace_service_raises_403_if_user_is_not_owner_or_researcher_in_workspace(self, _, __, app, client):
        response = await client.get(app.url_path_for(strings.API_GET_WORKSPACE_SERVICE_BY_ID, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # [PATCH] /workspaces/{workspace_id}/services/{service_id}
    @patch("api.dependencies.workspaces.WorkspaceServiceRepository.get_workspace_service_by_id", return_value=None)
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=sample_workspace())
    async def test_patch_workspaces_service_raises_403_if_user_is_not_workspace_owner(self, _, __, app, client) -> None:
        response = await client.patch(app.url_path_for(strings.API_UPDATE_WORKSPACE_SERVICE, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID), json={"enabled": False})
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserResourcesOwnerOrResearcherRoutesAccess:
    @pytest.fixture(autouse=True, scope='class')
    def log_in_with_non_owner_or_researcher(self, app, no_workspace_role_user):
        # try accessing the route with a non-admin user
        app.dependency_overrides[get_current_ws_user] = no_workspace_role_user
        yield
        app.dependency_overrides = {}

    # [GET] /workspaces/{workspace_id}/workspace-services/{service_id}/user-resources/{resource_id}
    @patch("api.dependencies.workspaces.UserResourceRepository.get_user_resource_by_id")
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=None)
    async def test_get_user_resource_raises_403_if_user_is_not_workspace_owner_or_researcher(self, _, __, app,
                                                                                             client):
        response = await client.get(
            app.url_path_for(strings.API_GET_USER_RESOURCE, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID,
                             resource_id=USER_RESOURCE_ID))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # [GET] /workspaces/{workspace_id}/workspace-services/{service_id}/user-resources
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=None)
    @patch("api.routes.workspaces.UserResourceRepository.get_user_resources_for_workspace_service")
    async def test_get_user_resources_raises_403_if_user_is_not_researcher_or_owner_of_workspace(self, __, get_user_resources_mock, app, client):
        get_user_resources_mock.return_value = [sample_user_resource()]
        response = await client.get(app.url_path_for(strings.API_GET_MY_USER_RESOURCES, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # [POST] /workspaces/{workspace_id}/workspace-services/{service_id}/user-resources
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_deployed_workspace_by_id", return_value=None)
    @patch("api.dependencies.workspaces.WorkspaceServiceRepository.get_deployed_workspace_service_by_id", return_value=None)
    async def test_post_user_resource_raises_403_if_user_is_not_workspace_owner_or_researcher(self, _, __, app, client):
        input_data = {
            "userResourceType": "test-user-resource",
            "properties": {"display_name": "display"}
        }
        response = await client.post(app.url_path_for(strings.API_CREATE_USER_RESOURCE, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID), json=input_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # [PATCH] /workspaces/{workspace_id}/workspace-services/{service_id}/user-resources/{resource_id}
    @patch("api.dependencies.workspaces.UserResourceRepository.get_user_resource_by_id")
    @patch("api.dependencies.workspaces.WorkspaceServiceRepository.get_workspace_service_by_id")
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=None)
    async def test_patch_user_resource_raises_403_if_user_is_not_workspace_owner_or_researcher(self, _, __, ___,app, client):
        response = await client.patch(app.url_path_for(strings.API_UPDATE_USER_RESOURCE, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID, resource_id=USER_RESOURCE_ID), json={"enabled": False})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # [DELETE] /workspaces/{workspace_id}/workspace-services/{service_id}/user-resources/{resource_id}
    @patch("api.dependencies.workspaces.UserResourceRepository.get_user_resource_by_id")
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=None)
    async def test_delete_user_resource_raises_403_if_user_is_not_workspace_owner_or_researcher(self, _, __,
                                                                                                app, client):
        response = await client.delete(
            app.url_path_for(strings.API_DELETE_USER_RESOURCE, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID,
                             resource_id=USER_RESOURCE_ID))
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserResourcesRoutesOwnerOrResourceOwnerAccess:
    @pytest.fixture(autouse=True, scope='class')
    def log_in_with_non_owner(self, app, non_owner_user):
        # try accessing the route with a non-admin user
        app.dependency_overrides[get_current_ws_user] = non_owner_user
        yield
        app.dependency_overrides = {}

    # [GET] /workspaces/{workspace_id}/workspace-services/{service_id}/user-resources/{resource_id}
    @patch("api.dependencies.workspaces.UserResourceRepository.get_user_resource_by_id")
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=None)
    async def test_get_user_resource_raises_403_if_user_is_researcher_and_not_owner_of_resource(self, _, get_user_resource_mock, app, client):
        user_resource = sample_user_resource()
        user_resource.ownerId = "11111"  # not users id
        get_user_resource_mock.return_value = user_resource

        response = await client.get(app.url_path_for(strings.API_GET_USER_RESOURCE, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID, resource_id=USER_RESOURCE_ID))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    # [DELETE] /workspaces/{workspace_id}/workspace-services/{service_id}/user-resources/{resource_id}
    @patch("api.dependencies.workspaces.UserResourceRepository.get_user_resource_by_id")
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=None)
    async def test_delete_user_resource_raises_403_if_user_is_researcher_and_not_owner_of_resource(self, _, get_user_resource_mock, app, client):
        user_resource = sample_user_resource()
        user_resource.ownerId = "11111"  # not users id
        get_user_resource_mock.return_value = user_resource

        response = await client.delete(app.url_path_for(strings.API_DELETE_USER_RESOURCE, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID, resource_id=USER_RESOURCE_ID))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    # [PATCH] /workspaces/{workspace_id}/workspace-services/{service_id}/user-resources/{resource_id}
    @patch("api.dependencies.workspaces.UserResourceRepository.get_user_resource_by_id")
    @patch("api.dependencies.workspaces.WorkspaceServiceRepository.get_workspace_service_by_id")
    @patch("api.dependencies.workspaces.WorkspaceRepository.get_workspace_by_id", return_value=None)
    async def test_patch_user_resource_raises_403_if_user_is_researcher_and_not_owner_of_resource(self, _, __, get_user_resource_mock, app, client):
        user_resource = sample_user_resource()
        user_resource.ownerId = "11111"  # not users id
        get_user_resource_mock.return_value = user_resource

        response = await client.patch(app.url_path_for(strings.API_UPDATE_USER_RESOURCE, workspace_id=WORKSPACE_ID, service_id=SERVICE_ID, resource_id=USER_RESOURCE_ID), json={"enabled": False})

        assert response.status_code == status.HTTP_403_FORBIDDEN

