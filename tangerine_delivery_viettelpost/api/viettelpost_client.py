from typing import Dict, Any
from dataclasses import dataclass
from odoo import models
from odoo.exceptions import UserError
from .viettelpost_connection import ViettelpostConnection


@dataclass
class ViettelpostClient(ViettelpostConnection):
    carrier: models

    def __post_init__(self):
        self.conn = ViettelpostConnection(self.carrier)

    def get_token(self, payload: Dict[str, Any]):
        func_name = 'GetToken'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    def get_token_long_term(self, payload: Dict[str, Any]):
        func_name = 'GetTokenLongTerm'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    def sync_provinces(self):
        func_name = 'SyncProvinces'
        result = self.conn.execute_restful(func_name, 'GET')
        return self._validate_result(func_name, result)

    def sync_districts(self):
        func_name = 'SyncDistricts'
        result = self.conn.execute_restful(func_name, 'GET')
        return self._validate_result(func_name, result)

    def sync_wards(self):
        func_name = 'SyncWards'
        result = self.conn.execute_restful(func_name, 'GET')
        return self._validate_result(func_name, result)

    def sync_offices(self):
        func_name = 'SyncPostOffices'
        result = self.conn.execute_restful(func_name, 'GET')
        return self._validate_result(func_name, result)

    def sync_services(self, payload: Dict[str, Any]):
        func_name = 'SyncServices'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    def sync_extend_services(self, param: str):
        func_name = 'SyncExtendServices'
        result = self.conn.execute_restful(func_name, 'GET', param)
        return self._validate_result(func_name, result)

    def sync_warehouses(self):
        func_name = 'SyncWarehouses'
        result = self.conn.execute_restful(func_name, 'GET')
        return self._validate_result(func_name, result)

    def register_warehouse(self, payload: Dict[str, Any]):
        func_name = 'RegisterWarehouse'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    def get_rate(self, payload: Dict[str, Any]):
        func_name = 'GetRate'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    def get_matching_service(self, payload: Dict[str, Any]):
        func_name = 'GetMatchingService'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    def create_bill(self, payload: Dict[str, Any]):
        func_name = 'CreateBill'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    def update_bill(self, payload: Dict[str, Any]):
        func_name = 'UpdateBill'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    def get_link_print(self, payload: Dict[str, Any]):
        func_name = 'GetLinkPrint'
        result = self.conn.execute_restful(func_name, 'POST', **payload)
        return self._validate_result(func_name, result)

    @staticmethod
    def _validate_result(func_name: str, result):
        if isinstance(result, list):
            return result
        if result.get('status') != 200:
            raise UserError(f'Request API {func_name} error. {result.get("status")} - {result.get("message")}')
        if func_name == 'GetLinkPrint':
            return result.get('message', False)
        return result.get('data', False)
