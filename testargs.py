import argparse

parser = argparse.ArgumentParser()
parser.add_argument("type", nargs='?', default = 'average')
parser.add_argument("number", type = int, nargs='?', default = 10)
parser.add_argument("direction", nargs='?', default='normal')

args = parser.parse_args()



# parser = argparse.ArgumentParser()
# parser.add_argument('args', '--arg', nargs='+')

print parser.parse_args()

usage = 'Usage: mashup.py ["average" | "highscore" |, "inspections" [<NumberToDisplay> ["reverse"]]]'
if args.type.lower() not in  ['average',  'highscore', 'inspections',]:
    print usage
    exit(0)
    
if args.number <= 0:
    print 'NumberToDisplay must be greater than 0'
    exit(0)   
   
if args.direction.lower() not in  ['normal', 'reverse',]:
    print usage
    exit(0)
    
try:
    print args.type
except NameError:
    print 'No arg type'
        
try:
    print args.number
except NameError:
    print 'No arg number'
    
try:
    print args.direction
except:
    print 'No direction arg'
    
    