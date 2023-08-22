/** @odoo-module */

import { listView } from "@web/views/list/list_view";
import { HandleButtonListModel } from "./HandleButtonListModel";
import { HandleButtonListController } from "./HandleButtonListController";
import { registry } from "@web/core/registry";

export const HandleButtonListView = {
    ...listView,
    Model: HandleButtonListModel,
    Controller: HandleButtonListController,
    buttonTemplate: 'Sync.Buttons',
};

registry.category("views").add('handle_button_list', HandleButtonListView);