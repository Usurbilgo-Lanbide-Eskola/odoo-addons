# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Company internships",
    "version": "14.0.1.1.5",
    "category": "Customer Relationship Management",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "sale_crm", "sale_order_line_menu", "school_year",
        "partner_second_lastname", "product", "partner_contact_gender",
        "partner_contact_birthdate", "partner_phone_secondary"
    ],
    "excludes": [],
    "data": [
        "security/ir.model.access.csv",
        "views/internship_type_view.xml",
        "views/product_template_view.xml",
        "views/res_partner_view.xml",
        "views/sale_order_line_view.xml",
        "views/crm_lead_view.xml",
        "views/school_year_historical_view.xml",
    ],
    "installable": True,
}
