from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QComboBox, QDateEdit, QPushButton, QMessageBox,
    QLineEdit, QFormLayout, QGroupBox, QCheckBox, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem
)
from PySide6.QtCore import QDate
from PySide6.QtGui import QFont
from database.db import get_connection
from controllers.reservation_controller import ReservationController
from controllers.client_controller import ClientController
from models.chambre_model import ChambreModel


class ReservationsPage(QWidget):
    def __init__(self, user_id=None):
        super().__init__()

        self.conn = get_connection()
        self.chambre_model = ChambreModel()
        self.reservation_controller = ReservationController(self.conn, user_id)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        title = QLabel("Réservations")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.layout.addWidget(title)

        client_group = QGroupBox("Client")
        client_layout = QFormLayout()

        self.checkbox_new_client = QCheckBox("Nouveau client")
        self.checkbox_new_client.setChecked(True)
        self.checkbox_new_client.stateChanged.connect(self.toggle_client_mode)
        self.layout.addWidget(self.checkbox_new_client)

        self.combo_clients = QComboBox()
        self.load_clients()
        client_layout.addRow("Client existant :", self.combo_clients)

        self.input_nom = QLineEdit()
        self.input_prenom = QLineEdit()
        self.input_tel = QLineEdit()
        self.input_email = QLineEdit()
        self.input_cni = QLineEdit()
        self.input_adresse = QLineEdit()

        client_layout.addRow("Nom * :", self.input_nom)
        client_layout.addRow("Prénom :", self.input_prenom)
        client_layout.addRow("Téléphone :", self.input_tel)
        client_layout.addRow("Email :", self.input_email)
        client_layout.addRow("CNI :", self.input_cni)
        client_layout.addRow("Adresse :", self.input_adresse)

        client_group.setLayout(client_layout)
        self.layout.addWidget(client_group)

        self.toggle_client_mode()

        form_layout = QHBoxLayout()

        form_layout.addWidget(QLabel("Chambre :"))
        self.combo_chambres = QComboBox()
        self.load_chambres()
        self.combo_chambres.currentIndexChanged.connect(self.update_prix)
        form_layout.addWidget(self.combo_chambres)

        form_layout.addWidget(QLabel("Date arrivée :"))
        self.date_arrivee = QDateEdit(QDate.currentDate())
        self.date_arrivee.setCalendarPopup(True)
        self.date_arrivee.dateChanged.connect(self.update_prix)
        form_layout.addWidget(self.date_arrivee)

        form_layout.addWidget(QLabel("Date départ :"))
        self.date_depart = QDateEdit(QDate.currentDate().addDays(1))
        self.date_depart.setCalendarPopup(True)
        self.date_depart.dateChanged.connect(self.update_prix)
        form_layout.addWidget(self.date_depart)

        self.layout.addLayout(form_layout)

        prix_layout = QHBoxLayout()
        self.label_prix_nuit = QLabel("Prix par nuit : 0 FCFA")
        self.label_nb_nuits = QLabel("Nombre de nuits : 0")
        self.label_prix_total = QLabel("Prix total : 0 FCFA")
        prix_layout.addWidget(self.label_prix_nuit)
        prix_layout.addWidget(self.label_nb_nuits)
        prix_layout.addWidget(self.label_prix_total)
        self.layout.addLayout(prix_layout)

        self.btn_reserver = QPushButton("Réserver")
        self.btn_reserver.clicked.connect(self.action_reserver)
        self.layout.addWidget(self.btn_reserver)

        btn_refresh = QPushButton("Actualiser")
        btn_refresh.clicked.connect(self.refresh_table)
        self.layout.addWidget(btn_refresh)

        self.layout.addStretch()

        self.update_prix()

        title = QLabel("Liste des Réservations")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Client", "Chambre", "Arrivée", "Départ", "Statut", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.layout.addWidget(self.table)

        self.refresh_table()

    def toggle_client_mode(self):
        nouveau = self.checkbox_new_client.isChecked()
        self.combo_clients.setEnabled(not nouveau)
        for widget in [self.input_nom, self.input_prenom, self.input_tel, self.input_email, self.input_cni, self.input_adresse]:
            widget.setEnabled(nouveau)

    def load_clients(self):
        self.combo_clients.clear()
        try:
            res = ClientController.liste_clients()
            if not res.get("success", False):
                raise Exception(res.get("error", "Erreur chargement clients"))
            for c in res.get("clients", []):
                self.combo_clients.addItem(f"{c.get('nom', '')} {c.get('prenom', '')}".strip(), c.get('id'))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur chargement clients : {e}")

    def load_chambres(self):
        self.combo_chambres.clear()
        try:
            for chambre in self.chambre_model.get_all():
                if chambre['statut'] == 'libre':
                    self.combo_chambres.addItem(f"{chambre['numero']} - {chambre['prix_par_nuit']} XOF/nuit", chambre['id'])
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur chargement chambres : {e}")

    def update_prix(self):
        chambre_id = self.combo_chambres.currentData()
        if chambre_id is None:
            self.label_prix_nuit.setText("Prix par nuit : 0 FCFA")
            self.label_nb_nuits.setText("Nombre de nuits : FCFA")
            self.label_prix_total.setText("Prix total : 0 FCFA")
            return
        try:
            chambre = self.chambre_model.get_by_id(chambre_id)
            prix_nuit = chambre['prix_par_nuit']
            nb_nuits = max(0, self.date_arrivee.date().daysTo(self.date_depart.date()))
            prix_total = nb_nuits * prix_nuit
            self.label_prix_nuit.setText(f"Prix par nuit : {prix_nuit} FCFA")
            self.label_nb_nuits.setText(f"Nombre de nuits : {nb_nuits}")
            self.label_prix_total.setText(f"Prix total : {prix_total} FCFA")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur calcul prix : {e}")

    def action_reserver(self):
        chambre_id = self.combo_chambres.currentData()
        if chambre_id is None:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une chambre.")
            return

        date_arrivee = self.date_arrivee.date().toString("yyyy-MM-dd")
        date_depart = self.date_depart.date().toString("yyyy-MM-dd")

        if self.date_arrivee.date() >= self.date_depart.date():
            QMessageBox.warning(self, "Erreur", "La date de départ doit être après la date d'arrivée.")
            return

        try:
            if self.reservation_controller.check_conflit(chambre_id, date_arrivee, date_depart):
                QMessageBox.warning(self, "Conflit", "La chambre est déjà réservée sur cette période.")
                return
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur vérification disponibilité : {e}")
            return

        if self.checkbox_new_client.isChecked():
            nom = self.input_nom.text().strip()
            if not nom:
                QMessageBox.warning(self, "Erreur", "Le nom du client est obligatoire.")
                return
            result_client = ClientController.ajouter_client(
                nom, self.input_prenom.text().strip(), self.input_tel.text().strip(),
                self.input_email.text().strip(), self.input_cni.text().strip(), self.input_adresse.text().strip())
            if not result_client.get("success", False):
                QMessageBox.warning(self, "Erreur",
                                    f"Erreur création client : {result_client.get('error', 'Erreur inconnue')}")
                return
            client_id = result_client.get("id")
        else:
            client_id = self.combo_clients.currentData()
            if client_id is None:
                QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un client.")
                return

        try:
            result = self.reservation_controller.create_reservation(
                client_id, chambre_id, date_arrivee, date_depart
            )
            if not result.get("success", False):
                QMessageBox.warning(self, "Erreur",
                                    f"Erreur création réservation : {result.get('error', 'Erreur inconnue')}")
                return
            reservation_id = result.get("reservation_id")
            QMessageBox.information(self, "Succès", f"Réservation créée avec l'ID {reservation_id}")

            self.load_chambres()
            self.load_clients()
            self.update_prix()
            for widget in [self.input_nom, self.input_prenom, self.input_tel, self.input_email, self.input_cni,
                           self.input_adresse]:
                widget.clear()
            self.date_arrivee.setDate(QDate.currentDate())
            self.date_depart.setDate(QDate.currentDate().addDays(1))
            self.refresh_table()

        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur lors de la création de réservation : {e}")

    def make_annuler_handler(self, res_id):
        return lambda checked: self.annuler_reservation(res_id)

    def refresh_table(self):
        try:
            response = self.reservation_controller.list_reservations()
            if not response.get("success", False):
                QMessageBox.warning(self, "Erreur", response.get("error", "Erreur inconnue"))
                return

            reservations = response.get("data", [])
            self.table.clearContents()
            self.table.setRowCount(len(reservations))

            # Charger tous les clients une fois
            clients = {c['id']: c for c in ClientController.liste_clients().get("clients", [])}

            # Charger toutes les chambres une fois
            chambres = {ch['id']: ch for ch in self.chambre_model.get_all()}

            for i, r in enumerate(reservations):
                client = clients.get(r["client_id"], {})
                chambre = chambres.get(r["chambre_id"], {})

                self.table.setItem(i, 0, QTableWidgetItem(str(r["id"])))
                self.table.setItem(i, 1, QTableWidgetItem(f"{client.get('nom', '')} {client.get('prenom', '')}"))
                self.table.setItem(i, 2, QTableWidgetItem(chambre.get("numero", "?")))
                self.table.setItem(i, 3, QTableWidgetItem(r["date_arrivee"]))
                self.table.setItem(i, 4, QTableWidgetItem(r["date_depart"]))

                statut = r.get("statut", "inconnu")
                self.table.setItem(i, 5, QTableWidgetItem(statut.capitalize()))

                # Créer un widget d'action
                h_layout = QHBoxLayout()
                h_layout.setContentsMargins(0, 0, 0, 0)
                cell_widget = QWidget()
                cell_widget.setLayout(h_layout)

                if statut == "réservée":
                    btn_annuler = QPushButton("Annuler")
                    btn_annuler.clicked.connect(self.make_annuler_handler(r["id"]))
                    h_layout.addWidget(btn_annuler)

                    btn_modifier = QPushButton("Modifier")
                    btn_modifier.clicked.connect(lambda _, rid=r["id"]: self.modifier_reservation(rid))
                    h_layout.addWidget(btn_modifier)
                else:
                    btn_modifier = QPushButton("Modifier")
                    btn_modifier.clicked.connect(lambda _, rid=r["id"]: self.modifier_reservation(rid))
                    h_layout.addWidget(btn_modifier)


                self.table.setCellWidget(i, 6, cell_widget)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur chargement des réservations : {e}")

    def modifier_reservation(self, reservation_id):
        try:
            res = self.reservation_controller.get_reservation(reservation_id)
            if not res.get("success", False):
                QMessageBox.warning(self, "Erreur", res.get("error", "Réservation introuvable"))
                return

            data = res["data"]
            chambres_libres = [
                ch for ch in self.chambre_model.get_all()
                if ch["statut"] == "libre" or ch["id"] == data["chambre_id"]
            ]

            if not chambres_libres:
                QMessageBox.information(self, "Info", "Aucune autre chambre disponible.")
                return

            # Boîte de dialogue personnalisée
            dialog = QWidget()
            dialog.setWindowTitle(f"Modifier la chambre - Réservation {reservation_id}")
            layout = QVBoxLayout(dialog)

            label = QLabel("Sélectionnez une nouvelle chambre :")
            layout.addWidget(label)

            combo = QComboBox()
            id_to_index = {}
            for i, ch in enumerate(chambres_libres):
                combo.addItem(f"{ch['numero']} - {ch['prix_par_nuit']} FCFA/nuit", ch["id"])
                id_to_index[ch["id"]] = i

            combo.setCurrentIndex(id_to_index.get(data["chambre_id"], 0))
            layout.addWidget(combo)

            btn_ok = QPushButton("Valider le changement")
            layout.addWidget(btn_ok)

            def valider():
                new_chambre_id = combo.currentData()
                if new_chambre_id == data["chambre_id"]:
                    QMessageBox.information(dialog, "Info", "La chambre sélectionnée est la même.")
                    dialog.close()
                    return

                update = self.reservation_controller.update_reservation(reservation_id, chambre_id=new_chambre_id)
                if update.get("success", False):
                    QMessageBox.information(dialog, "Succès", update["message"])
                    self.refresh_table()
                    self.load_chambres()
                else:
                    QMessageBox.warning(dialog, "Erreur", update.get("error", "Erreur inconnue"))
                dialog.close()

            btn_ok.clicked.connect(valider)
            dialog.setLayout(layout)
            dialog.setFixedSize(400, 120)
            dialog.show()

        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def annuler_reservation(self, reservation_id):
        try:
            # Récupérer la réservation depuis le backend
            res = self.reservation_controller.get_reservation(reservation_id)
            if not res.get("success", False):
                raise Exception(res.get("error", "Réservation introuvable"))

            statut = res.get("data", {}).get("statut", "")
            if statut != "réservée":
                QMessageBox.warning(self, "Annulation impossible",
                                    f"Seules les réservations avec le statut 'réservée' peuvent être annulées (statut actuel : '{statut}').")
                return

            confirm = QMessageBox.question(
                self, "Confirmation",
                "Annuler cette réservation ?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                self.reservation_controller.cancel_reservation(reservation_id)
                QMessageBox.information(self, "Succès", "Réservation annulée.")
                self.refresh_table()
                self.load_chambres()

        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

