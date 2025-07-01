from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QHBoxLayout, QMessageBox, QDialog,
    QFormLayout, QComboBox, QSpinBox
)
from PySide6.QtGui import QFont

from controllers.commande_controller import CommandeController
from controllers.commande_item_controller import CommandeItemController
from controllers.produit_controller import ProduitController
from controllers.reservation_controller import ReservationController


class RestaurationPage(QWidget):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        self.load_commandes()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Gestion de la Restauration")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        layout.addWidget(title)

        # Actions
        action_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.load_commandes)
        btn_ajouter = QPushButton("➕ Nouvelle Commande")
        btn_ajouter.clicked.connect(self.ajouter_commande)
        action_layout.addWidget(btn_refresh)
        action_layout.addStretch()
        action_layout.addWidget(btn_ajouter)
        layout.addLayout(action_layout)

        # Tableau des commandes
        self.table = QTableWidget()
        # --- MODIFICATION : Ajout de la colonne Statut ---
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Client", "Chambre", "Plat/Produit", "Qté", "Prix Total", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnWidth(3, 60)  # Quantité
        self.table.setColumnWidth(6, 200)  # Actions (plus large)
        layout.addWidget(self.table)

    def load_commandes(self):
        """Charge les articles des commandes du restaurant depuis la base de données."""
        self.table.setRowCount(0)
        result = CommandeItemController.liste_items_details_par_lieu("Restaurant")

        if not result.get("success"):
            QMessageBox.warning(self, "Erreur", result.get("error", "Impossible de charger les commandes."))
            return

        commandes = result.get("data", [])
        for row, item in enumerate(commandes):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(item.get("client_nom", "N/A")))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("chambre_numero", "?")))
            self.table.setItem(row, 2, QTableWidgetItem(item.get("produit_nom", "Inconnu")))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.get("quantite", 0))))

            total = item.get("quantite", 0) * item.get("prix_unitaire_capture", 0)
            self.table.setItem(row, 4, QTableWidgetItem(f"{total:,.0f} FCFA"))

            # --- MODIFICATION : Affichage du statut de la commande ---
            statut = item.get("commande_statut", "Inconnu")
            self.table.setItem(row, 5, QTableWidgetItem(statut))

            # --- MODIFICATION : Création des boutons d'action dynamiques ---
            self.create_action_buttons(row, item)

    def ajouter_commande(self):
        """Ouvre une boîte de dialogue pour ajouter une nouvelle commande."""
        dialog = RestaurationFormDialog(self, self.user_id)
        if dialog.exec():
            self.load_commandes()

    # --- NOUVEAU : Méthode pour créer les boutons d'action en fonction du statut ---
    def create_action_buttons(self, row, item):
        statut = item.get("commande_statut")
        commande_id = item.get("commande_id")
        item_id = item.get("item_id")

        cell_widget = QWidget()
        h_layout = QHBoxLayout(cell_widget)
        h_layout.setContentsMargins(5, 0, 5, 0)
        h_layout.setSpacing(5)

        if statut == 'Commandé':
            btn_cuisine = QPushButton("👨‍🍳 En Cuisine")
            btn_cuisine.clicked.connect(lambda _, cid=commande_id: self.changer_statut_commande(cid, "En cuisine"))
            h_layout.addWidget(btn_cuisine)

            btn_annuler_item = QPushButton("❌")
            btn_annuler_item.setToolTip("Annuler cet article de la commande")
            btn_annuler_item.clicked.connect(lambda _, iid=item_id: self.supprimer_item(iid))
            h_layout.addWidget(btn_annuler_item)


        elif statut == 'En cuisine':
            btn_recu = QPushButton("✅ Livré")
            btn_recu.clicked.connect(lambda _, cid=commande_id: self.changer_statut_commande(cid, "Livré"))
            h_layout.addWidget(btn_recu)

        # Si le statut est 'Livré' ou 'Annulé', on ne met aucun bouton.
        else:
            label_final = QLabel(f"Commande {statut}")
            label_final.setFont(QFont("Segoe UI", 9, italic=True))
            h_layout.addWidget(label_final)

        h_layout.addStretch()
        self.table.setCellWidget(row, 6, cell_widget)

    # --- NOUVEAU : Méthode pour gérer le changement de statut ---
    def changer_statut_commande(self, commande_id, nouveau_statut):
        confirm = QMessageBox.question(self, "Confirmation",
                                       f"Passer la commande #{commande_id} au statut '{nouveau_statut}' ?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            res = CommandeController.modifier_statut(commande_id, nouveau_statut)
            if res.get("success"):
                QMessageBox.information(self, "Succès", "Statut de la commande mis à jour.")
                self.load_commandes()
            else:
                QMessageBox.warning(self, "Erreur", res.get("error", "Erreur lors de la mise à jour du statut."))

    def supprimer_item(self, item_id):
        """Logique pour supprimer un article d'une commande."""
        rep = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment annuler cet article ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            res = CommandeItemController.supprimer_item(item_id)
            if res.get("success"):
                QMessageBox.information(self, "Succès", "Article annulé.")
                self.load_commandes()
            else:
                QMessageBox.warning(self, "Erreur", res.get("error", "Erreur lors de l'annulation."))

class RestaurationFormDialog(QDialog):
    """Dialogue pour créer une nouvelle commande de restauration."""

    def __init__(self, parent=None, user_id=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Ajouter une Commande Restaurant")
        self.setMinimumWidth(450)

        layout = QFormLayout(self)

        self.combo_resa = QComboBox()
        self.combo_produit = QComboBox()
        self.input_qte = QSpinBox()
        self.input_qte.setMinimum(1)

        layout.addRow("Client (Chambre - Nom):", self.combo_resa)
        layout.addRow("Plat / Produit:", self.combo_produit)
        layout.addRow("Quantité:", self.input_qte)

        btn_valider = QPushButton("Valider la commande")
        btn_valider.clicked.connect(self.valider)
        layout.addRow(btn_valider)

        self.load_reservations()
        self.load_produits()

    def load_reservations(self):
        """Charge uniquement les clients actuellement en 'check-in'."""
        self.combo_resa.clear()
        result = ReservationController.list_reservations(filtre={"statuts": ["check-in"]})
        if result.get("success"):
            for resa in result["data"]:
                label = f"Chambre {resa.get('chambre', '?')} - {resa.get('client', 'N/A')}"
                self.combo_resa.addItem(label, resa["id"])
        if self.combo_resa.count() == 0:
            self.combo_resa.addItem("Aucun client à facturer", None)
            self.combo_resa.setEnabled(False)

    def load_produits(self):
        """Charge les produits de type nourriture."""
        self.combo_produit.clear()
        result = ProduitController.liste_produits()
        if result.get("success"):
            # On filtre pour ne garder que la nourriture
            food_categories = ['Entrée', 'Plat', 'Dessert', 'Snack']
            for p in result["data"]:
                if p["disponible"] and p["categorie"] in food_categories:
                    self.combo_produit.addItem(f"{p['nom']} - {p['prix_unitaire']} FCFA", p)

    def valider(self):
        reservation_id = self.combo_resa.currentData()
        produit = self.combo_produit.currentData()
        quantite = self.input_qte.value()

        if not reservation_id or not produit:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un client et un produit.")
            return

        # Logique "Trouver ou Créer" une commande pour le restaurant
        commande_res = CommandeController.get_or_create_commande(
            reservation_id, self.user_id, "Restaurant"
        )

        if not commande_res.get("success"):
            QMessageBox.critical(self, "Erreur Critique", commande_res.get("error"))
            return

        commande_id = commande_res.get("id")

        # Ajouter l'article à cette commande
        item_res = CommandeItemController.ajouter_item(
            commande_id, produit["id"], quantite, produit["prix_unitaire"]
        )

        if item_res.get("success"):
            QMessageBox.information(self, "Succès", "La commande a été ajoutée.")
            self.accept()  # Ferme le dialogue avec succès
        else:
            QMessageBox.warning(self, "Erreur", item_res.get("error"))
