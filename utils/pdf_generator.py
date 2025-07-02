# /home/soutonnoma/PycharmProjects/HotelManager/utils/pdf_generator.py

import os
from datetime import date
from PySide6.QtWidgets import QMessageBox
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT

# --- Contrôleurs pour récupérer les données ---
from controllers.facture_controller import FactureController
from controllers.facture_item_controller import FactureItemController
from controllers.hotel_info_controller import HotelInfoController
from controllers.paiement_controller import PaiementController
from controllers.reservation_controller import ReservationController
from controllers.client_controller import ClientController


def creer_facture_pdf(reservation_id: int):
    """
    Génère une facture PDF professionnelle et détaillée pour une réservation donnée.
    """
    try:
        # --- 1. Collecte de toutes les données nécessaires ---
        resa_resp = ReservationController.get_by_id(reservation_id)
        if not resa_resp.get("success"): raise ValueError("Réservation introuvable.")
        reservation = resa_resp["data"]

        client_resp = ClientController.obtenir_client(reservation["client_id"])
        if not client_resp.get("success"): raise ValueError("Client introuvable.")
        client = client_resp["data"]

        facture_resp = FactureController.get_facture_par_reservation(reservation_id)
        if not facture_resp.get("success") or not facture_resp.get("data"):
            raise ValueError("Facture introuvable pour cette réservation.")
        facture = facture_resp["data"]

        items_resp = FactureItemController.liste_items_par_facture(facture["id"])
        if not items_resp.get("success"): raise ValueError("Impossible de charger les lignes de la facture.")
        facture_items = items_resp["data"]

        paiements_resp = PaiementController.get_paiements_par_facture(facture["id"])
        if not paiements_resp.get("success"): raise ValueError("Impossible de charger les paiements.")
        paiements = paiements_resp["data"]

        hotel_resp = HotelInfoController.get_info()
        hotel = hotel_resp.get("data", {})

        # --- 2. Configuration du document PDF ---
        bureau = os.path.join(os.path.expanduser("~"), "Desktop")
        dossier_factures = os.path.join(bureau, "FacturesHotel")
        os.makedirs(dossier_factures, exist_ok=True)
        chemin_pdf = os.path.join(dossier_factures, f"Facture_{facture['id']}_Client_{client['nom']}.pdf")

        doc = SimpleDocTemplate(chemin_pdf, pagesize=A4, topMargin=20 * mm, bottomMargin=20 * mm)
        story = []
        styles = getSampleStyleSheet()

        # --- 3. Construction des éléments de la facture ---

        # En-tête avec logo et infos de l'hôtel
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
        logo = Image(logo_path, width=40 * mm, height=40 * mm) if os.path.exists(logo_path) else Paragraph("Logo Hôtel",
                                                                                                           styles['h2'])

        hotel_info_text = f"""
            <b>{hotel.get('nom', 'Nom de votre Hôtel')}</b><br/>
            {hotel.get('adresse', 'Adresse de votre hôtel')}<br/>
            Tél : {hotel.get('telephone', 'Votre téléphone')} | Email : {hotel.get('email', 'Votre email')}<br/>
            SIRET : {hotel.get('siret', 'Votre SIRET')}
        """
        hotel_info_para = Paragraph(hotel_info_text, styles['Normal'])

        header_table = Table([[logo, hotel_info_para]], colWidths=[50 * mm, None])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 15 * mm))

        # Titre de la facture et infos client
        titre_facture = Paragraph(f"FACTURE N° {facture['id']}", styles['h1'])
        story.append(titre_facture)
        story.append(Spacer(1, 2 * mm))

        client_info_text = f"""
            <b>Facturé à :</b><br/>
            {client.get('nom', '')} {client.get('prenom', '')}<br/>
            {client.get('adresse', 'Adresse non spécifiée')}<br/>
            Tél : {client.get('tel', '')}
        """
        client_info_para = Paragraph(client_info_text, styles['Normal'])

        facture_details_text = f"""
            <b>Date de facturation :</b> {date.today().strftime('%d/%m/%Y')}<br/>
            <b>Réservation N° :</b> {reservation_id}<br/>
            <b>Période du séjour :</b> {reservation['date_arrivee']} au {reservation['date_depart']}
        """
        facture_details_para = Paragraph(facture_details_text, styles['Normal'])

        info_table = Table([[client_info_para, facture_details_para]], colWidths=['50%', '50%'])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 10 * mm))

        # Tableau des lignes de la facture
        table_data = [
            ["Description", "Qté", "P.U. (HT)", "Montant (TTC)"]
        ]
        for item in facture_items:
            table_data.append([
                item['description'],
                item['quantite'],
                f"{item['prix_unitaire_ht']:,.0f} FCFA",
                f"{item['montant_ttc']:,.0f} FCFA"
            ])

        invoice_table = Table(table_data, colWidths=[None, 25 * mm, 35 * mm, 40 * mm])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4a69bd")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(invoice_table)
        story.append(Spacer(1, 5 * mm))

        # Section des totaux
        total_ht = facture.get('montant_total_ht', 0)
        total_tva = facture.get('montant_total_tva', 0)
        total_ttc = facture.get('montant_total_ttc', 0)
        total_paye = facture.get('montant_paye', 0)
        reste_a_payer = total_ttc - total_paye

        totals_data = [
            ['Sous-total (HT):', f"{total_ht:,.0f} FCFA"],
            ['Total TVA:', f"{total_tva:,.0f} FCFA"],
            ['Total TTC:', f"{total_ttc:,.0f} FCFA"],
            ['Montant Payé:', f"{total_paye:,.0f} FCFA"],
            [Paragraph("<b>Reste à Payer:</b>", styles['Normal']),
             Paragraph(f"<b>{reste_a_payer:,.0f} FCFA</b>", styles['Normal'])]
        ]

        totals_table = Table(totals_data, colWidths=[None, 40 * mm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),  # Grille invisible
            ('FONTNAME', (0, 4), (1, 4), 'Helvetica-Bold'),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 10 * mm))

        # Pied de page
        methodes_paiement = " / ".join(sorted(list({p['methode'] for p in paiements}))) if paiements else "N/A"
        footer_text = f"Payé par : {methodes_paiement}<br/><br/>Merci de votre confiance et à bientôt !"
        footer_para = Paragraph(footer_text, ParagraphStyle(name='Footer', alignment=TA_CENTER, fontSize=10))
        story.append(footer_para)

        # --- 4. Génération du document ---
        doc.build(story)

        return {"success": True, "path": chemin_pdf}

    except Exception as e:
        return {"success": False, "error": f"Erreur lors de la génération du PDF : {e}"}
