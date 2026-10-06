from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMaterialModel(TransactionCase):

    def setUp(self):
        super(TestMaterialModel, self).setUp()

        self.supplier = self.env['res.partner'].create({
            'name': 'Test Supplier',
        })

    def test_create_material_valid(self):
        material = self.env['material.registration'].create({
            'material_code': 'TEST-001',
            'material_name': 'Test Cotton',
            'material_type': 'cotton',
            'material_buy_price': 100,
            'supplier_id': self.supplier.id,
        })

        self.assertTrue(material)
        self.assertEqual(material.material_code, 'TEST-001')
        self.assertEqual(material.material_name, 'Test Cotton')
        self.assertEqual(material.material_type, 'cotton')
        self.assertEqual(material.material_buy_price, 100)
        self.assertEqual(material.supplier_id.id, self.supplier.id)

    def test_material_buy_price_below_100(self):
        with self.assertRaises(ValidationError):
            self.env['material.registration'].create({
                'material_code': 'TEST-002',
                'material_name': 'Invalid Price Material',
                'material_type': 'cotton',
                'material_buy_price': 99,
                'supplier_id': self.supplier.id,
            })

    def test_material_type_invalid(self):
        with self.assertRaises(ValueError):
            self.env['material.registration'].create({
                'material_code': 'TEST-003',
                'material_name': 'Invalid Material Type',
                'material_type': 'plastic',
                'material_buy_price': 100,
                'supplier_id': self.supplier.id,
            })

    def test_material_code_required(self):
        with self.assertRaises(Exception):
            self.env['material.registration'].create({
                'material_code': False,
                'material_name': 'Test Cotton',
                'material_type': 'cotton',
                'material_buy_price': 100,
                'supplier_id': self.supplier.id,
            })

    def test_material_name_required(self):
        with self.assertRaises(Exception):
            self.env['material.registration'].create({
                'material_code': 'TEST-004',
                'material_name': False,
                'material_type': 'cotton',
                'material_buy_price': 100,
                'supplier_id': self.supplier.id,
            })

    def test_material_type_required(self):
        with self.assertRaises(Exception):
            self.env['material.registration'].create({
                'material_code': 'TEST-005',
                'material_name': 'Material Without Type',
                'material_type': False,
                'material_buy_price': 100,
                'supplier_id': self.supplier.id,
            })

    def test_supplier_required(self):
        with self.assertRaises(Exception):
            self.env['material.registration'].create({
                'material_code': 'TEST-006',
                'material_name': 'Material Without Supplier',
                'material_type': 'cotton',
                'material_buy_price': 100,
                'supplier_id': False,
            })

    def test_material_buy_price_equal_100(self):
        material = self.env['material.registration'].create({
            'material_code': 'TEST-007',
            'material_name': 'Boundary Price Material',
            'material_type': 'cotton',
            'material_buy_price': 100,
            'supplier_id': self.supplier.id,
        })

        self.assertTrue(material)
        self.assertEqual(material.material_buy_price, 100)