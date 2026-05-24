def user_role(request):
    """Ajoute le rôle de l'utilisateur au contexte des templates"""
    if request.user.is_authenticated:
        # Logique pour déterminer le rôle (ADMIN/EMPLOYÉ)
        role = 'ADMIN' if request.user.is_superuser else 'EMPLOYÉ'
        return {'user_role': role}
    return {'user_role': None}