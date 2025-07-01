from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
                               QHeaderView, QPushButton, QHBoxLayout, QMessageBox, QDialog,
                               QFormLayout, QTextEdit, QComboBox, QDialogButtonBox,
                               QInputDialog)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from controllers.probleme_controller import ProblemeController
# --- MODIFICATION : Import du contrôleur des chambres ---
from controllers.chambre_controller import ChambreController


# --- Boîte de dialogue pour signaler un nouveau problème (AMÉLIORÉE) ---
class NouveauProblemeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Signaler un nouveau problème")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- MODIFICATION : Remplacement du QSpinBox par une QComboBox ---
        self.chambre_combo = QComboBox()
        self.chambre_combo.setToolTip("Choisissez la chambre concernée dans la liste.")
        self.charger_liste_chambres() # Appel de la méthode pour peupler la liste

        self.description_input = QTextEdit()
        self.priorite_input = QComboBox()
        self.priorite_input.addItems(["Basse", "Moyenne", "Haute"])
        self.priorite_input.setCurrentText("Moyenne")

        form_layout.addRow("Chambre:", self.chambre_combo)
        form_layout.addRow("Description du problème:", self.description_input)
        form_layout.addRow("Priorité:", self.priorite_input)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def charger_liste_chambres(self):
        """
        Utilise le ChambreController pour récupérer et afficher les chambres.
        """
        result = ChambreController.get_all_chambres()
        if result["success"]:
            chambres = result["data"]
            if not chambres:
                self.chambre_combo.addItem("Aucune chambre trouvée", -1)
                self.chambre_combo.setEnabled(False)
            else:
                for chambre in chambres:
                    # On affiche le numéro de la chambre, mais on stocke son ID
                    self.chambre_combo.addItem(f"Chambre n° {chambre['numero']}", chambre['id'])
        else:
            # Gérer le cas où les chambres ne peuvent pas être chargées
            self.chambre_combo.addItem("Erreur de chargement", -1)
            self.chambre_combo.setEnabled(False)
            QMessageBox.critical(self, "Erreur", f"Impossible de charger la liste des chambres:\n{result['error']}")

    def get_data(self):
        """
        Récupère les données du formulaire, y compris l'ID de la chambre sélectionnée.
        """
        chambre_id = self.chambre_combo.currentData() # On récupère l'ID stocké

        if chambre_id is None or chambre_id == -1:
            QMessageBox.warning(self, "Sélection invalide", "Veuillez sélectionner une chambre valide.")
            return None

        if not self.description_input.toPlainText().strip():
            return None  # Retourne None si la description est vide

        return {
            "chambre_id": chambre_id,
            "description": self.description_input.toPlainText(),
            "priorite": self.priorite_input.currentText()
        }


# --- Page principale de gestion des problèmes (inchangée, mais bénéficie de la nouvelle dialogue) ---
class ProblemesPage(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        title = QLabel("Gestion des Problèmes et de la Maintenance")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        self.table_problemes = QTableWidget()
        self.table_problemes.setColumnCount(7)
        self.table_problemes.setHorizontalHeaderLabels([
            "ID", "N° Chambre", "Description", "Statut", "Priorité", "Signalé le", "Résolu le"
        ])
        self.table_problemes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_problemes.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_problemes.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_problemes.setColumnHidden(0, True)
        main_layout.addWidget(self.table_problemes)

        buttons_layout = QHBoxLayout()
        btn_signaler = QPushButton("➕ Signaler un problème")
        btn_changer_statut = QPushButton("🔄 Changer le statut")
        btn_supprimer = QPushButton("❌ Supprimer")

        buttons_layout.addWidget(btn_signaler)
        buttons_layout.addWidget(btn_changer_statut)
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_supprimer)
        main_layout.addLayout(buttons_layout)

        btn_signaler.clicked.connect(self.signaler_nouveau_probleme)
        btn_changer_statut.clicked.connect(self.changer_statut_probleme)
        btn_supprimer.clicked.connect(self.supprimer_probleme_selectionne)

        self.charger_problemes()

    def charger_problemes(self):
        """Charge ou recharge les données des problèmes dans le tableau."""
        result = ProblemeController.liste_problemes()
        if result["success"]:
            problemes = result["data"]
            self.table_problemes.setRowCount(len(problemes))
            for row, p in enumerate(problemes):
                self.table_problemes.setItem(row, 0, QTableWidgetItem(str(p['id'])))
                self.table_problemes.setItem(row, 1, QTableWidgetItem(str(p.get('numero_chambre', 'N/A'))))
                self.table_problemes.setItem(row, 2, QTableWidgetItem(p['description']))
                self.table_problemes.setItem(row, 3, QTableWidgetItem(p['statut']))
                self.table_problemes.setItem(row, 4, QTableWidgetItem(p['priorite']))
                self.table_problemes.setItem(row, 5, QTableWidgetItem(p['date_signalement']))
                self.table_problemes.setItem(row, 6, QTableWidgetItem(p.get('date_resolution') or "N/A"))
        else:
            QMessageBox.warning(self, "Erreur", result["error"])

    def signaler_nouveau_probleme(self):
        """Ouvre la boîte de dialogue pour signaler un nouveau problème."""
        dialog = NouveauProblemeDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data is None:
                # Le message d'erreur est déjà géré dans la dialogue, on sort juste.
                return

            result = ProblemeController.signaler_probleme(**data)
            if result["success"]:
                QMessageBox.information(self, "Succès", result["message"])
                self.charger_problemes()
            else:
                QMessageBox.warning(self, "Erreur", result["error"])

    def _get_selected_probleme_id(self):
        """Méthode utilitaire pour récupérer l'ID du problème sélectionné."""
        selected_rows = self.table_problemes.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner un problème dans la liste.")
            return None

        row = selected_rows[0].row()
        return int(self.table_problemes.item(row, 0).text())

    def changer_statut_probleme(self):
        """Change le statut du problème sélectionné."""
        probleme_id = self._get_selected_probleme_id()
        if probleme_id is None:
            return

        current_row = self.table_problemes.currentRow()
        current_statut = self.table_problemes.item(current_row, 3).text()
        statuts_possibles = ["Nouveau", "En cours", "Résolu", "Annulé"]

        try:
            current_index = statuts_possibles.index(current_statut)
        except ValueError:
            current_index = 0

        nouveau_statut, ok = QInputDialog.getItem(self, "Changer le statut",
                                                  "Choisissez le nouveau statut :",
                                                  statuts_possibles,
                                                  current_index, False)

        if ok and nouveau_statut:
            result = ProblemeController.mettre_a_jour_statut(probleme_id, nouveau_statut)
            if result["success"]:
                QMessageBox.information(self, "Succès", result["message"])
                self.charger_problemes()
            else:
                QMessageBox.warning(self, "Erreur", result["error"])

    def supprimer_probleme_selectionne(self):
        """Supprime le problème sélectionné après confirmation."""
        probleme_id = self._get_selected_probleme_id()
        if probleme_id is None:
            return

        current_row = self.table_problemes.currentRow()
        description = self.table_problemes.item(current_row, 2).text()
        reply = QMessageBox.question(self, "Confirmation",
                                     f"Êtes-vous sûr de vouloir supprimer le problème N°{probleme_id} ?\n\n'{description}'",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            result = ProblemeController.supprimer_probleme(probleme_id)
            if result["success"]:
                QMessageBox.information(self, "Succès", result["message"])
                self.charger_problemes()
            else:
                QMessageBox.warning(self, "Erreur", result["error"])
