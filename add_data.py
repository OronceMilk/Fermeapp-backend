from fermeapp.fermeapp.models import Animal, Traitement
from datetime import datetime, timedelta
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fermeapp.settings')
django.setup()

# Ajouter des animaux d'exemple
animals_data = [
    {
        'nom': 'Bella',
        'numero_identification': 'COW-001',
        'espece': 'bovine',
        'sexe': 'femelle',
        'date_naissance': '2021-03-15',
        'poids': 650.0,
        'statut': 'actif',
        'lot': 'Lot A',
        'notes': 'Vache laitière très productive'
    },
    {
        'nom': 'Taureau Max',
        'numero_identification': 'COW-002',
        'espece': 'bovine',
        'sexe': 'male',
        'date_naissance': '2020-06-20',
        'poids': 800.0,
        'statut': 'actif',
        'lot': 'Lot A',
        'notes': 'Reproducteur premium'
    },
    {
        'nom': 'Stella',
        'numero_identification': 'SHEEP-001',
        'espece': 'ovine',
        'sexe': 'femelle',
        'date_naissance': '2022-02-10',
        'poids': 65.0,
        'statut': 'actif',
        'lot': 'Lot B',
        'notes': 'Brebis de reproduction'
    },
    {
        'nom': 'Babar',
        'numero_identification': 'SHEEP-002',
        'espece': 'ovine',
        'sexe': 'male',
        'date_naissance': '2021-01-05',
        'poids': 85.0,
        'statut': 'actif',
        'lot': 'Lot B',
        'notes': 'Bélier robuste'
    },
    {
        'nom': 'Coco',
        'numero_identification': 'CHICKEN-001',
        'espece': 'volaille',
        'sexe': 'femelle',
        'date_naissance': '2023-09-12',
        'poids': 2.5,
        'statut': 'actif',
        'lot': 'Lot C',
        'notes': 'Poule pondeuse'
    },
    {
        'nom': 'Rusty',
        'numero_identification': 'PIG-001',
        'espece': 'porcine',
        'sexe': 'male',
        'date_naissance': '2023-05-08',
        'poids': 120.0,
        'statut': 'vendu',
        'lot': 'Lot D',
        'notes': 'Vendu en avril 2026'
    },
]

# Créer les animaux
created_animals = []
for data in animals_data:
    animal, created = Animal.objects.get_or_create(
        numero_identification=data['numero_identification'],
        defaults=data
    )
    if created:
        created_animals.append(animal)
        print(f"✓ Animal créé: {animal.nom} ({animal.numero_identification})")
    else:
        print(f"✗ Animal existe déjà: {animal.nom}")

# Ajouter des traitements d'exemple
treatments = [
    {
        'animal_id': 1,
        'type_traitement': 'vaccination',
        'description': 'Vaccination contre la fièvre aphteuse',
        'date_traitement': (datetime.now() - timedelta(days=30)).date(),
        'veterinaire': 'Dr. Dubois',
        'notes': 'Traitement régulier'
    },
    {
        'animal_id': 1,
        'type_traitement': 'medicament',
        'description': 'Antibiotique pour infection respiratoire',
        'date_traitement': (datetime.now() - timedelta(days=15)).date(),
        'veterinaire': 'Dr. Dubois',
        'notes': 'Traitement de 5 jours'
    },
    {
        'animal_id': 2,
        'type_traitement': 'examen',
        'description': 'Examen de santé annuel',
        'date_traitement': datetime.now().date(),
        'veterinaire': 'Dr. Martin',
        'notes': 'Bonne santé générale'
    },
    {
        'animal_id': 3,
        'type_traitement': 'vaccination',
        'description': 'Vaccination contre la clavelée',
        'date_traitement': (datetime.now() - timedelta(days=60)).date(),
        'veterinaire': 'Dr. Martin',
        'notes': 'Vaccination complète'
    },
]

for treatment_data in treatments:
    try:
        animal = Animal.objects.get(id=treatment_data['animal_id'])
        traitement, created = Traitement.objects.get_or_create(
            animal=animal,
            date_traitement=treatment_data['date_traitement'],
            type_traitement=treatment_data['type_traitement'],
            defaults={
                'description': treatment_data['description'],
                'veterinaire': treatment_data['veterinaire'],
                'notes': treatment_data['notes']
            }
        )
        if created:
            print(f"✓ Traitement ajouté: {animal.nom} - {traitement.get_type_traitement_display()}")
    except Exception as e:
        print(f"✗ Erreur: {e}")

print("\n✅ Données d'exemple ajoutées avec succès!")
