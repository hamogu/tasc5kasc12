/* Formatting function for row details - modify as you need */
function format ( d ) {
    // `d` is the original data object for the row
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
        '<tr>'+
            '<td>idnum:</td>'+
            '<td>'+d.idnum+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td>Authors:</td>'+
            '<td>'+d.authorlist+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td>Schedule / Location:</td>'+
            '<td>'+d.loctime+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td>Contact:</td>'+
            '<td>'+d.authoremail+'</td>'+
        '</tr>'+
	'<tr>'+
            '<td>Affiliations:</td>'+
            '<td>'+d.affiliations+'</td>'+
        '</tr>'+
	'<tr>'+
            '<td>Supp. material:</td>'+
            '<td>'+d.link+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td>Abstract:</td>'+
            '<td>'+d.abstract+'</td>'+
        '</tr>'+
    '</table>';
}
 
$(document).ready(function() {
    var table = $('#example').DataTable( {
        "ajax": "data/abstracts.json",
        "columns": [
            {
                "className":      'details-control',
                "orderable":      false,
                "data":           null,
                "defaultContent": ''
            },
            { "data": "type" },
            { "data": "idnum" },
            { "data": "title" },
            { "data": "authorlist", "visible": false },
	    { "data": "affiliations", "visible": false },
	    { "data": "abstract", "visible": false },
	    { "data": "authoremail", "visible": false},
	    { "data": "link", visible: false},
	    { "data": "loctime", visible: false},
	    { "data": "index", visible: false},
        ],
        "order": [[2, 'asc']],
    } );
     
    // Add event listener for opening and closing details
    $('#example tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
 
        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
	    MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
        }
    } );
} );
