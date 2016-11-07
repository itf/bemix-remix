var id = 0;

function cancel(id){
    $("#file_" + id).remove();
}
function handle_uploads(){
    $('#uploadArea').fileupload({
        url: "/uploader/do_upload/",
        sequentialUploads: true,
        add: function (e,data){
                id+=1;
                $('#uploadArea').append('<div class="songRow" id="file_'+id + '"> ' +  '</div>');
                data.div = "#file_"+id; 
                data.id = id;
                $(data.div).progressbar({
                    value: 0
                }); 
            var jqXHR = data.submit()
                .success( function (result,textStatus,jqXHR) {})
                .error( function (jqXHR,textStatus,errorThrow) {})
                .complete( function (result,textStatus,jqXHR) {});
            
            }
        })
       .bind('fileuploadprogress', function (e, data) {
           var percent = parseInt(data.loaded/data.total * 100,10);
           $(data.div).progressbar({value: percent});
            } 
           )
        .bind('fileuploadprogressall', function (e, data) {/* ... */})
        .bind('fileuploadstart', function (e) {})
        .bind('fileuploadstop', function (e) {/* ... */})
        .bind('fileuploaddone',function(e,data){
        var form ="<form>";
        var result =  JSON.parse(data.result);
        form += '<input class="inLabel" type="text" id="title_' + data.id+'" value="'+ result.title + '"> </input>';
        form += '<input class="inLabel" type="text" id="artist_' + data.id+'" value="'+ result.artist + '"> </input>';
        form += '<input class="inLabel" type="text" id="album_' + data.id+'" value="'+ result.album + '"> </input>';
        form += '<input type="hidden" id="filename_'+ data.id +'" value="' + result.full_filename + '"></input>';
        form += '<input class="control_button" type="button" value="Cancel" onClick="cancel(' + data.id + ');" /> ';
        form += '<input class="control_button save_button" type="button" value="Save" onClick="sendData(' + data.id + ');" /> ';
        form +="</form>";
       $(data.div).html("");
       $(data.div).append(form);
    });   
}

function sendData(sid)
{
    title = $('#title_' + sid).val()
    artist = $('#artist_' + sid).val()
    album = $('#album_' + sid).val()
    full_filename = $('#filename_' + sid).val()
    
    $.post('/uploader/tag_file/', {'title': title, 'artist': artist, 'album': album, 'full_filename':full_filename},
    function success(data, textStatus, jqXHR)
    {
        js = JSON.parse(data)
        if(js.success)
            $('#file_' + sid).fadeOut(250, function() { $('#file_' + sid).remove(); });
        else
            $('#file_' + sid).css('background-color', 'red')
    });
}

function saveAll()
{
    t= 0;
    $('.save_button').each(function(i,e)
    {
        setTimeout(function(){ 
        e.click()
        },250*t);
        t++;
    });
}

$(document).ready(function(){
    handle_uploads();
});
