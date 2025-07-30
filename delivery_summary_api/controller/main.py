from odoo import http
from odoo.exceptions import AccessDenied
from odoo.http import request
import json
import ast
import jwt

SECRET_KEY = '123'  # Replace with your secure key

def jwt_required(fn):
    def wrapper(*args, **kwargs):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header:
            raise AccessDenied("Missing Authorization header")

        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            raise AccessDenied("Invalid Authorization header format")

        token = parts[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            kwargs['jwt_payload'] = payload  # Optional: pass the decoded payload
        except jwt.ExpiredSignatureError:
            raise AccessDenied("Token has expired")
        except jwt.InvalidTokenError:
            raise AccessDenied("Invalid token")
        return fn(*args, **kwargs)
    return wrapper

class DeliverySummaryController(http.Controller):

    @http.route('/api/v1/order-summary',type='http',auth='public',methods=['GET'],csrf=False)
    @jwt_required
    def order_summary(self, **kwargs):
        delivery_ids_str = kwargs.get('delivery_ids')
        template_ids = kwargs.get('product_templates')
        domain = []
        if delivery_ids_str:
                delivery_ids = ast.literal_eval(delivery_ids_str)
                domain.append(('picking_id','in',delivery_ids))
        if template_ids:
                template_ids = ast.literal_eval(template_ids)
                domain.append(('product_id.product_tmpl_id', 'in', template_ids))
        fields = ['product_id','product_uom_qty','picking_id']
        product_data = request.env['stock.move'].sudo().search_read(domain,fields)
        return request.make_response(json.dumps(product_data))