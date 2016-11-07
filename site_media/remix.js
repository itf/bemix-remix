$(document).ready(function()
{
    $('#repeat').buttonset().click(function(event) {
        if(event.target.type != 'radio')
        {
                command('repeat');
        }
    });

    $('#progressbar').progressbar({
        value: 0
    });

    $('#volume').slider({max:100, min:10, range:'min',
        stop: function(event, ui)
      	{
            new_val=$('#volume').slider('value');
            $.ajax({url: '/remix/' + $('#player').val() + '/command/volset' + new_val});
        }
    });

    $('#player').change(function() {
	    window.location.hash = $('#player').val();
	    window.document.title = "Bemix: " + $('#player').val()
	    $('#query').val(""); search_handler()
	});

	info_update = function() {
        if ($("#player").val() != null) {
	       $.getJSON('/remix/' + $('#player').val() + '/info',
                function(data)
                {
                    // The play/pause button
                    if(data.state == 'playing')
                        $('#playpause').attr("src", "/site_media/pause.png");
                    else
                        $('#playpause').attr("src", "/site_media/play.png");

                    // Volume slider
                    $("#volume").slider("option", "value", data.volume);

                    // Repeat buttons
                    if(data.repeat) {
                        $('#repeat_on').click()
                        $("#repeat").buttonset("refresh");
                    } else {
                        $('#repeat_off').click()
                        $("#repeat").buttonset("refresh");
                    }

                    // Progress bar
                    $('#progresstext').html(data.time_at + ' / ' + data.time_total);
                    $('#progressbar').progressbar("value", data.percent);

                    // The queue
                    if(!dragging)
                    {
                        $('#sortable').html('')
                        for (i in data.queue)
                        {
                            q = data.queue[i]
                            cls = ''
                            if(q.place > 0)
                            {
                                cls=' sortme'
                            }
                            $('#sortable').append('<li class="ui-state-default' + cls + '" id="queue_' + q.place +'">' +
                                + (q.place+1) + ") " + q.title + ' - ' + q.artist + ' - ' + q.album + ' <a href="javascript:dequeue(' + q.place + ');">[X]</a>'
                             + '</li>');
                        }
                        $("#sortable").sortable("refresh")
                    }
                    // Update
                    window.setTimeout(info_update, 500);
                }
            ).error(function(){window.setTimeout(info_update, 500);});
        }
	}

	updatesort = function(event, ui) {
	    new_order = Array()
	    $(".sortme").each(function(i) {
	        new_order.push(this.id.split('_')[1])
	    })
	    request = new_order.join(',')
	    $.ajax({url: '/remix/' + $('#player').val() + '/requeue/' + request});
	}

	enqueue = function(song_id) {
		$.ajax({
		    url: '/remix/' + $('#player').val() + '/enqueue/' + song_id,
		});
	}
    enqueue_youtube = function(song_id) {
		$.ajax({
		    url: '/remix/' + $('#player').val() + '/enqueue_youtube/' + song_id,
		});
	}
	dequeue = function(position) {
		$.ajax({
		  url: '/remix/' + $('#player').val() + '/dequeue/' + position,
		});
	}
	command = function(cmd) {
		$.ajax({
		  url: '/remix/' + $('#player').val() + '/command/' + cmd,
		});
    }
    inityoutube = function() {
        gapi.client.setApiKey("AIzaSyAJQu47Nl-6_WzclB77cJYt5iQQEIsa5pU");
        gapi.client.load("youtube", "v3", function() {
            // yt api is ready
        });
    }

    search_youtube_handler = function(query){
       var request = gapi.client.youtube.search.list({
            part: "snippet",
            type: "video",
            q: encodeURIComponent(query).replace(/%20/g, "+"),
            maxResults: 5,
            order: "viewCount",
       }); 
       var videos =[]
       request.then(function(response) {
          var results = response.result;

          $("#resultsyoutube").html("");
          var res = "<table><tr class='rowtop'><th style='width:50%'>Youtube Title</th><th style='width:30%'> </th><th style='width:20%'> </th></tr>"
          $.each(results.items, function(index, item) {
            var s={"title":item.snippet.title, "id":item.id.videoId, "album": "", "artist":""}
            res += "<tr class='row" + ((index%2)+1) +"' onclick='enqueue_youtube(\"" + s.id + "\")'><td>" + s.title + "</td><td>" + s.album + "</td><td>" + s.artist + "</td></tr>"
          });
          res += "</table>"
          $('#resultsyoutube').html(res);

       });
    }
    
    
    search_handler = function() {
		var query = $('#query').val();
		if (query.length < 3)
		{
		        $('#results').html('');
		        $('#resultsyoutube').html('');
		        last_received = num_sent;
		        return;
		}
		if (query == last_query)
		        return;
		last_query = query;
		var request_id = ++num_sent;
		search_youtube_handler(query);
		$.getJSON('/remix/ajax_search',{query: $('#query').val()},
		        function(data)
		        {
		                if (request_id > last_received)
		                {
			                res = "<table><tr class='rowtop'><th style='width:50%'>Title</th><th style='width:30%'>Album</th><th style='width:20%'>Artist</th></tr>"
			                for(i in data.results)
		                    {
		                        s = data.results[i]
		                        res += "<tr class='row" + ((i%2)+1) +"' onclick='enqueue(\"" + s.id + "\")'><td>" + s.title + "</td><td>" + s.album + "</td><td>" + s.artist + "</td></tr>"
		                    }
                            res += "</table>"
                            $('#results').html(res);
			                last_received = request_id;
			            }
		        }
		);
	}
	hash = window.location.hash.substr(1)
	if(hash)
	{
	    if(hash != "uploads")
	    {
	        $('#player').val(hash).attr('selected', true)
	        window.document.title = "Bemix: " + $('#player').val()
	    }
	    else
	    {
	        $("#uploads_button").button().click()
	    }
	}
	else
	{
	    window.location.hash = $('#player').val()
	    window.document.title = "Bemix: " + $('#player').val()
	}

	$(window).bind('hashchange', function() {
	    if(window.location.hash != '#uploads')
	    {
            hash = window.location.hash.substr(1)
            $('#player').val(hash).attr('selected', true)
            window.document.title = "Bemix: " + $('#player').val()
            $("#uploads_back").button().click()
        }
        else
        {
            $("#uploads_button").button().click()
        }
    });
    num_sent = 0;
    last_received = 0;
    last_query = "";
    dragging = false;
    $('#query').keydown(search_handler);
	$('#query').keypress(search_handler);
	$('#query').keyup(search_handler);
	$('#query').blur(search_handler);
	search_handler();
	$("#sortable").sortable({
	    placeholder: "ui-state-highlight",
	    items:"li:.sortme",
	    update: updatesort,
	    start: function() { dragging = true; },
	    stop: function() { dragging = false; }
	});
    $("#sortable").disableSelection();
    $("#preferences_button").button({icons: {primary:'ui-icon-gear'}}).click(function(event,ui){$('#preferences').toggle("blind", { direction: "vertical" }, 500)});
    $('#preferences_submit').click(
        function(event, ui)
        {
            prefs = {
                'local_public': $('#local_public').attr('checked'),
                'style': $('#style').val()
            }
            $.post('/remix/preferences/',
                {'json': JSON.stringify(prefs)},
                function (data, textStatus, jqXHR) {
                        // maybe change the stylesheets...
                });
            $('#preferences').toggle("blind", {direction: "vertical" }, 500)
        }
        );
    $("#uploads_button").button().click(function(event, ui) {
        $('#wrap').css('display', 'none')
        $('#uploads').css('display', 'block')
        window.location.hash = 'uploads'
        $('#uploads_back').button().click(function(event, ui) {
            $('#wrap').css('display', 'block')
            $('#uploads').css('display', 'none')
            window.location.hash = '#' + $('#player').val()
        })
    })
    info_update();
});
