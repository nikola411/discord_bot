import json

class Authors:
    history = {}
    doNotScan = ['Psovkobrojac BOT#9107', 'Psovkobrojac BOT']
    AUTHORS_HISTORY_FILE = './Commands/Authors/authors_history.json'


    def __init__(self):
        with open(self.AUTHORS_HISTORY_FILE, encoding='UTF-8') as f:
            self.history = json.load(f)

    def GetHistory(self) -> dict:
        return self.history

    def RegisterAuthorCursing(self, author: str, words: list) -> None:
        if len(words) == 0:
            return
        if author in self.doNotScan:
            return
        
        if self.history.get(author) is None:
            self.history[author] = {}

        for word in words:   
            if self.history[author].get(word) is None:
                self.history[author][word] = 1
            else:
                self.history[author][word] += 1
        
    def DeleteFromHistory(self, words: list) -> None:
        for word in words:
            for author in self.history.keys():
                if word in self.history[author]:
                    del self.history[author][word]

    def FormatOutputString(self) -> str:
        out = '**Ko najvise psuje ovde? **\n'
        curse_cnt = []
        for key in self.history.keys():
            author = self.history[key]
            data = ''
            data += 'Autor: **' + key + '**' + '\n['
            sum = 0
            for curse in author:
                data += '  ' + curse  + ' : '
                data += str(author[curse])
                sum += author[curse]

            data += ' ]\n'
            data += 'Ukupno psovki: **' + str(sum) + '**\n\n'
            data = '{:30}'.format(data)
            curse_cnt.append((key, sum))
            out += data

        # sorted_cnt = sorted(curse_cnt, key=lambda autor: autor[1], reverse=True)
        # # out += '\nPobednik: ' + str(sorted_cnt[0][0])
        return out
    
    def UpdateDB(self):
        with open(self.AUTHORS_HISTORY_FILE, 'w', encoding='UTF-8') as f:
            f.write(str(self.history).replace('\'', '\"'))