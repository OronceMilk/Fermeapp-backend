from django.contrib import admin
from .models import Espece, Animal, LotPondeuses, Traitement, ComptageOeufs
from .models import Produit

admin.site.register(Produit)

@admin.register(Espece)
class EspeceAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)


@admin.register(LotPondeuses)
class LotPondeusesAdmin(admin.ModelAdmin):
    list_display = ('nom', 'espece', 'nombre_sujets', 'date_mise_en_place')
    list_filter = ('espece',)
    search_fields = ('nom',)


@admin.register(Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('identifiant', 'nom', 'espece', 'sexe', 'statut', 'date_arrivee')
    list_filter = ('espece', 'statut', 'sexe')
    search_fields = ('identifiant', 'nom')
    readonly_fields = ('date_arrivee',)


@admin.register(Traitement)
class TraitementAdmin(admin.ModelAdmin):
    list_display = ('animal', 'type', 'date', 'produit')
    list_filter = ('type', 'date')
    search_fields = ('produit',)


@admin.register(ComptageOeufs)
class ComptageOeufsAdmin(admin.ModelAdmin):
    list_display = ('lot', 'date', 'nombre')
    list_filter = ('date',)