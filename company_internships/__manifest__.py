# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Company internships",
    "version": "14.0.1.1.15",
    "category": "Customer Relationship Management",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "contributors": [
        "Aitor Mindeguia (CIFP USURBIL LHII)",
        "Gloria Moya (ZUBIGUNE FUNDAZIOA)",
        "Malen Aierbe (CIFP USURBIL LHII)",
        "Mikel Arregi (CIFP USURBIL LHII)"
    ],    
    "depends": [
        "sale_crm", "sale_order_line_menu", "school_year",
        "partner_second_lastname", "product", "partner_contact_gender",
        "partner_contact_birthdate", "partner_phone_secondary"
    ],
    "external_dependencies": {"python": ["openpyxl"]},
    "excludes": [],
    "data": [
        "security/internship_security.xml",
        "security/ir.model.access.csv",
        "wizard/crm_internship_partial_move_view.xml",
        "views/internship_type_view.xml",
        "views/internship_line_view.xml",
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
        "views/sale_order_line_view.xml",
        "views/crm_lead_view.xml",
        "views/school_year_historical_view.xml",
        "views/internship_menu.xml",
        "views/internship_documentation_view.xml",
        "views/res_config_settings_view.xml",
        "wizard/create_internship_document_view.xml",
        "wizard/upload_new_file_view.xml",
        "wizard/promote_student_view.xml",
        "data/document_type_code_sequence.xml"
    ],
    "installable": True,
}
