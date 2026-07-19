from decimal import Decimal

from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.models import Ferme, User
from stocks.models import MouvementStock, ProduitStock
from stocks.services import StockService
from stocks import views


class StockViewsTest(TestCase):
    def setUp(self):
        self.ferme = Ferme.objects.create(
            nom="Ferme Stock",
            localisation="Porto-Novo",
            email="stock@example.com",
        )
        self.user = User.objects.create_user(
            username="adminstock",
            password="pass123",
            role="ADMIN",
            ferme=self.ferme,
        )
        self.factory = RequestFactory()
        self.produit = ProduitStock.objects.create(
            ferme=self.ferme,
            nom="Aliment pondeuse",
            unite="KG",
            quantite_actuelle=Decimal("10.00"),
            seuil_alerte=Decimal("3.00"),
            emplacement="Magasin",
        )

    def build_request(self, method, path):
        request = getattr(self.factory, method.lower())(path)
        request.user = self.user
        SessionMiddleware(lambda req: None).process_request(request)
        request.session.save()
        request._messages = FallbackStorage(request)
        return request

    def test_stock_dashboard_and_partials_render(self):
        view_calls = [
            (views.stock_dashboard, reverse("stocks:dashboard")),
            (views.aliments_partial, reverse("stocks:aliments_partial")),
            (views.semences_partial, reverse("stocks:semences_partial")),
        ]

        for view, url in view_calls:
            with self.subTest(url=url):
                response = view(self.build_request("get", url))
                self.assertEqual(response.status_code, 200)

    def test_delete_entree_mouvement_compensates_stock(self):
        mouvement = MouvementStock.objects.create(
            produit=self.produit,
            type="ENTREE",
            quantite=Decimal("4.00"),
            stock_avant=Decimal("10.00"),
            stock_apres=Decimal("14.00"),
            created_by=self.user,
        )
        self.produit.quantite_actuelle = Decimal("14.00")
        self.produit.save(update_fields=["quantite_actuelle"])

        response = views.mouvement_delete(
            self.build_request("post", reverse("stocks:mouvement_delete", args=[mouvement.pk])),
            mouvement.pk,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("stocks:mouvement_list"))
        self.produit.refresh_from_db()
        self.assertEqual(self.produit.quantite_actuelle, Decimal("10.00"))
        self.assertFalse(MouvementStock.objects.filter(pk=mouvement.pk).exists())

    def test_service_uses_today_when_date_is_missing(self):
        mouvement = StockService.creer_mouvement(
            produit_id=self.produit.id,
            type_mouvement="ENTREE",
            quantite=Decimal("2.00"),
            user=self.user,
        )

        self.assertIsNotNone(mouvement.date)
