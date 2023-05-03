frappe.ui.form.on("Sales Invoice",{
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


frappe.ui.form.on('Sales Invoice Item', {
    item_code(frm,cdt,cdn){
        let data=locals[cdt][cdn]
      
        if(data.item_code){
            transaction_history(data,frm)
            frm.fields_dict.transaction.html()
           }
        else{
            frm.fields_dict.transaction.html()
        }
 }})
 
 async function transaction_history(data,frm){
    await frappe.call({
        method: "hollow_blocks.hollow_blocks.custom.py.sales_invoice.last_invoice_item_rate",
        args: {
            customer: frm.doc.customer,
            item:data.item_code
        },
        callback(r) {
          
            let outstanding_amount =r.message
          
         frm.fields_dict.transaction
             .html(frappe.render_template("transaction_history", { outstanding_amount: outstanding_amount }));
            
         }
         
        })
    
 }