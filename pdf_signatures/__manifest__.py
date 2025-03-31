{
    "name": "PDF Signatures",
    "version": "14.0.1.0.1",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "CIFP USURBIL LHII",
    "website": "http://www.lhusurbil.eus",
    "depends": [],
    "external_dependencies": {"python": ["asn1crypto", "pypdf"]},
    "excludes": [],
    "data": [
        "views/ir_attachment_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "post_init_hook": "_generate_signatures_for_existing_pdfs",
}