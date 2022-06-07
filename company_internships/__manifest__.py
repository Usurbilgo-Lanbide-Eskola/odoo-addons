# Copyright 2021 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Company internships",
    "version": "14.0.1.0.2",
    "category": "Customer Relationship Management",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [
        "crm", "sale_order_line_menu", "school_year",
    ],
    "excludes": [],
    "data": [
        "views/product_template_view.xml",
        "views/res_partner_category_view.xml",
        "views/res_partner_view.xml",
        "views/sale_order_line_view.xml",
    ],
    "installable": True,
}
