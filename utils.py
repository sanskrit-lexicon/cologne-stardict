import datetime
import codecs

# Function to return timestamp
def timestamp():
    return datetime.datetime.now()


# Function to read normalized headwords (hwnorm1c.txt) into a dict
# Returns a dict with headword as key and the list of associated headwords as value.
def readhwnorm1c():
    fin = codecs.open('input/hwnorm1c.txt', 'r', 'utf-8')
    lines = fin.readlines()
    output = {}
    for line in lines:
        line = line.strip()
        chunks = line.split(';')
        words = []
        if len(chunks) > 1:
            baseword = chunks[0].split(':')[0]
            for chunk in chunks[1:]:
                worddictsep = chunk.split(':')
                word = worddictsep[0]
                dicts = worddictsep[-1].split(',')
                if not baseword == word:
                    result = [baseword, word]
                    output[word] = (result, dicts)
    return output


def licencetext(dictId):
    fin = codecs.open('../' + dictId + '/pywork/' + dictId + 'header.xml', 'r', 'utf-8')
    data = fin.read()
    fin.close()
    return data

