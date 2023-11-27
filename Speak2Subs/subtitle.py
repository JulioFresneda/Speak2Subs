import copy

class Token:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return self.text

class Subtitle:
    def __init__(self):
        self.tokens = []
        self.text = ""
        for token in self.tokens:
            self.text += token.text

        if(len(self.tokens) > 0):
            self.start = self.tokens[0].start
            self.end = self.tokens[-1].end
        else:
            self.start = 0
            self.end = 0

    def add_token(self, token):
        if(len(self.tokens) == 0):
            self.start = token.start
        self.tokens.append(token)
        self.text += token.text
        self.end = token.end

    def __str__(self):
        return self.text





