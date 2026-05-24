# accounts/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    """Vérifie que l'utilisateur a le rôle ADMIN"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role != 'ADMIN':
            messages.error(request, "⛔ Accès refusé. Cette action est réservée aux administrateurs.")
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper