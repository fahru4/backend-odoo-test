import json
import logging

from odoo import http
from odoo.http import request
from werkzeug.wrappers import Response


_logger = logging.getLogger(__name__)


class MaterialController(http.Controller):

    @http.route(
        '/api/materials',
        type='http',
        auth='public',
        methods=['POST'],
        csrf=False
    )
    def create_material(self, **kwargs):
        try:
            # Read raw JSON body
            try:
                payload = json.loads(
                    request.httprequest.data.decode('utf-8')
                )
            except (ValueError, json.JSONDecodeError):
                return self._json_response(
                    {
                        'success': False,
                        'message': 'Invalid JSON payload'
                    },
                    status=400
                )

            required_fields = [
                'material_code',
                'material_name',
                'material_type',
                'material_buy_price',
                'supplier_id',
            ]

            errors = {}

            for field in required_fields:
                if field not in payload or payload[field] in [None, '']:
                    errors[field] = '{} is required'.format(field)

            if errors:
                return self._json_response(
                    {
                        'success': False,
                        'message': 'Validation error',
                        'errors': errors
                    },
                    status=400
                )

            allowed_types = [
                'fabric',
                'jeans',
                'cotton'
            ]

            if payload['material_type'] not in allowed_types:
                errors['material_type'] = (
                    'Material type must be fabric, jeans, or cotton'
                )

            try:
                material_buy_price = float(
                    payload['material_buy_price']
                )
            except (TypeError, ValueError):
                errors['material_buy_price'] = (
                    'Material buy price must be a number'
                )
                material_buy_price = None

            if (
                material_buy_price is not None
                and material_buy_price < 100
            ):
                errors['material_buy_price'] = (
                    'Material buy price must be greater than or equal to 100'
                )

            try:
                supplier_id = int(payload['supplier_id'])
            except (TypeError, ValueError):
                errors['supplier_id'] = 'Supplier ID must be valid'
                supplier_id = None

            supplier = None

            if supplier_id is not None:
                supplier = request.env[
                    'res.partner'
                ].sudo().browse(supplier_id).exists()

                if not supplier:
                    errors['supplier_id'] = 'Supplier not found'

            if errors:
                return self._json_response(
                    {
                        'success': False,
                        'message': 'Validation error',
                        'errors': errors
                    },
                    status=400
                )

            material = request.env[
                'material.registration'
            ].sudo().create({
                'material_code': payload['material_code'],
                'material_name': payload['material_name'],
                'material_type': payload['material_type'],
                'material_buy_price': material_buy_price,
                'supplier_id': supplier.id,
            })

            return self._json_response(
                {
                    'success': True,
                    'message': 'Material created successfully',
                    'data': {
                        'id': material.id,
                        'material_code': material.material_code,
                        'material_name': material.material_name,
                        'material_type': material.material_type,
                        'material_buy_price': material.material_buy_price,
                        'supplier': {
                            'id': material.supplier_id.id,
                            'name': material.supplier_id.name,
                        }
                    }
                },
                status=201
            )

        except Exception:
            _logger.exception(
                'Unexpected error while creating material'
            )

            return self._json_response(
                {
                    'success': False,
                    'message': 'Internal server error'
                },
                status=500
            )

    def _json_response(self, data, status=200):
        return Response(
            json.dumps(data),
            status=status,
            content_type='application/json'
        )

    @http.route(
        '/api/materials',
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False
    )
    def get_materials(self, **kwargs):
        try:
            material_type = request.httprequest.args.get('material_type')

            domain = []

            if material_type:
                allowed_types = [
                    'fabric',
                    'jeans',
                    'cotton'
                ]

                if material_type not in allowed_types:
                    return self._json_response(
                        {
                            'success': False,
                            'message': 'Validation error',
                            'errors': {
                                'material_type':
                                    'Material type must be fabric, jeans, or cotton'
                            }
                        },
                        status=400
                    )

                domain.append(
                    ('material_type', '=', material_type)
                )

            materials = request.env[
                'material.registration'
            ].sudo().search(domain)

            data = []

            for material in materials:
                data.append({
                    'id': material.id,
                    'material_code': material.material_code,
                    'material_name': material.material_name,
                    'material_type': material.material_type,
                    'material_buy_price': material.material_buy_price,
                    'supplier': {
                        'id': material.supplier_id.id,
                        'name': material.supplier_id.name,
                    }
                })

            return self._json_response(
                {
                    'success': True,
                    'data': data
                },
                status=200
            )

        except Exception:
            _logger.exception(
                'Unexpected error while getting materials'
            )

            return self._json_response(
                {
                    'success': False,
                    'message': 'Internal server error'
                },
                status=500
            )

    @http.route(
        '/api/materials/<int:material_id>',
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False
    )
    def get_material_detail(self, material_id, **kwargs):
        try:
            material = request.env[
                'material.registration'
            ].sudo().browse(material_id).exists()

            if not material:
                return self._json_response(
                    {
                        'success': False,
                        'message': 'Material not found'
                    },
                    status=404
                )

            return self._json_response(
                {
                    'success': True,
                    'data': {
                        'id': material.id,
                        'material_code': material.material_code,
                        'material_name': material.material_name,
                        'material_type': material.material_type,
                        'material_buy_price': material.material_buy_price,
                        'supplier': {
                            'id': material.supplier_id.id,
                            'name': material.supplier_id.name,
                        }
                    }
                },
                status=200
            )

        except Exception:
            _logger.exception(
                'Unexpected error while getting material detail'
            )

            return self._json_response(
                {
                    'success': False,
                    'message': 'Internal server error'
                },
                status=500
            )

    @http.route(
        '/api/materials/<int:material_id>',
        type='http',
        auth='public',
        methods=['PUT'],
        csrf=False
    )
    def update_material(self, material_id, **kwargs):
        try:
            material = request.env[
                'material.registration'
            ].sudo().browse(material_id).exists()

            if not material:
                return self._json_response(
                    {
                        'success': False,
                        'message': 'Material not found'
                    },
                    status=404
                )

            try:
                payload = json.loads(
                    request.httprequest.data.decode('utf-8')
                )
            except (ValueError, json.JSONDecodeError):
                return self._json_response(
                    {
                        'success': False,
                        'message': 'Invalid JSON payload'
                    },
                    status=400
                )

            if not payload:
                return self._json_response(
                    {
                        'success': False,
                        'message': 'No data provided'
                    },
                    status=400
                )

            allowed_fields = [
                'material_code',
                'material_name',
                'material_type',
                'material_buy_price',
                'supplier_id',
            ]

            values = {}
            errors = {}

            for field in payload:
                if field not in allowed_fields:
                    errors[field] = 'Field is not allowed'

            if 'material_code' in payload:
                if payload['material_code'] in (None, ''):
                    errors['material_code'] = 'material_code is required'
                else:
                    values['material_code'] = payload['material_code']

            if 'material_name' in payload:
                if payload['material_name'] in (None, ''):
                    errors['material_name'] = 'material_name is required'
                else:
                    values['material_name'] = payload['material_name']

            if 'material_type' in payload:
                allowed_types = [
                    'fabric',
                    'jeans',
                    'cotton'
                ]

                if payload['material_type'] not in allowed_types:
                    errors['material_type'] = (
                        'Material type must be fabric, jeans, or cotton'
                    )
                else:
                    values['material_type'] = payload['material_type']

            if 'material_buy_price' in payload:
                try:
                    material_buy_price = float(
                        payload['material_buy_price']
                    )

                    if material_buy_price < 100:
                        errors['material_buy_price'] = (
                            'Material buy price must be greater than or equal to 100'
                        )
                    else:
                        values['material_buy_price'] = material_buy_price

                except (TypeError, ValueError):
                    errors['material_buy_price'] = (
                        'Material buy price must be a number'
                    )

            if 'supplier_id' in payload:
                try:
                    supplier_id = int(payload['supplier_id'])

                    supplier = request.env[
                        'res.partner'
                    ].sudo().browse(supplier_id).exists()

                    if not supplier:
                        errors['supplier_id'] = 'Supplier not found'
                    else:
                        values['supplier_id'] = supplier.id

                except (TypeError, ValueError):
                    errors['supplier_id'] = 'Supplier ID must be valid'

            if errors:
                return self._json_response(
                    {
                        'success': False,
                        'message': 'Validation error',
                        'errors': errors
                    },
                    status=400
                )

            material.write(values)

            return self._json_response(
                {
                    'success': True,
                    'message': 'Material updated successfully',
                    'data': {
                        'id': material.id,
                        'material_code': material.material_code,
                        'material_name': material.material_name,
                        'material_type': material.material_type,
                        'material_buy_price':
                            material.material_buy_price,
                        'supplier': {
                            'id': material.supplier_id.id,
                            'name': material.supplier_id.name,
                        }
                    }
                },
                status=200
            )

        except Exception:
            _logger.exception(
                'Unexpected error while updating material'
            )

            return self._json_response(
                {
                    'success': False,
                    'message': 'Internal server error'
                },
                status=500
            )

    @http.route(
        '/api/materials/<int:material_id>',
        type='http',
        auth='public',
        methods=['DELETE'],
        csrf=False
    )
    def delete_material(self, material_id, **kwargs):
        try:
            material = request.env[
                'material.registration'
            ].sudo().browse(material_id).exists()

            if not material:
                return self._json_response(
                    {
                        'success': False,
                        'message': 'Material not found'
                    },
                    status=404
                )

            material.unlink()

            return self._json_response(
                {
                    'success': True,
                    'message': 'Material deleted successfully'
                },
                status=200
            )

        except Exception:
            _logger.exception(
                'Unexpected error while deleting material'
            )

            return self._json_response(
                {
                    'success': False,
                    'message': 'Internal server error'
                },
                status=500
            )