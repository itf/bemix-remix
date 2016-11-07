player = function() {
     return $('#player').val()
}

command = function(cmd) {
	$.ajax({
	  url: '/remix/' + player() + '/command/' + cmd,
	});
}

requeue = function(event, ui) {
    new_order = Array()
    $(".sortme").each(function(i) {
        new_order.push(this.id.split('_')[1])
    })
    request = new_order.join(',')
    $.ajax({url: '/remix/' + player() + '/requeue/' + request});
}

enqueue = function(song_id) {
	$.ajax({
	    url: '/remix/' + player() + '/enqueue/' + song_id,
	});
}

dequeue = function(position) {
	$.ajax({
	  url: '/remix/' + player() + '/dequeue/' + position,
	});
}

info_update = function() {
    $.getJSON('/remix/' + player() + '/info',
            function(data)
            {
                if(data.state == 'playing')
                    btn = "pause"
                else
                    btn = "play"
                    
                $('#command_playpause').attr("src", "/site_media/" + btn + ".png")
                    
                $("#volume").slider("option", "value", data.volume);
                
                if(data.repeat) {
                    $('#repeat_on').click()
                    $("#repeat").buttonset("refresh");
                } else {
                    $('#repeat_off').click()
                    $("#repeat").buttonset("refresh");
                }
                
                $('#progress_text').html(data.time_at + ' / ' + data.time_total);
                $('#progress').progressbar("value", data.percent);
                
                now_playing = data.queue[0]
                if(now_playing)
                    $('#playing').html(now_playing.title + " by " + now_playing.artist)
                else
                    $('#playing').html("")
                    
                if(!dragging)
                {
                    $('#sortable').html('')
                    for (i in data.queue)
                    {
                        q = data.queue[i]
                        if(q.place > 0)
                        $('#sortable').append('<li class="sortme row' + q.place%2 + '" id="queue_' + q.place +'">'
                            + (q.place) + " - " + q.title + ' - ' + q.artist + ' - ' + q.album + ' <a href="javascript:dequeue(' + q.place + ');">[X]</a>'
                         + '</li>');
                    }
                    $("#sortable").sortable("refresh") 
                }
                if(data.queue[0])
                {
                    artist = data.queue[0].artist
                    album = data.queue[0].album
                    $('#album_art').attr('src', '/remix/get_album_art/?artist=' + artist + '&album=' + album)
                }
                else
                {
                    $('#album_art').attr('src', '/remix/get_album_art/?artist=sfjsgsfdg&album=sfjsgsfdg')
                }
                
                window.setTimeout(info_update, 500);
            }
    ).error(function(){ window.setTimeout(info_update, 500); });
}

search_handler = function() {
	var query = $('#query').val();
	if (query.length < 3)
	{
	        $('#results').html('');
	        last_received = num_sent;
	        return;
	}
	if (query == last_query)
	        return;
	last_query = query;
	var request_id = ++num_sent;
	$.getJSON('/remix/ajax_search',{query: $('#query').val()},
	        function(data)
	        {
	                if (request_id > last_received)
	                {
		                res = "<table><tr class='rowtop'><th style='width:50%'>Title</th><th style='width:30%'>Album</th><th style='width:20%'>Artist</th></tr>"
		                for(i in data.results)
	                    {
	                        s = data.results[i]
	                        res += "<tr class='row" + (i%2) +"' onclick='enqueue(\"" + s.id + "\")'><td>" + s.title + "</td><td>" + s.album + "</td><td>" + s.artist + "</td></tr>"
	                    }                            
                        res += "</table>"
                        $('#results').html(res);
		                last_received = request_id;
		            }
	        }
	);
}

$(document).ready(function() {
    $('#progress').progressbar({ value: 0 })
    $('#command_previous').click(function(){ command('prev'); })
    $('#command_next').click(function(){ command('next'); })
    $('#command_playpause').click(function(){ command('pause'); })
    $('#volume').slider({
        max:100, min:10, range:'min',
        stop: function(event, ui)
      	{
            $.ajax({url: '/remix/' + player() + '/command/volset' + $(this).slider('value')});
        }
    })
    $('#repeat').buttonset().click(function(event) {
        if(event.target.type != 'radio')
        {
                command('repeat');
        }
    })
    dragging = false
    $("#sortable").sortable({
	    placeholder: "ui-state-highlight", 
	    items:"li:.sortme", 
	    update: requeue,
	    start: function() { dragging = true; }, 
	    stop: function() { dragging = false; }
	})
    $("#sortable").disableSelection()
    $('#tabs').tabs()
    num_sent = 0;
    last_received = 0;
    last_query = "";
    $('#query').keydown(search_handler);
	$('#query').keypress(search_handler);
	$('#query').keyup(search_handler);
	$('#query').blur(search_handler);
	search_handler();
    info_update()
})