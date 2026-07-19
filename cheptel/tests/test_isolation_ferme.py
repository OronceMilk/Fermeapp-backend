import pytest
from django.urls import reverse
from django.test import Client
from cheptel.models import Animal

pytestmark = pytest.mark.django_db

def test_utilisateur_ne_voit_pas_animaux_autre_ferme(ferme, ferme_autre, espece, admin_user):
    # Créer un animal dans l'autre ferme
    animal_autre = Animal.objects.create(
        identifiant="AN-ISOLATION",
        ferme=ferme_autre,
        espece=espece,
        sexe="F",
    )

    # Se connecter avec un utilisateur de la ferme principale
    client = Client()
    client.force_login(admin_user)  # admin_user appartient à `ferme`

    # Accéder à la liste des animaux
    response = client.get(reverse("cheptel:animal_list"))

    assert response.status_code == 200
    # Vérifier que l'animal de l'autre ferme n'est pas dans la liste
    animaux_dans_context = response.context.get("animaux", [])
    assert animal_autre not in animaux_dans_context