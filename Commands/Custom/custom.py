import json
import re

TYPE = 'tip'
LINK = 'link'
AUTHOR = 'autor'
PHRASE = 'fraza'
TITLE = 'naslov'
ADD = 'dodaj'
REMOVE = 'obrisi'
REGEX = 'regex'

ALLOWED_TYPES = ['img', 'vid', 'msg']

class Custom:
    CUSTOM_EVENTS_FOR_ALL = './Commands/Custom/custom_for_all.json'
    CUSTOM_EVENTS_FOR_ONE = './Commands/Custom/custom_for_one.json'
    CUSTOM_EVENTS_REGEX   = './Commands/Custom/custom_regex.json'

    AUTHOR_RE = r'(autor)\=\[([^\]]+)\]'
    PHRASE_RE = r'(fraza)\=\[([^\]]+)\]'
    TYPE_RE = r'(tip)\=\[(img|msg|vid)\]'
    LINK_RE = r'(link)\=\[([^\]]+)\]'
    TITLE_RE = r'(naslov)\=\[([^\]]+)\]'
    REGEX_RE = r'(regex)\=\`([^\`]+)\`'

    CAPTURES = [AUTHOR_RE, PHRASE_RE, TYPE_RE, LINK_RE, TITLE_RE, REGEX_RE]

    custom_events_all = {}
    custom_events_one = {}
    custom_events_regex = {}

    def __init__(self):
        with open(self.CUSTOM_EVENTS_FOR_ALL, encoding='UTF-8') as f:
            self.custom_events_all = json.load(f)
        with open(self.CUSTOM_EVENTS_FOR_ONE, encoding='UTF-8') as f:
            self.custom_events_one = json.load(f)
        with open(self.CUSTOM_EVENTS_REGEX, encoding='UTF-8') as f:
            self.custom_events_regex = json.load(f)

    def ProcessCommand(self, words: list) -> bool:
        if len(words) == 0: return False
        if words[0] != ADD and words[0] != REMOVE: return False
        
        entry = {AUTHOR: None, PHRASE: None, TYPE: None, LINK: None, TITLE: None, REGEX: None}
        args = ' '.join(words[1:]).lower()

        for reg in self.CAPTURES:
            catch = re.search(reg, args)
            if catch is not None:
                catch = catch.groups()
                entry[catch[0]] = catch[1]

        if words[0] == REMOVE:
            return self.RemoveCustomEventGeneral(entry[PHRASE]) if entry[AUTHOR] is None \
                else self.RemoveCustomEventSingle(entry[AUTHOR], entry[PHRASE])
        
        if entry[LINK] is None and entry[TITLE] is None: return False

        if entry[PHRASE] is None and entry[REGEX] is not None:
            return self.AddCustomEventRegex(entry)
        
        if entry[TYPE] is None or entry[PHRASE] is None: return False
                    
        return self.AddCustomEventSingle(entry) if entry[AUTHOR] is not None \
                else self.AddCustomEventGeneral(entry)
        
    def CheckForCustomEventAll(self, words: list) -> dict:
        specials = [word.lower() for word in words if word in self.custom_events_all.keys()]
        specials.append(' '.join(words).lower())
        if len(specials) == 0: 
            return None
        return [value for key, value in self.custom_events_all.items() if key in specials]
    
    def CheckForCustomEventSingle(self, author: str, words: list) -> dict:
        if author not in self.custom_events_one:
            return None
        specials = [word.lower() for word in words if word in self.custom_events_one[author].keys()]
        specials.append(' '.join(words).lower())
        return [value for key, value in self.custom_events_one[author].items() if key in words]

    def CheckForCustomEventRegex(self, author: str, words: list) -> dict:
        captured = []
        if author not in self.custom_events_regex.keys():
            return
                
        for key, value in self.custom_events_regex[author].items():
            for word in words:
                catch = re.search(key, word)
                if catch is not None:
                    captured.append(value)

        return captured

    def AddCustomEventGeneral(self, entry: dict) -> bool:
        if entry[PHRASE] in self.custom_events_all:
            return False

        if entry[TYPE] not in ALLOWED_TYPES:
            return False
        
        prepared = {}
        prepared[LINK] = '' if entry.get(LINK) is None else entry[LINK]
        prepared[TYPE] = entry[TYPE]
        prepared[TITLE] = '' if entry.get(TITLE) is None else entry[TITLE]

        self.custom_events_all[entry[PHRASE]] = prepared
        return True

    def AddCustomEventSingle(self, entry: dict) -> bool:
        if self.custom_events_one.get(entry[AUTHOR]) is None:
            self.custom_events_one[entry[AUTHOR]] = {}

        if self.custom_events_one[entry[AUTHOR]].get(entry[PHRASE]) is not None:
            return False
        
        if entry[TYPE] not in ALLOWED_TYPES:
            return False
        
        prepared = {}
        prepared[LINK] = '' if entry.get(LINK) is None else entry[LINK]
        prepared[TYPE] = entry[TYPE]
        prepared[TITLE] = '' if entry.get(TITLE) is None else entry[TITLE]
        
        self.custom_events_one[entry[AUTHOR]][entry[PHRASE]] = prepared
        return True
    
    def AddCustomEventRegex(self, entry: dict) -> bool:
        print('regex')
        if self.custom_events_regex.get(entry[AUTHOR]) is None:
            self.custom_events_regex[entry[AUTHOR]] = {}

        if self.custom_events_regex[entry[AUTHOR]].get(entry[REGEX]) is not None:
            return False

        if entry[TYPE] not in ALLOWED_TYPES:
            return False
        
        prepared = {}
        prepared[LINK] = '' if entry.get(LINK) is None else entry[LINK]
        prepared[TYPE] = entry[TYPE]
        prepared[TITLE] = '' if entry.get(TITLE) is None else entry[TITLE]

        self.custom_events_regex[entry[AUTHOR]][entry[REGEX]] = prepared

        return True

    def RemoveCustomEventGeneral(self, word: list) -> bool:
        if self.custom_events_all.get(word) is None:
            return False
        del self.custom_events_all[word]
        return True
    
    def RemoveCustomEventSingle(self, author: str, word: list) -> bool:
        if self.custom_events_one.get(author) is None:
            return False
        if self.custom_events_one[author].get(word) is None:
            return False

        del self.custom_events_one[author][word]
        return True
    
    def RemoveCustomEventRegex(self, author: str, word: list) -> bool:
        if self.custom_events_regex.get(author) is None:
            return False
        if self.custom_events_regex[author].get(word) is None:
            return False

        del self.custom_events_regex[author][word]
        return True
    
    def UpdateDB(self):
        with open(self.CUSTOM_EVENTS_FOR_ALL, 'w', encoding='UTF-8') as f:
            f.write(str(self.custom_events_all).replace('\'', '\"'))
        with open(self.CUSTOM_EVENTS_FOR_ONE, 'w', encoding='UTF-8') as f:
            f.write(str(self.custom_events_one).replace('\'', '\"'))
        with open(self.CUSTOM_EVENTS_REGEX, 'w', encoding='UTF-8') as f:
            f.write(str(self.custom_events_regex).replace('\'', '\"'))