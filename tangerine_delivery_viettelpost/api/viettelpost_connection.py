import json
import requests
from dataclasses import dataclass
from typing import Dict, Any, NoReturn
from datetime import datetime
from odoo import models, _, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import ustr

API_ROUTES = {
    'GetToken': '/v2/user/Login',
    'GetTokenLongTerm': '/v2/user/ownerconnect',
    'SyncProvinces': '/v2/categories/listProvinceById?provinceId=-1',
    'SyncDistricts': '/v2/categories/listDistrict?provinceId=-1',
    'SyncWards': '/v2/categories/listWards?districtId=-1',
    'SyncPostOffices': '/v2/categories/listBuuCucVTP',
    'SyncServices': '/v2/categories/listService',
    'SyncExtendServices': '/v2/categories/listServiceExtra?serviceCode={}',
    'SyncWarehouses': '/v2/user/listInventory',
    'GetRate': '/v2/order/getPrice',
    'GetMatchingService': '/v2/order/getPriceAll',
    'CreateBill': '/v2/order/createOrder',
    'UpdateBill': '/v2/order/UpdateOrder',
    'GetLinkPrint': '/v2/order/printing-code',
    'RegisterWarehouse': '/v2/user/registerInventory'
}


@dataclass
class ViettelpostConnection:
    carrier: models

    @staticmethod
    def _build_header(func_name: str, token: str) -> Dict[str, Any]:
        header = {'Content-Type': 'application/json'}
        if func_name != 'GetToken':
            header.update({'Token': token})
        return header

    @staticmethod
    def _validate_func_name(func_name: str) -> NoReturn:
        if func_name not in API_ROUTES:
            raise UserError(_(f'The routes {func_name} not found.'))

    @staticmethod
    def _get_message_and_status(result) -> (str, int):
        if isinstance(result, dict):
            message = result.get('message')
            status = result.get('status')
        else:
            message = 'OK'
            status = 200
        return message, status

    def execute_restful(self, func_name, method, *args, **kwargs):
        self._validate_func_name(func_name)
        try:
            header = self._build_header(func_name, self.carrier.viettelpost_token)
            endpoint = self.carrier.viettelpost_host + API_ROUTES[func_name].format(*args)
            if method == 'POST':
                response = requests.post(endpoint, json=kwargs, headers=header, timeout=300)
            elif method == 'GET':
                response = requests.get(endpoint, headers=header, timeout=300)
            else:
                raise UserError(_('The method invalid'))
            response.raise_for_status()
            result = response.json()
            if response.status_code != 200:
                raise UserError(_(f'Request Name {func_name} error.'))
            message, status = self._get_message_and_status(result)
            self._create_request_history(func_name, method, self.carrier.viettelpost_host, kwargs, message, status)
            return result
        except Exception as e:
            raise UserError(ustr(e))

    def _get_sequence_request_id(self) -> str:
        sequence = self.carrier.env.ref('tangerine_delivery_viettelpost.seq_request_api_viettelpost')
        next_document = sequence.get_next_char(sequence.number_next_actual)
        self.carrier.env.cr.execute('''SELECT request_id FROM viettelpost_connect_history''')
        query_res = self.carrier.env.cr.fetchall()
        while next_document in [res[0] for res in query_res]:
            next_tmp = self.carrier.env['ir.sequence'].next_by_code('viettelpost.connect.history')
            next_document = next_tmp
        return next_document

    def _create_request_history(self, func_name, method, url, body, msg, status):
        create_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        uid = self.carrier.env.uid
        sequence = self._get_sequence_request_id()
        self.carrier.env['viettelpost.connect.history'].create({
            'name': func_name,
            'method': method,
            'url': url,
            'body': body,
            'message': msg,
            'status': status,
            'request_id': sequence,
            'create_date': create_date,
            'create_uid': uid
        })
        self.carrier.env.cr.commit()
