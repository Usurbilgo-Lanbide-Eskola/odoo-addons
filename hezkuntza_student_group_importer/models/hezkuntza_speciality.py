# Copyright 2022 Mikel Arregi Etxaniz - CIFP Usurbil LHII
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from random import randint


class HezkuntzaSpeciality(models.Model):
    _name = 'hezkuntza.speciality'
    _order = 'name'
    _parent_store = True

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Speciality Name', required=True, translate=True)
    description = fields.Char(string="Description")
    color = fields.Integer(string='Color Index', default=_get_default_color)
    parent_id = fields.Many2one('hezkuntza.speciality',
                                string='Parent Category', index=True,
                                ondelete='cascade')
    child_ids = fields.One2many('hezkuntza.speciality', 'parent_id',
                                string='Child Specialities')
    active = fields.Boolean(default=True,
                            help="The active field allows you to hide "
                                 "the category without removing it.")
    parent_path = fields.Char(index=True)
    partner_ids = fields.Many2many('hezkuntza.degree', column1='category_id',
                                   column2='partner_id', string='Partners')

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive tags.'))

    def name_get(self):
        """ Return the categories' display name, including their direct
            parent by default.

            If ``context['partner_category_display']`` is ``'short'``, the short
            version of the category name (without the direct parent) is used.
            The default is the long version.
        """
        if self._context.get('specialty_category_display') == 'short':
            return super(HezkuntzaSpeciality, self).name_get()

        res = []
        for category in self:
            names = []
            current = category
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((category.id, ' / '.join(reversed(names))))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100,
                     name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

