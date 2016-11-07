import os, sys
import shutil
import string
import re
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.mp3 import HeaderNotFoundError
from database import db
from pymongo import DESCENDING, ASCENDING

pat = re.compile(r'\s+')
WORD_REGEX = re.compile(r'\w+')

class Organizer:
    results = {'success': 0, 'fail': 0, 'not mp3': 0}
    count = 0
    def word_list(self, strings):
        words = set()
        for string in strings:
            for match in WORD_REGEX.finditer(string):
                words.add(match.group(0).lower())
        return list(words)

    def clean_string(self, isaac):
        isaac = isaac.strip()
        isaac = pat.sub('_', isaac)
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in isaac if c in valid_chars)

    def organize_directory(self, source, destination):
        db.songs.ensure_index([('words', ASCENDING)])
        visited = set()
        self.results = {"success":0, "fail": 0, "not mp3": 0}
        self.count = 0
        for path, dirs, files in os.walk(source, followlinks=True):
            abspath = os.path.abspath(path)
            for file in files:
                full_filename = os.path.join(path, file)
                self.process_file(full_filename, destination)
                self.count += 1
            if abspath in visited:
                continue
            else:
                visited.add(abspath)
        
    def process_file(self, full_filename, destination, user=None):
        (basename, ext) = os.path.splitext(full_filename)
        if ext == ".mp3":
            try:
                audio = MP3(full_filename,ID3=EasyID3)
            except Exception:
                pass
            title = audio['title'][0]
            album = audio['album'][0]
            artist = audio['artist'][0]
            length = audio.info.length
            try:
                tracknumber = audio['tracknumber'][0]
            except Exception:
                tracknumber = 0
            firstchar = "_azn"
            for c in artist:
                if c in ("%s%s" % (string.ascii_letters, string.digits)):
                    firstchar = c.upper()
                    if firstchar in ("%s" % (string.digits)):
                        firstchar = "0-9"
                    break
            new_path = firstchar + os.sep + self.clean_string(artist).capitalize() + os.sep + self.clean_string(album).capitalize()
            new_full_path = os.path.join(destination,new_path)
            if not os.path.exists(new_full_path):
                os.makedirs(new_full_path)
            new_filename = self.clean_string(title) + ".mp3"
            new_basename = self.clean_string(title)
            dst = os.path.join(new_full_path,new_filename)
            i=2
            new_dst = dst
            while os.path.exists(new_dst):
                new_dst = new_full_path + new_basename + '_' + unicode(i) + ext
                i+=1
            dst = new_dst
            os.rename(full_filename, dst)
            song = db.songs.Song()
            song.title = unicode(title)
            song.album = unicode(album)
            song.artist = unicode(artist)
            song.tracknumber = unicode(tracknumber)
            song.length = float(length)
            if user != None:
                song.uploader = user
            fname = unicode(new_basename)
            (nbasename, ext) = os.path.splitext(new_filename)
            song_path = new_path + os.sep + nbasename
            if i > 2:
                song_path += u'_' + unicode(i-1) + unicode(ext)
            else:
                song_path += unicode(ext)
            song.path = unicode(song_path)
            song.duplicate = i-2
            song.words = self.word_list([song.title, song.album, song.artist])
            if db.songs.save(song):
                with open("/tmp/log", "a") as f:
                    f.write(str(song))
            else:
                with open("/tmp/log", "a") as f:
                    f.write("Didn't save shit")

            self.results['success'] += 1
        else:
            self.results['not mp3']  +=1
        
if __name__ == '__main__':
    sorter = Organizer()
    DATA_ROOT = "/pants"
    source = os.path.join(DATA_ROOT, "fuck")
    destination = os.path.join(DATA_ROOT, "ProcessedMusic")
    sorter.organize_directory(source, destination)
    print Organizer.results
