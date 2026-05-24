# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Ferme


# ==============================
# ADMIN FERME
# ==============================
@admin.register(Ferme)
class FermeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'localisation', 'email', 'telephone', 'created_at')
    search_fields = ('nom', 'email', 'localisation')


# ==============================
# ADMIN USER
# ==============================
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        'username',
        'email',
        'role',
        'ferme',
        'is_staff',
        'is_active',
    )

    list_filter = (
        'role',
        'ferme',
        'is_staff',
        'is_active',
    )

    search_fields = (
        'username',
        'email',
        'ferme__nom',
    )

    ordering = ('username',)

    # ==============================
    # FORMULAIRE D'AJOUT (IMPORTANT !)
    # ==============================
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'email',
                'phone',
                'adresse',
                'role',
                'ferme',
                'is_active',
                'is_staff',
            ),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),

        ('Informations personnelles', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone',
                'adresse',
                'ferme',
                'role',
            )
        }),

        ('Permissions', {
            'fields': (
                'is_staff',
                'is_active',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),

        ('Dates importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # ==============================
    # FILTRAGE PAR FERME
    # ==============================
    def get_queryset(self, request):
        """Filtre les utilisateurs par ferme (sauf superuser)"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(ferme=request.user.ferme)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limite le choix des fermes dans les formulaires"""
        if db_field.name == "ferme" and not request.user.is_superuser:
            kwargs["queryset"] = Ferme.objects.filter(id=request.user.ferme.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)