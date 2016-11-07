import pafy
import collections
import threading
lock = threading.Lock()

#http://stackoverflow.com/questions/2437617/limiting-the-size-of-a-python-dictionary
class MyDict(collections.MutableMapping):
  def __init__(self, maxlen, *a, **k):
    self.maxlen = maxlen
    self.d = dict(*a, **k)
    while len(self) > maxlen:
      self.popitem()
  def __iter__(self):
    return iter(self.d)
  def __len__(self):
    return len(self.d)
  def __getitem__(self, k):
    return self.d[k]
  def __delitem__(self, k):
    del self.d[k]
  def __setitem__(self, k, v):
    if k not in self and len(self) == self.maxlen:
      self.popitem()
    self.d[k] = v 

myDictCache = MyDict(200)

def getSongFromYoutube(song_id):
    
    url = song_id
    try:
        if (not song_id in myDictCache):
            video = pafy.new(url)
            a={}
            a['title']=video.title
            a['album']= video.rating
            a['artist']= video.author
            a['tracknumber']= 1
            a['length']= video.length
            a['path']="url"
            a['duplicate'] = 1,
            a['words']=""
            a['uploader']=""
            try:
                lock.acquire()
                myDictCache[song_id]=a
            finally:
                 # Always called, even if exception is raised in try block
                lock.release()
            return a
        else:
            return myDictCache[song_id]
    except:
        a={}
        a['title']=song_id
        a['album']= ""
        a['artist']= 1
        a['tracknumber']= 1
        a['length']= 300
        a['path']=""
        a['duplicate'] = 1,
        a['words']=""
        a['uploader']=""
        return a
