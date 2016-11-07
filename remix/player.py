from bson.objectid import ObjectId
import datetime

class Player(object):
    HISTORY_LENGTH = 50

    def __init__(self, name=None, mongo_object=None):
        mongo_dict = mongo_object
        if mongo_dict is not None:
            self.mongo_id = mongo_dict['_id']
            self.name = mongo_dict['name']
            self.queue = mongo_dict['queue']
            self.history = mongo_dict['history']
            self.state = mongo_dict['state']
            self.position = mongo_dict['position']
            self.volume = mongo_dict['volume']
            self.repeat = mongo_dict['repeat']
            self.last_tick = mongo_dict['last_tick']
            self.owner = mongo_dict['owner']

            # song_index ensures that each song is treated as
            # unique, despite the song's name. Otherwise a queue
            # of the same song will break the node.
            self.song_index = mongo_dict.get('song_index', 0)

        else:
            self.mongo_id = None
            self.name = name
            self.queue = []
            self.history = []
            self.state = 'playing'
            self.position = 0.0
            self.volume = 100
            self.repeat = False
            self.last_tick = None
            self.owner = 'sys'
            self.song_index = 0

    def to_mongo_dict(self):
        self.history = self.history[-self.HISTORY_LENGTH:]

        mongo_dict = {
            'name': self.name,
            'queue': self.queue,
            'history': self.history,
            'state': self.state,
            'position': self.position,
            'volume': self.volume,
            'repeat': self.repeat,
            'last_tick': self.last_tick,
            'owner': self.owner,
            'song_index': self.song_index,
        }

        if self.mongo_id is not None:
            mongo_dict['_id'] = self.mongo_id

        return mongo_dict


    def previous_song(self):

        self.song_index += 1

        if self.repeat:
            if len(self.queue) > 0:
                self.queue.insert(0, self.queue.pop())
        else:
            if len(self.history) > 0:
                self.queue.insert(0, self.history.pop())

    def next_song(self):
        if len(self.queue) == 0:
            return

        self.song_index += 1

        if self.repeat:
            self.queue.append(self.queue[0])
        else:
            self.history.append(self.queue[0])
        self.queue.pop(0)

    def pause(self):
        self.state = 'paused'

    def start(self):
        self.state = 'playing'

    def volume_up(self):
        self.volume = min(100, self.volume + 10)

    def volume_down(self):
        self.volume = max(10, self.volume - 10)

    def volume_set(self, value):
        self.volume = max(10, min(100, value))

    @property
    def current_song(self):
        if len(self.queue) > 0:
            return self.queue[0]
        else:
            return None

    def enqueue(self, song):
        if len(self.queue) == 0:
            self.song_index += 1
        queue_object={}
        queue_object["song"]=song
        queue_object["source"]="local"
        self.queue.append(queue_object)

    def enqueue_youtube(self, youtube_url):
        if len(self.queue) == 0:
            self.song_index += 1
        queue_object={}
        queue_object["song"]=youtube_url
        queue_object["source"]="youtube"
        self.queue.append(queue_object)

    def dequeue(self, index):
        self.queue.pop(index)

    def tick(self, info):
        self.last_tick = datetime.datetime.now()
        if 'finished' in info:
            if info['source']=='local':
                if ObjectId(info['finished']) == self.current_song["song"]:
                    self.next_song()
            if info['source']=='youtube':
                if info['finished'] == self.current_song["song"]:
                    self.next_song()
        if 'position' in info:
            self.position = float(info['position'])

        song = None
        if self.current_song != None:
            song = str(self.current_song["song"])
            source = str(self.current_song["source"])
        if (song ==None):
            song=None
            source=None
        return {
            'state': self.state,
            'volume': self.volume,
            'song': song,
            'song_source': source,
            'song_index': self.song_index,
        }


