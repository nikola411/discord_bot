from Commands.Authors.authors import Authors
import csv

class Curses:
    allowed_words = []
    ALLOWED_WORDS_FILE = './Commands/CurseWords/dict_latin.txt'

    def __init__(self):
        with open(self.ALLOWED_WORDS_FILE, newline='') as csvfile:
            self.allowed_words = [row for row in csv.reader(csvfile, delimiter=',')][0]

    def GetAllowedWords(self):
        return self.allowed_words
    
    def AddAllowedWords(self, words: list):
        for word in words:
            if word not in self.allowed_words:
                self.allowed_words.append(word)

    def RemoveCurseWords(self, words: list) -> None:
        for word in words:
            if word in self.allowed_words:
                self.allowed_words.remove(word)

    def CheckIfCursing(self, words: list) -> list:
        return [word for word in words if word in self.allowed_words]

    def PrepareOutput(self) -> str:
        out = ''
        for i, word in enumerate(self.allowed_words):
            out += '**' + str(i + 1) + '**. ' + word + ' '
        return out

    def UpdateDB(self):
        with open(self.ALLOWED_WORDS_FILE, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.allowed_words)
        