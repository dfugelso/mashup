import argparse

parser = argparse.ArgumentParser()
parser.add_argument("type")
parser.add_argument("number")
parser.add_argument("direction")
args = parser.parse_args()

try:
    print args.type
except NameError:
    print 'No arg type'
        
        
try:
    print int(arg.number)
except NameError:
    print 'No arg number'
    
try:
    print args.direction
except:
    print 'No direction arg'
    
    