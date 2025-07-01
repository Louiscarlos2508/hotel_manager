from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QSpinBox, QComboBox, QHeaderView
)
from PySide6.QtGui import QFont
from controllers.commande_controller import CommandeController
from controllers.commande_item_controller import CommandeItemController
from controllers.produit_controller import ProduitController
from controllers.reservation_controller import ReservationController
from models.produit_model import ProduitModel


class BarPage(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.commande_id = None  # Commande Bar liée à la réservation sélectionnée
        self.current_item_id = None  # Pour une future édition

        self.setLayout(QVBoxLayout())
        title = QLabel("Bar – Commandes")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.layout().addWidget(title)

        self.init_form()
        self.init_table()

        # On charge les données après avoir initialisé l'UI
        self.load_produits()
        self.load_reservations()  # Ceci va déclencher le reste de la logique

    def init_form(self):
        form_layout = QHBoxLayout()

        self.combo_resa = QComboBox()
        self.combo_resa.currentIndexChanged.connect(self.reservation_changed)
        form_layout.addWidget(QLabel("Client (Chambre - Nom):"))
        form_layout.addWidget(self.combo_resa, 2)  # Donne plus d'espace

        self.combo_produit = QComboBox()
        form_layout.addWidget(QLabel("Produit:"))
        form_layout.addWidget(self.combo_produit, 2)  # Donne plus d'espace

        self.input_qte = QSpinBox()
        self.input_qte.setMinimum(1)
        self.input_qte.setMaximum(99)
        form_layout.addWidget(QLabel("Quantité:"))
        form_layout.addWidget(self.input_qte, 1)

        self.btn_ajouter = QPushButton("➕ Ajouter")
        self.btn_ajouter.clicked.connect(self.ajouter_ou_modifier_item)
        form_layout.addWidget(self.btn_ajouter)

        self.layout().addLayout(form_layout)

    def init_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Produit", "Quantité", "P.U.", "Total", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnWidth(0, 50)  # ID
        self.table.setColumnWidth(2, 80)  # Quantité
        self.table.setColumnWidth(5, 100)  # Actions
        self.layout().addWidget(self.table)

    def load_reservations(self):
        """Charge uniquement les réservations avec le statut 'check-in'."""
        # --- RÈGLE MÉTIER APPLIQUÉE ICI ---
        filtre = {"statuts": ["check-in"]}
        result = ReservationController.list_reservations(filtre=filtre)

        self.combo_resa.clear()
        self.combo_resa.addItem("--- Sélectionner un client ---", None)

        if result.get("success"):
            reservations = result["data"]
            if not reservations:
                self.set_form_enabled(False)  # Désactive le formulaire si personne n'est là
            else:
                self.set_form_enabled(True)

            for resa in reservations:
                # Label plus informatif pour l'utilisateur
                label = f"Chambre {resa.get('chambre', '?')} - {resa.get('client', 'N/A')}"
                self.combo_resa.addItem(label, resa["id"])
        else:
            QMessageBox.warning(self, "Erreur", result.get("error", "Erreur chargement réservations."))

    def load_produits(self):
        """
        Charge uniquement les produits de type 'boisson' qui sont disponibles.
        """
        self.combo_produit.clear()

        # --- MODIFICATION : Définir les catégories de boissons autorisées ---
        drink_categories = ['Boisson chaude', 'Boisson fraîche', 'Alcool']

        try:
            result = ProduitController.liste_produits()
            if result.get("success"):
                # On parcourt tous les produits récupérés
                for p in result["data"]:
                    # --- MODIFICATION : On ajoute la condition sur la catégorie ici ---
                    if p["disponible"] and p.get("categorie") in drink_categories:
                        self.combo_produit.addItem(f"{p['nom']} - {p['prix_unitaire']} FCFA", p)
            else:
                raise Exception(result.get("error"))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur chargement produits : {e}")

    def reservation_changed(self):
        """Appelé quand l'utilisateur change de réservation dans la liste."""
        resa_id = self.combo_resa.currentData()
        if not resa_id:
            self.commande_id = None
            self.table.setRowCount(0)  # Vide la table si aucune réservation n'est sélectionnée
            return

        # --- LOGIQUE "TROUVER OU CRÉER" APPLIQUÉE ICI ---
        result = CommandeController.get_or_create_commande(resa_id, self.user_id, "Bar")

        if result.get("success"):
            self.commande_id = result["id"]
            self.load_items()
        else:
            QMessageBox.warning(self, "Erreur", result.get("error", "Erreur gestion de la commande."))
            self.commande_id = None
            self.table.setRowCount(0)

    def ajouter_ou_modifier_item(self):
        produit = self.combo_produit.currentData()
        if not produit:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un produit.")
            return

        quantite = self.input_qte.value()
        if quantite <= 0:
            QMessageBox.warning(self, "Erreur", "La quantité doit être supérieure à zéro.")
            return

        if not self.commande_id:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord sélectionner un client.")
            return

        if self.current_item_id:
            QMessageBox.information(self, "Info", "L'édition d'article n'est pas encore implémentée.")
        else:
            res = CommandeItemController.ajouter_item(
                self.commande_id, produit["id"], quantite, produit["prix_unitaire"]
            )
            if res.get("success"):
                self.reset_form()
                self.load_items()
            else:
                QMessageBox.warning(self, "Erreur", res.get("error", "Erreur lors de l'ajout de l'article."))

    def load_items(self):
        """Charge les articles de la commande actuellement sélectionnée."""
        self.table.setRowCount(0)
        if not self.commande_id:
            return

        res = CommandeItemController.liste_items(self.commande_id)
        if not res.get("success"):
            QMessageBox.warning(self, "Erreur", res.get("error", "Erreur chargement articles."))
            return

        items = res.get("data", [])
        for row, item in enumerate(items):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["produit_nom"]))
            self.table.setItem(row, 2, QTableWidgetItem(str(item["quantite"])))
            self.table.setItem(row, 3, QTableWidgetItem(f"{item['prix_unitaire_capture']:,.0f}"))
            total = item["quantite"] * item["prix_unitaire_capture"]
            self.table.setItem(row, 4, QTableWidgetItem(f"{total:,.0f}"))

            btn_supp = QPushButton("🗑️ Supprimer")
            btn_supp.clicked.connect(lambda _, iid=item["id"]: self.supprimer_item(iid))
            self.table.setCellWidget(row, 5, btn_supp)

    def supprimer_item(self, item_id):
        rep = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment supprimer cet article ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            res = CommandeItemController.supprimer_item(item_id)
            if res.get("success"):
                self.load_items()
            else:
                QMessageBox.warning(self, "Erreur", res.get("error", "Erreur lors de la suppression."))

    def reset_form(self):
        self.input_qte.setValue(1)
        self.combo_produit.setCurrentIndex(0)
        self.current_item_id = None
        self.btn_ajouter.setText("➕ Ajouter")

    def set_form_enabled(self, enabled: bool):
        """Active ou désactive les widgets du formulaire."""
        self.combo_produit.setEnabled(enabled)
        self.input_qte.setEnabled(enabled)
        self.btn_ajouter.setEnabled(enabled)
        if not enabled:
            self.combo_resa.setCurrentIndex(0)
            self.combo_resa.setToolTip("Aucun client n'est actuellement en statut 'check-in'.")