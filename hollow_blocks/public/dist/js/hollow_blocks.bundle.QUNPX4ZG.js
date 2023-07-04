(() => {
  // frappe-html:/home/frappe/frappe-bench/apps/hollow_blocks/hollow_blocks/public/html/transaction_history.html
  frappe.templates["transaction_history"] = `

   
<table class="tab1">
   
	<thead>
		<tr>
            <th style="width: 06%">{%= __("S.No") %}</th>
			<th style="width: 06%">{%= __("Item") %}</th>
			<th style="width: 12%">{%= __("Rate") %}</th>
            <span class="close-x" onclick="cur_frm.fields_dict.transaction.html(); return false;">x</span>
			
		</tr>
	</thead>
    <tbody>
		{% for(var i=0, l=outstanding_amount.length; i<l; i++) { %}
			<tr>
			
				<td>{%= i+1 %}</td>
				<td>{%= outstanding_amount[i]["item_name"] %}</td>
                <td>{%= outstanding_amount[i]["rate"] %}</td>
				
				
           
			</tr>
		{% } %}
	</tbody>
</table>

`;
})();
//# sourceMappingURL=hollow_blocks.bundle.QUNPX4ZG.js.map
