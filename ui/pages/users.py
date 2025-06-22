from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLineEdit, QComboBox, QHBoxLayout, QCheckBox, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from controllers.user_controller import UserController


class EditUserDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifier utilisateur")
        self.setModal(True)
        self.user_data = user_data

        self.layout = QVBoxLayout(self)

        form = QFormLayout()
        self.input_nom_complet = QLineEdit(user_data.get("nom_complet", ""))
        self.input_role = QComboBox()
        self.input_role.addItems(["admin", "réception", "bar"])
        # Sélectionner le rôle courant
        role_index = self.input_role.findText(user_data.get("role", ""), Qt.MatchFixedString)
        if role_index >= 0:
            self.input_role.setCurrentIndex(role_index)

        self.input_actif = QCheckBox()
        self.input_actif.setChecked(user_data.get("actif", False))

        form.addRow("Nom complet :", self.input_nom_complet)
        form.addRow("Rôle :", self.input_role)
        form.addRow("Actif :", self.input_actif)

        self.layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def get_data(self):
        return {
            "nom_complet": self.input_nom_complet.text(),
            "role": self.input_role.currentText(),
            "actif": self.input_actif.isChecked()
        }


class UsersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QLabel { color: #2c3e70; }")
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        title = QLabel("Gestion des utilisateurs")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.layout.addWidget(title)

        btn_add = QPushButton("Ajouter un utilisateur")
        btn_add.clicked.connect(self.show_add_user_form)
        self.layout.addWidget(btn_add)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Nom complet", "Nom d’utilisateur", "Rôle", "Actif", "Modifier", "Supprimer"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        self.load_users()

    def load_users(self):
        self.table.setRowCount(0)
        result = UserController.get_all_users()
        if not result["success"]:
            QMessageBox.warning(self, "Erreur", result.get("error", "Erreur inconnue"))
            return
        users = result["data"]

        for row_idx, user in enumerate(users):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(user.get("nom_complet", "")))
            self.table.setItem(row_idx, 1, QTableWidgetItem(user.get("username", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(user.get("role", "")))

            cb = QCheckBox()
            cb.setChecked(user.get("actif", False))
            cb.stateChanged.connect(lambda state, uid=user.get("id"): self.toggle_active(uid, state))
            self.table.setCellWidget(row_idx, 3, cb)

            btn_edit = QPushButton("Modifier")
            btn_edit.clicked.connect(lambda checked, u=user: self.edit_user(u))
            self.table.setCellWidget(row_idx, 4, btn_edit)

            btn_delete = QPushButton("Supprimer")
            btn_delete.clicked.connect(lambda checked, u=user: self.delete_user(u))
            self.table.setCellWidget(row_idx, 5, btn_delete)

    def toggle_active(self, user_id, state):
        actif = state == Qt.Checked
        res = UserController.set_active_status(user_id, actif)
        if not res["success"]:
            QMessageBox.warning(self, "Erreur", "Impossible de changer le statut de l'utilisateur.")

    def edit_user(self, user):
        dialog = EditUserDialog(user, self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            # Ici tu dois implémenter une méthode update_user dans UserController pour appliquer les changements
            res = UserController.update_user(user["id"], data["nom_complet"], data["role"], data["actif"])
            if res["success"]:
                QMessageBox.information(self, "Succès", "Utilisateur mis à jour.")
                self.load_users()
            else:
                QMessageBox.warning(self, "Erreur", res.get("error", "Erreur inconnue."))

    def delete_user(self, user):
        confirm = QMessageBox.question(self, "Confirmer suppression", f"Voulez-vous supprimer l'utilisateur {user['username']} ?")
        if confirm == QMessageBox.Yes:
            res = UserController.delete_user(user["id"])
            if res["success"]:
                QMessageBox.information(self, "Succès", "Utilisateur supprimé.")
                self.load_users()
            else:
                QMessageBox.warning(self, "Erreur", res.get("error", "Erreur inconnue."))


    def show_add_user_form(self):
        form_widget = QWidget()
        form_layout = QVBoxLayout()
        form_widget.setLayout(form_layout)

        nom_complet = QLineEdit()
        username = QLineEdit()
        password = QLineEdit()
        password.setEchoMode(QLineEdit.Password)
        role = QComboBox()
        role.addItems(["admin", "réception", "bar"])

        form_layout.addWidget(QLabel("Nom complet :"))
        form_layout.addWidget(nom_complet)

        form_layout.addWidget(QLabel("Nom d’utilisateur :"))
        form_layout.addWidget(username)

        form_layout.addWidget(QLabel("Mot de passe :"))
        form_layout.addWidget(password)

        form_layout.addWidget(QLabel("Rôle :"))
        form_layout.addWidget(role)

        btn_create = QPushButton("Créer")
        btn_create.clicked.connect(lambda: self.create_user(
            nom_complet.text(), username.text(), password.text(), role.currentText(), form_widget
        ))

        btn_cancel = QPushButton("Annuler")
        btn_cancel.clicked.connect(lambda: self.layout.removeWidget(form_widget) or form_widget.deleteLater())

        hbtn = QHBoxLayout()
        hbtn.addWidget(btn_create)
        hbtn.addWidget(btn_cancel)

        form_layout.addLayout(hbtn)
        self.layout.addWidget(form_widget)

    def create_user(self, nom_complet, username, password, role, widget_to_remove):
        try:
            UserController.create_user(username, password, role, nom_complet)
            QMessageBox.information(self, "Succès", "Utilisateur créé avec succès.")
            self.layout.removeWidget(widget_to_remove)
            widget_to_remove.deleteLater()
            self.load_users()
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
