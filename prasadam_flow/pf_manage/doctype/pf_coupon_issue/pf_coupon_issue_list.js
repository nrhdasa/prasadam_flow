frappe.listview_settings['PF Coupon Issue'] = {
    add_fields: ['used'],
    get_indicator(doc) {
        // customize indicator color
        if (doc.docstatus == 1) {
            if (doc.used) {
                return [__("Used"), "green", "used,=,1"];
            } else {
                return [__("Unused"), "darkgrey", "docstatus,=,1"];
            }
        } else {
            return [__("Draft"), "grey", "docstatus,=,0"];
        }
    },
}