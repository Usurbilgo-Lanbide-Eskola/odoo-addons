PDF Signatures
==============

This module extends the functionality of Odoo's `ir.attachment` model to handle PDF signatures. It provides the following features:

Features
--------

- Automatically extracts and stores signature information from PDF files when they are uploaded or updated.
- Displays signature details in the attachment form and tree views.
- Ensures that signature records are deleted when the corresponding attachment is removed.
- Provides security access control for managing signature records.

Installation
------------

1. Install the required Python dependencies:
   ```
   pip install asn1crypto pypdf
   ```

2. Add the module to your Odoo addons path.

3. Update the module list and install the `pdf_signatures` module.

Usage
-----

1. Upload a PDF file as an attachment in Odoo.
2. The system will automatically extract and display the signature details in the attachment form view.
3. Signature details can also be viewed in the tree view of attachments.

Security
--------

- Regular users (`base.group_user`) can view and manage their own signature records.
- System administrators (`base.group_system`) have full access to all signature records.

License
-------

This module is licensed under the AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
