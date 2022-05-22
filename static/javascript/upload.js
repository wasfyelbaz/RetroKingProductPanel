$('#scrap-btn').prop('disabled', true);
$('#download-btn').prop('disabled', true);

$(document).ready(function(){
    $(".files").attr('data-before',"Drag file here or click the above button");
    $('input[type="file"]').change(function(e){
        var fileName = e.target.files[0].name;
        $(".files").attr('data-before',fileName);
    });
});

$('#upload-btn').click(function (event) {
   event.preventDefault()
   var file = $('#file').get(0).files[0];
   var formData = new FormData();
   formData.append('file', file);
   $.ajax({
       url: '/upload',
       // Ajax events
       success: function (e) {
         $('#upload-btn').prop('disabled', true);
         $('#scrap-btn').prop('disabled', false);
         swal("Success", "Successfully uploaded the sheet!", "success");
       },
       error: function (e) {
         swal ( "Oops", JSON.parse(e.responseText)["msg"], "error")
       },
       // Form data
       data: formData,
       type: 'POST',
       // Options to tell jQuery not to process data or worry about content-type.
       cache: false,
       contentType: false,
       processData: false
    });
    return false;
});

let check_csv_loop = true;

function check_csv(){
    $.ajax({
        url: '/csv?check=true',
        type: 'GET',
        success: function(data){
            // Perform operation on return value
            swal("Success", "Scraping finished, CSV is available to download", "success");
            $('#download-btn').prop('disabled', false);
            check_csv_loop = false;
        },
        complete:function(data){
            if (check_csv_loop) setTimeout(check_csv, 5000);
        }
    });
}

$('#scrap-btn').click(function (event) {
    event.preventDefault()

    $('#scrap-btn').prop('disabled', true);

    $.ajax({
        url: "/checkSheetFormat",
        type: 'GET',
        success: function(res) {
            swal("Scraping started", "Please wait until the scraping finish, thanks for your patience");
            $.ajax({
                url: "/scrap",
                type: 'GET'
            });

            setTimeout(check_csv,5000);

        },
        error: function (e) {
            $('#upload-btn').prop('disabled', false);
            swal ( "Oops", JSON.parse(e.responseText)["msg"], "error");
        }
    });
    return false;
});

$('#download-btn').click(function (event) {
    axios({
        url: '/csv',
        method:'GET',
        responseType: 'blob'
    })
    .then((response) => {
        const url = window.URL
        .createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'output.csv');
        document.body.appendChild(link);
        link.click();
        link.remove();
    })
    return false;
});
