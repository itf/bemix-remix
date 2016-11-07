import re

WORD_REGEX = re.compile(r'\w+')

'''
word_list returns a list of words found in its arguments for efficient searching
'''
def word_list(*strings):
    words = set()
    for string in strings:
        for match in WORD_REGEX.finditer(string):
            words.add(match.group(0).lower())
    return list(words)

def mongo_words_query(string):
    #TODO: make sure this won't make super-slow regexes
    regexes = []
    for word in word_list(string):
        regexes.append(re.compile('^' + word))
    return {'$all': regexes}
