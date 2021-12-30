from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from erpnext import get_default_company
from frappe.utils import get_link_to_form

@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	new_item=make_item(source_name)
	def set_missing_values(source, target):
		_set_missing_values(source, target)

	target_doc = get_mapped_doc("Lead", source_name,
		{"Lead": {
			"doctype": "Quotation",
			"field_map": {
				"name": "party_name"
			}
		}}, target_doc, set_missing_values)
	target_doc.append("items", {
			"item_code": new_item,
			"qty": 1
		})
	target_doc.quotation_to = "Lead"

	target_doc.run_method("set_missing_values")
	target_doc.run_method("set_other_charges")
	target_doc.run_method("calculate_taxes_and_totals")

	return target_doc

def _set_missing_values(source, target):
	if not source.company:
		default_company=get_default_company()
		if not default_company:
			frappe.throw(_('Please set default company in {}.'.format(get_link_to_form('Global Defaults','Global Defaults'))))

	address = frappe.get_all('Dynamic Link', {
			'link_doctype': source.doctype,
			'link_name': source.name,
			'parenttype': 'Address',
		}, ['parent'], limit=1)

	contact = frappe.get_all('Dynamic Link', {
			'link_doctype': source.doctype,
			'link_name': source.name,
			'parenttype': 'Contact',
		}, ['parent'], limit=1)

	if address:
		target.customer_address = address[0].parent

	if contact:
		target.contact_person = contact[0].parent

def make_item(lead_name):
	default_item_group = frappe.db.get_single_value('Stock Settings', 'item_group')
	default_stock_uom= frappe.db.get_single_value('Stock Settings', 'stock_uom')
	if not default_item_group:
		frappe.throw(_('Please set default item group in {}.'.format(get_link_to_form('Stock Settings','Stock Settings'))))	
	if not default_stock_uom:
		frappe.throw(_('Please set default stock uom in {}.'.format(get_link_to_form('Stock Settings','Stock Settings'))))			
	lead=frappe.get_doc('Lead',lead_name)
	doc = frappe.new_doc('Item')
	if frappe.db.get_default("item_naming_by") != "Naming Series":	
		doc.update({'item_code':lead.item_name_cf})
	doc.update({
			'item_name':lead.item_name_cf,
			'description':lead.item_description_cf,
			'company_logo_cf':lead.company_logo_cf,
			'total_length_cf':lead.total_length_cf,
			'gsm_cf':lead.gsm_cf,
			'length_cf':lead.length_cf,
			'width_cf':lead.width_cf,
			'height_cf':lead.height_cf,
			'ply_type_cf':lead.ply_type_cf,
			'flute_type_cf':lead.flute_type_cf,
			'paper_type_top_cf':lead.paper_type_top_cf,
			'paper_type_flute_cf':lead.paper_type_flute_cf,
			'paper_type_center_cf':lead.paper_type_center_cf,
			'paper_type_inside_cf':lead.paper_type_inside_cf,
			'paper_type_flute2_cf':lead.paper_type_flute2_cf,
			'style_cf':lead.style_cf,
			'special_flap_cf':lead.special_flap_cf,
			'number_of_out_cf':lead.number_of_out_cf,
			'joint_type_cf':lead.joint_type_cf,
			'print_type_cf':lead.print_type_cf,
			'no_of_colors_cf':lead.no_of_colors_cf
	})
	doc.run_method("set_missing_values")
	doc.flags.ignore_permissions = True
	doc.save()
	return doc.name		