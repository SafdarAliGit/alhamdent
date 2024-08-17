frappe.ui.form.on("Landed Cost Voucher", {
    refresh(frm) {
        calculate_total_qty(frm);
    }

});
frappe.ui.form.on("Landed Cost Taxes and Charges", {
    amount: function (frm) {
        let total_amount = 0;
        let taxes = frm.doc.taxes;
        taxes.forEach(item => {
            total_amount += item.amount || 0;
        });

        let per_piece_expense = (flt(total_amount) / flt(frm.doc.total_qty));
        frm.set_value('per_piece_expense', per_piece_expense);
        refresh_field('per_piece_expense');

        let items = frm.doc.items;
        items.forEach(item => {
            if (item.rate) {
                item.rate += per_piece_expense;
            }
        });
        refresh_field('items');
    }

});
$(document).ajaxComplete(function (event, xhr, settings) {
    // Ensure 'frm' is available, assuming it is set globally
    if (typeof cur_frm !== 'undefined') {
        calculate_total_qty(cur_frm);
    }
});

function calculate_total_qty(frm) {
    let total_qty = 0;
    let items = frm.doc.items;

    items.forEach(item => {
        total_qty += item.qty || 0;
    });

    frm.set_value('total_qty', total_qty);
}


