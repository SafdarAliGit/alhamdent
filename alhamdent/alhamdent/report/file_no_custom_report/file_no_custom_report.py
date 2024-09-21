# my_custom_app.my_custom_app.report.daily_activity_report.daily_activity_report.py
import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Headings"),
            "fieldname": "heading",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("<b>Date</b>"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 150
        },
        {
            "label": _("<b>Supplier/Customer</b>"),
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 100
        },
        {
            "label": _("<b>Pur. Inv#</b>"),
            "fieldname": "voucher_no",
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 180
        },
        {
            "label": _("<b>Total Qty</b>"),
            "fieldname": "qty",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": _("<b>Rate</b>"),
            "fieldname": "rate",
            "fieldtype": "Currency",
            "width": 180
        },

        {
            "label": _("<b>Amount</b>"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 200
        }

    ]
    return columns


def get_conditions(filters, doctype):
    conditions = []
    if doctype in ["pii", "sii", "lcv","jea"]:
        conditions.append(f"`{doctype}`.file_no = %(file_no)s")
    return " AND ".join(conditions)


def get_data(filters):
    data = []

    purchase = """
                SELECT
                   '' AS heading,
                    pi.posting_date,
                    pi.supplier,
                    pi.name AS voucher_no,
                    SUM(pii.qty) AS qty,
                    AVG(pii.base_rate) AS rate,
                    pi.base_total AS amount,
                    pi.conversion_rate
                FROM
                    `tabPurchase Invoice` AS pi
                LEFT JOIN
                    `tabPurchase Invoice Item` AS pii ON pi.name = pii.parent
                WHERE
                    {conditions} 
                    AND 
                    pi.docstatus = 1
                GROUP BY
                    pi.name
                ORDER BY
                    pi.posting_date ASC
            """.format(conditions=get_conditions(filters, "pii"))

    sale = """
                SELECT
                   '' AS heading,
                    si.posting_date,
                    si.customer AS supplier,
                    si.name AS voucher_no,
                    SUM(sii.qty) AS qty,
                    AVG(sii.rate) AS rate,
                    si.grand_total AS amount
                FROM
                    `tabSales Invoice` AS si
                LEFT JOIN
                    `tabSales Invoice Item` AS sii ON si.name = sii.parent
                WHERE
                    {conditions} 
                    AND 
                    si.docstatus = 1
                GROUP BY
                    si.name
                ORDER BY
                    si.posting_date ASC
            """.format(conditions=get_conditions(filters, "sii"))

    landed_cost = """
                SELECT
                   '' AS heading,
                    lcv.posting_date,
                    lctc.description AS qty,
                    lcv.name AS voucher_no,
                    lctc.expense_account AS supplier,
                    '' AS rate,
                    lctc.amount
                FROM
                    `tabLanded Cost Voucher` AS lcv
                LEFT JOIN
                    `tabLanded Cost Taxes and Charges` AS lctc ON lcv.name = lctc.parent
                WHERE
                    {conditions} 
                    AND 
                    lcv.docstatus = 1
                """.format(conditions=get_conditions(filters, "lcv"))

    je = """
                    SELECT
                       '' AS heading,
                        je.posting_date,
                        jea.account AS supplier,
                        jea.parent AS voucher_no,
                        '' AS  qty,
                        '' AS rate,
                        jea.debit_in_account_currency AS amount
                    FROM
                        `tabJournal Entry` AS je
                    LEFT JOIN
                        `tabJournal Entry Account` AS jea ON je.name = jea.parent
                    WHERE
                        {conditions} 
                        AND 
                        jea.docstatus = 1
                        AND 
                        jea.debit_in_account_currency > 0
                """.format(conditions=get_conditions(filters, "jea"))

    purchase_result = frappe.db.sql(purchase, filters, as_dict=1)
    sale_result = frappe.db.sql(sale, filters, as_dict=1)
    landed_cost_result = frappe.db.sql(landed_cost, filters, as_dict=1)
    je_result = frappe.db.sql(je, filters, as_dict=1)
    #
    # ====================CALCULATING TOTAL IN PURCHASE====================
    purchase_header_dict = [
        {'heading': '<b><u>Purchase Detail</b></u>', 'posting_date': '', 'supplier': '', 'voucher_no': '', 'qty': '',
         'rate': '', 'amount': ''}]
    purchase_total_dict = {'heading': '<b>Total</b>', 'posting_date': '-------', 'supplier': '-------',
                           'voucher_no': '-------',
                           'qty': None, 'rate': None, ',' 'amount': None}
    total_qty = 0
    total_rate = 0
    total_conversion_rate = 0
    total_purchase_amount = 0
    avg_conversion_rate = 0
    for purchase in purchase_result:
        total_qty += purchase.qty
        total_rate += purchase.rate
        total_purchase_amount += purchase.amount
        total_conversion_rate += purchase.conversion_rate
    if len(purchase_result) != 0:
        avg_rate = total_rate / len(purchase_result)
        avg_conversion_rate = total_conversion_rate / len(purchase_result)
    else:
        # Handle the case where len(purchase_result) is zero
        avg_rate = 0  # or any other appropriate value
        avg_conversion_rate = 0

    purchase_total_dict['qty'] = total_qty
    purchase_total_dict['rate'] = avg_rate
    purchase_total_dict['amount'] = total_purchase_amount

    purchase_result = purchase_header_dict + purchase_result
    purchase_result.append(purchase_total_dict)
    # ====================CALCULATING TOTAL IN PURCHASE END====================
    # ====================CALCULATING TOTAL IN SALES====================
    sales_header_dict = [
        {'heading': '<b><u>Sales Detail</b></u>', 'posting_date': '', 'supplier': '', 'voucher_no': '', 'qty': '',
         'rate': '', 'amount': ''}]
    sales_total_dict = {'heading': '<b>Total</b>', 'posting_date': '-------', 'supplier': '-------',
                        'voucher_no': '-------',
                        'qty': None, 'rate': None, ',' 'amount': None}
    total_qty = 0
    total_rate = 0
    total_sale_amount = 0
    for sale in sale_result:
        total_qty += sale.qty
        total_rate += sale.rate
        total_sale_amount += sale.amount
    if len(sale_result) != 0:
        avg_rate = total_rate / len(sale_result)
    else:
        # Handle the case where len(purchase_result) is zero
        avg_rate = 0  # or any other appropriate value

    sales_total_dict['qty'] = total_qty
    sales_total_dict['rate'] = avg_rate
    sales_total_dict['amount'] = total_sale_amount

    sale_result = sales_header_dict + sale_result
    sale_result.append(sales_total_dict)
    # ====================CALCULATING TOTAL IN SALES END====================

    # # ====================CALCULATING TOTAL IN LANDED COST VOUCHER====================
    landed_cost_header_dict = [
        {'heading': '<b><u>Expense Detail</b></u>', 'posting_date': '-------', 'supplier': '-------',
         'voucher_no': '-------', 'qty': '-------',
         'rate': '-------', 'amount': ''},
        {'heading': '', 'posting_date': '-------', 'supplier': '<b>Account</b>',
         'voucher_no': '<b>LCV#</b>', 'qty': '<b>Description</b>',
         'rate': '-------', 'amount': ''}
    ]
    landed_cost_total_dict = {'heading': '<b>Total</b>', 'posting_date': '-------', 'supplier': '-------',
                              'voucher_no': '-------',
                              'qty': '-------', 'rate': '-------', 'amount': None}

    total_lc_amount = 0
    for lcr in landed_cost_result:
        total_lc_amount += lcr.amount

    landed_cost_total_dict['amount'] = total_lc_amount

    landed_cost_result = landed_cost_header_dict + landed_cost_result

    # ====================CALCULATING TOTAL IN JOURNAL ENTRY====================
    je_header_dict = [
        {'heading': '<b><u>Journal Entries</b></u>', 'posting_date': '', 'supplier': '', 'voucher_no': '', 'qty': '',
         'rate': '', 'amount': ''}]
    je_total_dict = {'heading': '<b>Total</b>', 'posting_date': '-------', 'supplier': '-------',
                           'voucher_no': '-------',
                           'qty': None, 'rate': None, ',' 'amount': None}
    total_je_amount = 0
    for je in je_result:
        total_je_amount += je.amount

    je_total_dict['amount'] = total_je_amount

    je_result = je_header_dict + je_result
    je_result.append(je_total_dict)

    # # ====================CALCULATING TOTAL IN LANDED COST VOUCHER END====================
    # SUMMARY
    total_cost = total_purchase_amount + total_je_amount
    total_cost_summary = {'heading': '<b>Total Expense</b>', 'posting_date': '-------', 'supplier': '-------',
                          'voucher_no': '-------',
                          'qty': '-------', 'rate': '-------', ',' 'amount': None}
    total_cost_summary['amount'] = total_cost
    cost_after_expense_summary = {'heading': '<b>Cost after Expense</b>', 'posting_date': '-------',
                                  'supplier': '-------',
                                  'voucher_no': '-------',
                                  'qty': '-------', 'rate': '-------', ',' 'amount': None}
    if total_qty != 0:
        cost_after_expense_summary['amount'] = total_cost / total_qty
    else:
        cost_after_expense_summary['amount'] = 0
    # PROFIT OF FILE
    profit_of_file = {'heading': '<b>Profit Of File</b>', 'posting_date': '-------', 'supplier': '-------',
                          'voucher_no': '-------',
                          'qty': '-------', 'rate': '-------', ',' 'amount': None}
    profit_of_file['amount'] = (total_sale_amount if total_sale_amount else 0) - (total_cost if total_cost else 0)
    # AVERAGE CONVERSION RATE
    purchase_conversion_rate = {'heading': '<b>Conversion Rate</b>', 'posting_date': '-------', 'supplier': '-------',
                      'voucher_no': '-------',
                      'qty': '-------', 'rate': '-------', ',' 'amount': None}
    purchase_conversion_rate['amount'] = avg_conversion_rate

    landed_cost_result.append(landed_cost_total_dict)
    landed_cost_result.append(total_cost_summary)
    landed_cost_result.append(profit_of_file)
    landed_cost_result.append(purchase_conversion_rate)
    landed_cost_result.append(cost_after_expense_summary)

    data.extend(purchase_result)

    data.extend(sale_result)

    data.extend(je_result)

    data.extend(landed_cost_result)

    return data
