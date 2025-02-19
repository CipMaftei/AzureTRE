
from fastapi import HTTPException, status

from models.schemas.workspace import AuthProvider
from resources import strings
from services.aad_authentication import AzureADAuthorization
from services.access_service import AccessService, AuthConfigValidationError


def extract_auth_information(app_id: str) -> dict:
    access_service = get_access_service('AAD')
    try:
        auth_config = {'app_id': app_id}
        return access_service.extract_workspace_auth_information(auth_config)
    except AuthConfigValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def get_access_service(provider: str = AuthProvider.AAD) -> AccessService:
    if provider == AuthProvider.AAD:
        return AzureADAuthorization()
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.INVALID_AUTH_PROVIDER)


get_current_tre_user = AzureADAuthorization(require_one_of_roles=['TREUser'])


get_current_admin_user = AzureADAuthorization(require_one_of_roles=['TREAdmin'])


get_current_tre_user_or_tre_admin = AzureADAuthorization(require_one_of_roles=['TREUser', 'TREAdmin'])


get_current_workspace_owner_user = AzureADAuthorization(require_one_of_roles=['WorkspaceOwner'])


get_current_workspace_researcher_user = AzureADAuthorization(require_one_of_roles=['WorkspaceResearcher'])


get_current_workspace_owner_or_researcher_user = AzureADAuthorization(require_one_of_roles=['WorkspaceOwner', 'WorkspaceResearcher'])


get_current_workspace_owner_or_researcher_user_or_tre_admin = AzureADAuthorization(require_one_of_roles=["TREAdmin", "WorkspaceOwner", "WorkspaceResearcher"])


get_current_workspace_owner_or_tre_admin = AzureADAuthorization(require_one_of_roles=["TREAdmin", "WorkspaceOwner"])
