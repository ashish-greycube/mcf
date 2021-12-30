frappe.ui.form.on('Lead', {
	refresh: function (frm) {
		if (!frm.doc.__islocal && frm.doc.__onload && !frm.doc.__onload.is_customer) {
			frm.add_custom_button('MCF Quotation', () => {
				make_quotation(frm)
			}, __('Create'));

		}
	},
})

function make_quotation(frm) {
	frappe.model.open_mapped_doc({
		method: "mcf.lead_controller.make_quotation",
		frm: frm
	})
}