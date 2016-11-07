var state = "waiting";
var player_name = "javascript_test";
var song = "";
var position = 0.0;
var started = 0;
 
function doPost(url,req)
{
    $.post(url,{'json': JSON.stringify(req)}, function(data) {handleResponse(data);},'json');
}
 
function start(new_name)
{
    player_name = new_name
    started = 1;    
    jwplayer("container").setup(
        {
            autostart: true,
            controlbar: "none",
            duration: 57,
            flashplayer: "/site_media/jwplayer/player.swf",
            volume: 80,
            width: 120,
            height: 120
    });
    jwplayer("container").onComplete(
        function(event) 
        {
            state = 'finished-song';
        }
    );

setInterval(tick,1000);
}
function loaded()
{
    return (jwplayer().getPlaylist().length > 0)
}
 
function load(song_id)
{
    jwplayer().load( [{provider:"sound",title:"test",file: "https://hbf.mit.edu/remix_player/get/" + song_id}]); 
}

function tick()
{
    if(started)
    {
        req = {'name': player_name};
        if(loaded())
        {
            position = jwplayer().getPosition();
            req['position'] = position * 1.0;
        }
        else
        {
            req['position'] = 0;
        }   
        if(state=="finished-song")
        {
            req['finished']  = song;
            state = 'not-finished';
        }
        doTickRequest(req); 
        return true;
    }
}
 
function doTickRequest(req)
{   
    doPost("https://hbf.mit.edu/remix_player/tick", req);
    return true;
}
 
function handleResponse(res)
{
    jwplayer().setVolume(res['volume']);
    if(song != res['song'])
    {
        song = res['song'];
        if(res['song']!=null)
            load(res['song']);
        else
            jwplayer().stop();
    }   
    if(song != 'none')
    {
        if(res['state']=='playing')
            jwplayer().play(true);
        else if(res['state']=='paused')
            jwplayer().play(false);
    }
    if(res['song']==null)
    {
        jwplayer().stop();
    }   
    return true;
}

