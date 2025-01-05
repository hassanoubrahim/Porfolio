$(document).ready(function() {
    $('#form').on('submit',function(e){
    $.ajax({
        data : {
        url : $('#url').val(),
        },
        type : 'POST',
        url : '/'
    })
    .done(function(data){
        $('#output').val(data.output);
        // $('#qr').html('<img class="img-fluid text-center" src="{{ qrcode('+data.output+') }}">');
        $('#url-wrapper').css({"display": "block"});
        $('#url').val('');
    });
    e.preventDefault();
    });
});

/* Initialization of datatable */
$(document).ready(function() {
    var table = $('#table_location').DataTable({ 
        dom: 'Bfrtip',
        buttons: [
            'copy', 'csv', 'excel', 'pdf', 'print'
        ],
        order: [[4, 'desc']],
});
});

function CopyText() {
    var copyText = document.getElementById("output");
    copyText.select();
    copyText.setSelectionRange(0, 99999);
    navigator.clipboard.writeText(copyText.value);
    
    var tooltip = document.getElementById("txttooltip");
    tooltip.innerHTML = "Copied";
  }
  
  function outFunc() {
    var tooltip = document.getElementById("txttooltip");
    tooltip.innerHTML = "Copy to clipboard";
  }