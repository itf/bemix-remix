4E Bemix System
===

Media server and distributed music playback.

Located on rum at `/opt/bemix`

## Setup
You can run this thing locally!

Install [MongoDB](http://docs.mongodb.org/manual/installation/)
It could be as easy as `sudo apt-get install mongodb`.

Install the requirements

    $ pip install -r requirements.txt

Start the dev server

    $ python manage.py runserver

Visit [http://localhost:8000](http://localhost:8000)

You will probably also want a node to play to.
Check out [Bemix Node](https://github.com/Donlanes/bemix-node).
You can set up a local node pointing to your localhost to try
out your local bemix.

## Todo and Possible Features
* UI Redesign
* Repeat is broken? -- No.
* Suggest songs (random or popular songs)
* Playlists
* Advanced searching (e.g., artist="foo")
* Shuffle queue
* Upload a file without drag and drop

## Features at the moment
* Commands: prev, next, pause, volup, voldown, addrandom, repeat, volset ( https://rum.mit.edu/remix/place-name/command/command-name )
