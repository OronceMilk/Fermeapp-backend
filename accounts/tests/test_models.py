# accounts/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from accounts.models import User, Ferme


class FermeModelTest(TestCase):
    """Tests du modèle Ferme"""
    
    def setUp(self):
        self.ferme = Ferme.objects.create(
            nom="Ferme Test",
            localisation="Porto-Novo",
            email="contact@fermetest.com",
            telephone="+22997000000"
        )
    
    def test_creation_ferme(self):
        """Test de création d'une ferme"""
        self.assertEqual(self.ferme.nom, "Ferme Test")
        self.assertEqual(self.ferme.localisation, "Porto-Novo")
        self.assertEqual(str(self.ferme), "Ferme Test")
    
    def test_admin_principal_vide(self):
        """Une ferme sans admin retourne None"""
        self.assertIsNone(self.ferme.admin_principal)
        self.assertFalse(self.ferme.a_un_admin)
    
    def test_admin_principal_avec_admin(self):
        """Une ferme avec un admin retourne l'admin"""
        admin = User.objects.create_user(
            username="adminferme",
            password="pass123",
            email="admin@fermetest.com",
            role="ADMIN",
            ferme=self.ferme
        )
        
        self.assertEqual(self.ferme.admin_principal, admin)
        self.assertTrue(self.ferme.a_un_admin)


class UserModelTest(TestCase):
    """Tests du modèle User"""
    
    def setUp(self):
        self.ferme = Ferme.objects.create(
            nom="Ferme Benin",
            localisation="Cotonou",
            email="contact@benin.com"
        )
    
    def test_creation_employe_ok(self):
        """Création d'un employé avec ferme → OK"""
        user = User.objects.create_user(
            username="jean",
            password="pass123",
            email="jean@ferme.com",
            role="EMPLOYE",
            ferme=self.ferme
        )
        self.assertEqual(user.role, "EMPLOYE")
        self.assertEqual(user.ferme, self.ferme)
        self.assertEqual(str(user), "jean (Employé)")
    
    def test_employe_sans_ferme_erreur(self):
        """Un employé sans ferme → ValidationError"""
        user = User(
            username="pierre",
            email="pierre@ferme.com",
            role="EMPLOYE",
            ferme=None
        )
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_creation_admin_ok(self):
        """Création d'un admin avec ferme → OK"""
        admin = User.objects.create_user(
            username="admin1",
            password="pass123",
            email="admin1@ferme.com",
            role="ADMIN",
            ferme=self.ferme
        )
        self.assertEqual(admin.role, "ADMIN")
    
    def test_deux_admins_meme_ferme_erreur(self):
        """Deux admins dans la même ferme → ValidationError"""
        # Premier admin
        User.objects.create_user(
            username="admin1",
            password="pass123",
            email="admin1@ferme.com",
            role="ADMIN",
            ferme=self.ferme
        )
        
        # Deuxième admin (doit échouer)
        user2 = User(
            username="admin2",
            email="admin2@ferme.com",
            role="ADMIN",
            ferme=self.ferme
        )
        with self.assertRaises(ValidationError):
            user2.full_clean()
    
    def test_admins_fermes_differentes_ok(self):
        """Deux admins dans des fermes différentes → OK"""
        ferme2 = Ferme.objects.create(
            nom="Ferme 2",
            localisation="Parakou",
            email="contact@ferme2.com"
        )
        
        User.objects.create_user(
            username="admin1",
            password="pass123",
            email="admin1@ferme.com",
            role="ADMIN",
            ferme=self.ferme
        )
        
        user2 = User.objects.create_user(
            username="admin2",
            password="pass123",
            email="admin2@ferme2.com",
            role="ADMIN",
            ferme=ferme2
        )
        
        self.assertEqual(user2.role, "ADMIN")  # Pas d'erreur