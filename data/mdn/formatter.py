import glob
import re
from pathlib import Path
import json
TAG_RE = re.compile(r'<[^>]+>')
index = 0

def validateJSON(jsonData):
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True

def isValidHeader(header):
    if ("seosummary" in header):
        return True
    if ('<a href="/en-US/docs/Web/CSS">' in header):
        return True
    if ('<a href="/en-US/docs/CSS">' in header):
        return True

foldersToTrain = []
foldersToTrain.append('content/files/en-us/web/html/**/*.html')
foldersToTrain.append('content/files/en-us/web/css/**/*.html')

for folder in foldersToTrain:
    for filepath in glob.iglob(folder, recursive=True):
        f = open(filepath, "r")
        for line in f:
            line = line.lower()
            if (isValidHeader(line)):
                line = TAG_RE.sub('', line).strip()
                line = re.sub(r'\{[^()]*\(', '', line)
                line = re.sub(r'\)[^()]*\}', '', line)
                line = line.replace('{{HTMLElement("','<')
                line = line.replace("&lt","<")
                line = line.replace("&gt",">")
                line = line.replace("(","")
                line = line.replace(")", "")
                line = line.replace("<","")
                line = line.replace(">", "")
                line = line.replace('"','')
                line = line.replace(';','')
                jsonstr = '{{"id": "{}-{}", "text": "{}" }}'.format(filepath, index, line)
                text_file = open("json/{}.json".format(index), "w")
                text_file.write(jsonstr)
                text_file.close()
                index += 1
                isValidJson = validateJSON(jsonstr)
                if not isValidJson:
                    print("Given JSON string is invalid:", isValid)
                    print(jsonstr)
                    print(filepath)
                    quit()
print("End")
