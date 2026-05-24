# cheptel/management/commands/seed_especes.py
from django.core.management.base import BaseCommand
from cheptel.models import Espece

class Command(BaseCommand):
    help = 'Ajoute les espèces par défaut'

    def handle(self, *args, **kwargs):
        especes = [
            'Poulet', 'Lapin', 'Canard', 'Dinde', 
            'Mouton', 'Chèvre', 'Vache', 'Porc', 
            'Oie', 'Pintade'
        ]
        
        for nom in especes:
            espece, created = Espece.objects.get_or_create(nom=nom)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Espèce ajoutée : {nom}'))
            else:
                self.stdout.write(f'• Espèce existante : {nom}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Initialisation terminée !'))