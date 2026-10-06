import json

from odoo import tools
from odoo.tests.common import HttpCase, tagged, HOST


@tagged('-at_install', 'post_install')
class TestMaterialController(HttpCase):

    def setUp(self):
        super(TestMaterialController, self).setUp()

        self.supplier = self.env['res.partner'].create({
            'name': 'API Test Supplier',
        })

    def _request(self, method, path, payload=None):
        self.env['base'].flush()

        url = 'http://%s:%s%s' % (
            HOST,
            tools.config['http_port'],
            path,
        )

        headers = {}
        data = None

        if payload is not None:
            headers['Content-Type'] = 'text/plain'
            data = json.dumps(payload)

        return self.opener.request(
            method,
            url,
            data=data,
            headers=headers,
            timeout=10,
        )

    def _create_material(
        self,
        material_code='API-001',
        material_name='API Cotton',
        material_type='cotton',
        material_buy_price=100,
    ):
        response = self._request(
            'POST',
            '/api/materials',
            {
                'material_code': material_code,
                'material_name': material_name,
                'material_type': material_type,
                'material_buy_price': material_buy_price,
                'supplier_id': self.supplier.id,
            }
        )

        self.assertEqual(response.status_code, 201)

        return response.json()['data']

    def test_create_material_success(self):
        response = self._request(
            'POST',
            '/api/materials',
            {
                'material_code': 'API-001',
                'material_name': 'API Cotton',
                'material_type': 'cotton',
                'material_buy_price': 100,
                'supplier_id': self.supplier.id,
            }
        )

        self.assertEqual(response.status_code, 201)

        result = response.json()

        self.assertTrue(result['success'])
        self.assertEqual(
            result['message'],
            'Material created successfully'
        )
        self.assertEqual(
            result['data']['material_code'],
            'API-001'
        )
        self.assertEqual(
            result['data']['material_type'],
            'cotton'
        )
        self.assertEqual(
            result['data']['material_buy_price'],
            100.0
        )

    def test_create_material_price_below_100(self):
        response = self._request(
            'POST',
            '/api/materials',
            {
                'material_code': 'API-INVALID-PRICE',
                'material_name': 'Invalid Price',
                'material_type': 'cotton',
                'material_buy_price': 99,
                'supplier_id': self.supplier.id,
            }
        )

        self.assertEqual(response.status_code, 400)

        result = response.json()

        self.assertFalse(result['success'])
        self.assertEqual(
            result['message'],
            'Validation error'
        )
        self.assertIn(
            'material_buy_price',
            result['errors']
        )

    def test_get_all_materials(self):
        self._create_material(
            material_code='API-LIST-001',
            material_name='List Material',
        )

        response = self._request(
            'GET',
            '/api/materials'
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertTrue(result['success'])

        material_codes = [
            material['material_code']
            for material in result['data']
        ]

        self.assertIn(
            'API-LIST-001',
            material_codes
        )

    def test_filter_material_by_type(self):
        self._create_material(
            material_code='API-COTTON-001',
            material_name='Cotton Material',
            material_type='cotton',
        )

        self._create_material(
            material_code='API-JEANS-001',
            material_name='Jeans Material',
            material_type='jeans',
        )

        response = self._request(
            'GET',
            '/api/materials?material_type=cotton'
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertTrue(result['success'])

        material_codes = [
            material['material_code']
            for material in result['data']
        ]

        self.assertIn(
            'API-COTTON-001',
            material_codes
        )

        self.assertNotIn(
            'API-JEANS-001',
            material_codes
        )

        for material in result['data']:
            self.assertEqual(
                material['material_type'],
                'cotton'
            )

    def test_get_material_detail_success(self):
        material = self._create_material(
            material_code='API-DETAIL-001',
            material_name='Detail Material',
        )

        response = self._request(
            'GET',
            '/api/materials/%s' % material['id']
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertTrue(result['success'])
        self.assertEqual(
            result['data']['id'],
            material['id']
        )
        self.assertEqual(
            result['data']['material_code'],
            'API-DETAIL-001'
        )

    def test_get_material_detail_not_found(self):
        response = self._request(
            'GET',
            '/api/materials/999999'
        )

        self.assertEqual(response.status_code, 404)

        result = response.json()

        self.assertFalse(result['success'])
        self.assertEqual(
            result['message'],
            'Material not found'
        )

    def test_update_material_success(self):
        material = self._create_material(
            material_code='API-UPDATE-001',
            material_name='Before Update',
        )

        response = self._request(
            'PUT',
            '/api/materials/%s' % material['id'],
            {
                'material_name': 'After Update',
                'material_buy_price': 150,
            }
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertTrue(result['success'])
        self.assertEqual(
            result['message'],
            'Material updated successfully'
        )
        self.assertEqual(
            result['data']['material_code'],
            'API-UPDATE-001'
        )
        self.assertEqual(
            result['data']['material_name'],
            'After Update'
        )
        self.assertEqual(
            result['data']['material_buy_price'],
            150.0
        )

    def test_update_material_invalid_price(self):
        material = self._create_material(
            material_code='API-UPDATE-INVALID',
            material_name='Invalid Update',
        )

        response = self._request(
            'PUT',
            '/api/materials/%s' % material['id'],
            {
                'material_buy_price': 99,
            }
        )

        self.assertEqual(response.status_code, 400)

        result = response.json()

        self.assertFalse(result['success'])
        self.assertEqual(
            result['message'],
            'Validation error'
        )
        self.assertIn(
            'material_buy_price',
            result['errors']
        )

    def test_delete_material(self):
        material = self._create_material(
            material_code='API-DELETE-001',
            material_name='Delete Material',
        )

        response = self._request(
            'DELETE',
            '/api/materials/%s' % material['id']
        )

        self.assertEqual(response.status_code, 200)

        result = response.json()

        self.assertTrue(result['success'])
        self.assertEqual(
            result['message'],
            'Material deleted successfully'
        )

        second_response = self._request(
            'DELETE',
            '/api/materials/%s' % material['id']
        )

        self.assertEqual(
            second_response.status_code,
            404
        )

        second_result = second_response.json()

        self.assertFalse(second_result['success'])
        self.assertEqual(
            second_result['message'],
            'Material not found'
        )