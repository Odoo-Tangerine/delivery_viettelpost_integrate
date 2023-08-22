/** @odoo-module **/

import { useService } from '@web/core/utils/hooks';
import { ListController } from "@web/views/list/list_controller";

export class HandleButtonListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService('orm');
        this.actionService = useService('action');
        this.rpc = useService("rpc");
    }
    async onClickRegisterWarehouse() {
        this.actionService.doAction('tangerine_delivery_viettelpost.viettelpost_register_warehouse_action');
    }
}