import json
from pprint import pprint

with open('roi.json') as data_file:    
    data = json.load(data_file)

for list in data:
  print list
