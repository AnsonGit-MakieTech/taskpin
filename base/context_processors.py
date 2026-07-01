from .permissions import is_admin


def permissions(request):
    if not request.user.is_authenticated:
        return {'can_move_tasks': False, 'is_admin_user': False}
    admin = is_admin(request.user)
    return {
        'can_move_tasks': admin,
        'is_admin_user': admin,
    }
