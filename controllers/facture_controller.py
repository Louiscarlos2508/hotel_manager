# /home/soutonnoma/PycharmProjects/HotelManager/controllers/facture_controller.py

from datetime import date, datetime
from models.facture_item_model import FactureItemModel
from models.facture_model import FactureModel
from models.reservation_model import ReservationModel
from models.chambre_model import ChambreModel
from controllers.hotel_info_controller import HotelInfoController
from controllers.commande_controller import CommandeController
from controllers.commande_item_controller import CommandeItemController
# --- AJOUT : Importer le contrôleur des services demandés ---
from controllers.service_demande_controller import ServiceDemandeController


class FactureController:

    # ... (les méthodes creer_facture, get_facture_par_reservation, etc. restent inchangées) ...
    @staticmethod
    def creer_facture(reservation_id, statut="Brouillon"):
        if not reservation_id or not isinstance(reservation_id, int) or reservation_id <= 0:
            return {"success": False, "error": "ID réservation invalide."}
        try:
            facture_id = FactureModel.create(reservation_id, statut)
            return {"success": True, "facture_id": facture_id}
        except Exception as e:
            return {"success": False, "error": f"Erreur création facture : {e}"}

    @staticmethod
    def get_facture_par_reservation(reservation_id):
        if not reservation_id or not isinstance(reservation_id, int) or reservation_id <= 0:
            return {"success": False, "error": "ID réservation invalide."}
        try:
            facture = FactureModel.get_by_reservation(reservation_id)
            return {"success": True, "data": facture}
        except Exception as e:
            return {"success": False, "error": f"Erreur récupération facture : {e}"}

    @staticmethod
    def mettre_a_jour_montants(facture_id, montant_total_ht, montant_total_tva, montant_total_ttc, montant_paye):
        if not facture_id or not isinstance(facture_id, int) or facture_id <= 0:
            return {"success": False, "error": "ID facture invalide."}
        try:
            updated = FactureModel.update_montants(facture_id, montant_total_ht, montant_total_tva, montant_total_ttc,
                                                   montant_paye)
            if not updated:
                return {"success": False, "error": "Mise à jour des montants échouée."}
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour montants : {e}"}

    @staticmethod
    def mettre_a_jour_statut(facture_id, nouveau_statut):
        if not facture_id or not isinstance(facture_id, int) or facture_id <= 0:
            return {"success": False, "error": "ID facture invalide."}
        try:
            updated = FactureModel.update_statut(facture_id, nouveau_statut)
            if not updated:
                return {"success": False, "error": "Mise à jour du statut échouée."}
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"Erreur mise à jour statut : {e}"}


    @staticmethod
    def generer_et_mettre_a_jour_facture(reservation_id):
        """
        LA MÉTHODE CENTRALE DE CALCUL.
        Elle calcule tout (Hébergement, Consommations ET SERVICES), nettoie les anciennes lignes,
        recrée les nouvelles, met à jour les totaux de la facture ET RETOURNE LES DÉTAILS.
        """
        try:
            # 1. Récupérer toutes les informations de base
            resa = ReservationModel.get_by_id(reservation_id)
            if not resa:
                return {"success": False, "error": "Réservation introuvable."}

            hotel_info_resp = HotelInfoController.get_info()
            hotel_info = hotel_info_resp.get("data", {})
            tva_hebergement_rate = hotel_info.get('tva_hebergement', 0.10)
            tva_restauration_rate = hotel_info.get('tva_restauration', 0.18)
            # Pour l'instant, on applique la TVA de l'hébergement aux services.
            # On pourrait ajouter un champ tva_services dans hotel_info pour plus de précision.
            tva_services_rate = tva_hebergement_rate
            tdt_par_personne = hotel_info.get('tdt_par_personne', 0)

            chambre = ChambreModel.get_by_id(resa['chambre_id'])
            if not chambre:
                return {"success": False, "error": "Chambre de la réservation introuvable."}

            # 2. Calculer les coûts HT
            date_arrivee = datetime.fromisoformat(resa["date_arrivee"]).date()
            date_depart_effective = date.today() if resa["statut"] == "check-in" else datetime.fromisoformat(
                resa["date_depart"]).date()
            nb_nuits = max(1, (date_depart_effective - date_arrivee).days)
            nb_adultes = resa.get("nb_adultes", 1)
            montant_nuitee_ht = nb_nuits * chambre["prix_par_nuit"]

            montant_consommation_ht = 0
            commandes_resp = CommandeController.liste_commandes_par_reservation(reservation_id)
            if commandes_resp.get("success"):
                for commande in commandes_resp["data"]:
                    if commande["statut"] == "Annulé": continue
                    items_resp = CommandeItemController.liste_items(commande["id"])
                    if items_resp.get("success"):
                        for item in items_resp["data"]:
                            montant_consommation_ht += item["quantite"] * item["prix_unitaire_capture"]

            # --- AJOUT : Calcul du coût des services ---
            montant_services_ht = 0
            services_demandes_resp = ServiceDemandeController.lister_par_reservation(reservation_id)
            services_demandes = []
            if services_demandes_resp.get("success"):
                services_demandes = services_demandes_resp.get("data", [])
                for service in services_demandes:
                    montant_services_ht += service["quantite"] * service["prix_capture"]
            # --- FIN DE L'AJOUT ---

            # 3. Calculer les taxes et les totaux
            tva_hebergement = montant_nuitee_ht * tva_hebergement_rate
            tva_restauration = montant_consommation_ht * tva_restauration_rate
            tva_services = montant_services_ht * tva_services_rate # Taxe sur les services
            montant_tdt = nb_adultes * nb_nuits * tdt_par_personne

            total_ht = montant_nuitee_ht + montant_consommation_ht + montant_services_ht # Ajout des services
            total_tva = tva_hebergement + tva_restauration + tva_services # Ajout de la TVA des services
            total_ttc = total_ht + total_tva + montant_tdt

            # 4. Créer ou récupérer la facture
            facture_resp = FactureController.get_facture_par_reservation(reservation_id)
            if not facture_resp.get("success"): return facture_resp

            facture_data = facture_resp.get("data")
            if not facture_data:
                facture_creation_resp = FactureController.creer_facture(reservation_id)
                if not facture_creation_resp.get("success"): return facture_creation_resp
                facture_id = facture_creation_resp["facture_id"]
                montant_paye_existant = 0
            else:
                facture_id = facture_data["id"]
                montant_paye_existant = facture_data.get("montant_paye", 0)

            # 5. Nettoyer la facture de ses anciennes lignes pour éviter les doublons
            FactureItemModel.delete_by_facture(facture_id)

            # 6. Créer les NOUVELLES lignes de facture détaillées
            FactureItemModel.create(facture_id, "Hébergement", nb_nuits, chambre["prix_par_nuit"], montant_nuitee_ht,
                                    tva_hebergement, montant_nuitee_ht + tva_hebergement)
            if montant_consommation_ht > 0:
                FactureItemModel.create(facture_id, "Consommations (Bar/Restaurant)", 1, montant_consommation_ht,
                                        montant_consommation_ht, tva_restauration,
                                        montant_consommation_ht + tva_restauration)
            if montant_tdt > 0:
                FactureItemModel.create(facture_id, "Taxe de Développement Touristique", 1, montant_tdt, montant_tdt, 0,
                                        montant_tdt)

            # --- AJOUT : Créer les lignes de facture pour chaque service ---
            for service in services_demandes:
                service_ht = service["quantite"] * service["prix_capture"]
                service_tva = service_ht * tva_services_rate
                service_ttc = service_ht + service_tva
                FactureItemModel.create(
                    facture_id,
                    f"Service: {service['nom_service']}",
                    service['quantite'],
                    service['prix_capture'], # prix_unitaire_ht
                    service_ht,              # montant_ht
                    service_tva,             # montant_tva
                    service_ttc,             # montant_ttc
                    service_demande_id=service['id']
                )
            # --- FIN DE L'AJOUT ---

            # 7. Mettre à jour les totaux de la facture principale, en conservant le montant déjà payé
            FactureController.mettre_a_jour_montants(facture_id, total_ht, total_tva, total_ttc, montant_paye_existant)

            # --- MODIFICATION : On retourne les détails calculés, y compris les services ---
            details = {
                "montant_nuitee_ht": montant_nuitee_ht, "tva_hebergement": tva_hebergement,
                "tva_hebergement_rate": tva_hebergement_rate,
                "montant_consommation_ht": montant_consommation_ht,
                "tva_restauration": tva_restauration, "tva_restauration_rate": tva_restauration_rate,
                "montant_services_ht": montant_services_ht, # Ajout
                "tva_services": tva_services,             # Ajout
                "montant_tdt": montant_tdt,
                "total_ht": total_ht, "total_tva": total_tva, "total_ttc": total_ttc,
            }
            return {"success": True, "data": details, "message": "Facture mise à jour avec les derniers calculs."}

        except Exception as e:
            # On peut ajouter un print pour un débogage plus facile en cas de problème
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"Erreur lors de la génération de la facture : {e}"}
