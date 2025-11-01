
from flask_restful import Api

from .auth import (
    LoginResource,
    RegisterResource,
    LogoutResource,
    RefreshResource
)
from .analysis_results import (
    AnalysisResultResource,
    AnalysisResultCreateResource,
    AnalysisResultUpdateResource,
    AnalysisResultDeleteResource,
    AnalysisResultListResource,
    AnalysisResultPageResource
)
from .tasks import (
    TaskResource,
    TaskCreateResource,
    TaskUpdateResource,
    TaskDeleteResource,
    TaskListResource,
    TaskPageResource
)
from .plots import (
    PlotResource,
    PlotCreateResource,
    PlotUpdateResource,
    PlotDeleteResource,
    PlotListResource,
    PlotPageResource
)
from .imagery import (
    ImageryResource,
    ImageryCreateResource,
    ImageryUpdateResource,
    ImageryDeleteResource,
    ImageryListResource,
    ImageryPageResource
)
from .flight_paths import (
    FlightPathResource,
    FlightPathCreateResource,
    FlightPathUpdateResource,
    FlightPathDeleteResource,
    FlightPathListResource,
    FlightPathPageResource
)
from .map_objects_3d import (
    MapObject3DResource,
    MapObject3DCreateResource,
    MapObject3DUpdateResource,
    MapObject3DDeleteResource,
    MapObject3DListResource,
    MapObject3DPageResource
)
from .system_menus import (
    SystemMenuResource,
    SystemMenuCreateResource,
    SystemMenuUpdateResource,
    SystemMenuDeleteResource,
    SystemMenuListResource,
    SystemMenuPageResource
)
from .system_roles import (
    SystemRoleResource,
    SystemRoleCreateResource,
    SystemRoleUpdateResource,
    SystemRoleDeleteResource,
    SystemRoleListResource,
    SystemRolePageResource
)
from .system_users import (
    SystemUserResource,
    SystemUserCreateResource,
    SystemUserUpdateResource,
    SystemUserDeleteResource,
    SystemUserListResource,
    SystemUserPageResource

)
from .system_permissions import (
    SystemPermissionResource,
    SystemPermissionCreateResource,
    SystemPermissionUpdateResource,
    SystemPermissionDeleteResource,
    SystemPermissionListResource,
    SystemPermissionPageResource
)
from .role_permissions import (
    RolePermissionResource,
    RolePermissionCreateResource,
    RolePermissionUpdateResource,
    RolePermissionDeleteResource,
    RolePermissionListResource,
    RolePermissionPageResource
)
from .user_roles import (
    UserRoleResource,
    UserRoleCreateResource,
    UserRoleUpdateResource,
    UserRoleDeleteResource,
    UserRoleListResource,
    UserRolePageResource
)

def register_resources(api: Api):
    # Auth 认证
    api.add_resource(LoginResource, '/api/auth/login')
    api.add_resource(RegisterResource, '/api/auth/register')
    api.add_resource(RefreshResource, '/api/auth/refresh')
    api.add_resource(LogoutResource, '/api/auth/logout')

    # Analysis Results
    api.add_resource(AnalysisResultResource, '/api/analysis_results/<int:result_id>')
    api.add_resource(AnalysisResultCreateResource, '/api/analysis_results/create')
    api.add_resource(AnalysisResultUpdateResource, '/api/analysis_results/update/<int:result_id>')
    api.add_resource(AnalysisResultDeleteResource, '/api/analysis_results/delete/<int:result_id>')
    api.add_resource(AnalysisResultListResource, '/api/analysis_results/list')
    api.add_resource(AnalysisResultPageResource, '/api/analysis_results/page')

    # Tasks
    api.add_resource(TaskResource, '/api/tasks/<int:task_id>')
    api.add_resource(TaskCreateResource, '/api/tasks/create')
    api.add_resource(TaskUpdateResource, '/api/tasks/update/<int:task_id>')
    api.add_resource(TaskDeleteResource, '/api/tasks/delete/<int:task_id>')
    api.add_resource(TaskListResource, '/api/tasks/list')
    api.add_resource(TaskPageResource, '/api/tasks/page')

    # Plots
    api.add_resource(PlotResource, '/api/plots/<int:plot_id>')
    api.add_resource(PlotCreateResource, '/api/plots/create')
    api.add_resource(PlotUpdateResource, '/api/plots/update/<int:plot_id>')
    api.add_resource(PlotDeleteResource, '/api/plots/delete/<int:plot_id>')
    api.add_resource(PlotListResource, '/api/plots/list')
    api.add_resource(PlotPageResource, '/api/plots/page')

    # Imagery
    api.add_resource(ImageryResource, '/api/imagery/<int:imagery_id>')
    api.add_resource(ImageryCreateResource, '/api/imagery/create')
    api.add_resource(ImageryUpdateResource, '/api/imagery/update/<int:imagery_id>')
    api.add_resource(ImageryDeleteResource, '/api/imagery/delete/<int:imagery_id>')
    api.add_resource(ImageryListResource, '/api/imagery/list')
    api.add_resource(ImageryPageResource, '/api/imagery/page')

    # Flight Paths
    api.add_resource(FlightPathResource, '/api/flight_paths/<int:flight_path_id>')
    api.add_resource(FlightPathCreateResource, '/api/flight_paths/create')
    api.add_resource(FlightPathUpdateResource, '/api/flight_paths/update/<int:flight_path_id>')
    api.add_resource(FlightPathDeleteResource, '/api/flight_paths/delete/<int:flight_path_id>')
    api.add_resource(FlightPathListResource, '/api/flight_paths/list')
    api.add_resource(FlightPathPageResource, '/api/flight_paths/page')

    # Map Objects 3D
    api.add_resource(MapObject3DResource, '/api/map_objects_3d/<int:object_id>')
    api.add_resource(MapObject3DCreateResource, '/api/map_objects_3d/create')
    api.add_resource(MapObject3DUpdateResource, '/api/map_objects_3d/update/<int:object_id>')
    api.add_resource(MapObject3DDeleteResource, '/api/map_objects_3d/delete/<int:object_id>')
    api.add_resource(MapObject3DListResource, '/api/map_objects_3d/list')
    api.add_resource(MapObject3DPageResource, '/api/map_objects_3d/page')

    # System Menus
    api.add_resource(SystemMenuResource, '/api/system_menus/<int:menu_id>')
    api.add_resource(SystemMenuCreateResource, '/api/system_menus/create')
    api.add_resource(SystemMenuUpdateResource, '/api/system_menus/update/<int:menu_id>')
    api.add_resource(SystemMenuDeleteResource, '/api/system_menus/delete/<int:menu_id>')
    api.add_resource(SystemMenuListResource, '/api/system_menus/list')
    api.add_resource(SystemMenuPageResource, '/api/system_menus/page')

    # System Roles
    api.add_resource(SystemRoleResource, '/api/system_roles/<int:role_id>')
    api.add_resource(SystemRoleCreateResource, '/api/system_roles/create')
    api.add_resource(SystemRoleUpdateResource, '/api/system_roles/update/<int:role_id>')
    api.add_resource(SystemRoleDeleteResource, '/api/system_roles/delete/<int:role_id>')
    api.add_resource(SystemRoleListResource, '/api/system_roles/list')
    api.add_resource(SystemRolePageResource, '/api/system_roles/page')

    # System Users
    api.add_resource(SystemUserResource, '/api/system_users/<int:user_id>')
    api.add_resource(SystemUserCreateResource, '/api/system_users/create')
    api.add_resource(SystemUserUpdateResource, '/api/system_users/update/<int:user_id>')
    api.add_resource(SystemUserDeleteResource, '/api/system_users/delete/<int:user_id>')
    api.add_resource(SystemUserListResource, '/api/system_users/list')
    api.add_resource(SystemUserPageResource, '/api/system_users/page')

    # System Permissions
    api.add_resource(SystemPermissionResource, '/api/system_permissions/<int:permission_id>')
    api.add_resource(SystemPermissionCreateResource, '/api/system_permissions/create')
    api.add_resource(SystemPermissionUpdateResource, '/api/system_permissions/update/<int:permission_id>')
    api.add_resource(SystemPermissionDeleteResource, '/api/system_permissions/delete/<int:permission_id>')
    api.add_resource(SystemPermissionListResource, '/api/system_permissions/list')
    api.add_resource(SystemPermissionPageResource, '/api/system_permissions/page')

    # Role Permissions
    api.add_resource(RolePermissionResource, '/api/role_permissions/<int:rp_id>')
    api.add_resource(RolePermissionCreateResource, '/api/role_permissions/create')
    api.add_resource(RolePermissionUpdateResource, '/api/role_permissions/update/<int:rp_id>')
    api.add_resource(RolePermissionDeleteResource, '/api/role_permissions/delete/<int:rp_id>')
    api.add_resource(RolePermissionListResource, '/api/role_permissions/list')
    api.add_resource(RolePermissionPageResource, '/api/role_permissions/page')

    # User Roles
    api.add_resource(UserRoleResource, '/api/user_roles/<int:ur_id>')
    api.add_resource(UserRoleCreateResource, '/api/user_roles/create')
    api.add_resource(UserRoleUpdateResource, '/api/user_roles/update/<int:ur_id>')
    api.add_resource(UserRoleDeleteResource, '/api/user_roles/delete/<int:ur_id>')
    api.add_resource(UserRoleListResource, '/api/user_roles/list')
    api.add_resource(UserRolePageResource, '/api/user_roles/page')
    # print("Registered resources:", [(res.__name__, urls) for res, urls, _ in api.resources])

    return api