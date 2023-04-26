frappe.ui.form.on("Lead",{
    ts_open_link: function(frm){
        if(!frm.doc.ts_map_link){
            cur_frm.scroll_to_field('ts_map_link')
            frappe.throw('Enter Google Map Link')
        }
        else{
        window.open(frm.doc.ts_map_link, '_blank')
        }
    },
})