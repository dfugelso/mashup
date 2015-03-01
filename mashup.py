'''
Mashup.py
'''

# from http://info.kingcounty.gov/health/ehs/foodsafety/inspections/Results.aspx?Output=W&Business_Name=&Business_Address=&Longitude=&Latitude=&City=&Zip_Code=98101&Inspection_Type=All&Inspection_Start=02/01/2013&Inspection_End=02/01/2015&Inspection_Closed_Business=A&Violation_Points=&Violation_Red_Points=&Violation_Descr=&Fuzzy_Search=N&Sort=B


INSPECTION_DOMAIN = "http://info.kingcounty.gov"
INSPECTION_PATH = "/health/ehs/foodsafety/inspections/Results.aspx"

INSPECTION_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'H'
}

import requests
import geocoder
import json
import re
import argparse
import webbrowser
import urllib
from bs4 import BeautifulSoup

def get_inspection_page(**kwargs):
    url = INSPECTION_DOMAIN + INSPECTION_PATH
    params = INSPECTION_PARAMS.copy()
    for key, val in kwargs.items():
        if key in INSPECTION_PARAMS:
            params[key] = val
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.content, resp.encoding
    
def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html.decode('utf-8', 'ignore'))
    return parsed
  
def load_inspection_page(name):
    with open(name, 'r') as fh:
        content = fh.read()
        return content, 'utf-8'
 
def load_inspection_page(name):
    with open(name, 'r') as fh:
        content = fh.read()
        return content, 'utf-8'
        
def restaurant_data_generator(html):
    id_finder = re.compile(r'PR[\d]+~')
    return html.find_all('div', id=id_finder)
 
def has_two_tds(elem):
    is_tr = elem.name == 'tr'
    td_children = elem.find_all('td', recursive=False)
    has_two = len(td_children) == 2
    return is_tr and has_two
 
def clean_data(td):
    return unicode(td.text).strip(" \n:-")
 
def extract_restaurant_metadata(elem):
    restaurant_data_rows = elem.find('tbody').find_all(
        has_two_tds, recursive=False
    )
    rdata = {}
    current_label = ''
    for data_row in restaurant_data_rows:
        key_cell, val_cell = data_row.find_all('td', recursive=False)
        new_label = clean_data(key_cell)
        current_label = new_label if new_label else current_label
        rdata.setdefault(current_label, []).append(clean_data(val_cell))
    return rdata 

def is_inspection_data_row(elem):
    is_tr = elem.name == 'tr'
    if not is_tr:
        return False
    td_children = elem.find_all('td', recursive=False)
    has_four = len(td_children) == 4
    this_text = clean_data(td_children[0]).lower()
    contains_word = 'inspection' in this_text
    does_not_start = not this_text.startswith('inspection')
    return is_tr and has_four and contains_word and does_not_start    
 
def get_score_data(elem):
    inspection_rows = elem.find_all(is_inspection_data_row)
    samples = len(inspection_rows)
    total = high_score = average = 0
    for row in inspection_rows:
        strval = clean_data(row.find_all('td')[2])
        try:
            intval = int(strval)
        except (ValueError, TypeError):
            samples -= 1
        else:
            total += intval
            high_score = intval if intval > high_score else high_score
    if samples:
        average = total/float(samples)
    return {u'Average Score': average, u'High Score': high_score,
            u'Total Inspections': samples}
 
 
def set_color (result, type):
    try:
        if args.type == 'average':
            if result["Average Score"] < 10: return "#00FF00"
            if result["Average Score"] < 25: return "#FFFF00"
            return "FF0000"
        elif args.type == 'highscore':
            if result["High Score"] < 10: return "#00FF00"
            if result["High Score"] < 25: return "#FFFF00"
            return "FF0000"
        else:
            if result["Total Inspections"] < 1: return "#00FF00"
            if result["Total Inspections"] < 5: return "#FFFF00"
            return "FF0000"
    except KeyError:
        return "#0F0F0F"
   
def get_geojson(result, sort_type):
    address = " ".join(result.get('Address', ''))
    if not address:
        return None
    geocoded = geocoder.google(address)
    geojson = geocoded.geojson
    inspection_data = {}
    use_keys = (
        'Business Name', 'Average Score', 'Total Inspections', 'High Score'
    )
    for key, val in result.items():
        if key not in use_keys:
            continue
        if isinstance(val, list):
            val = " ".join(val)
        inspection_data[key] = val
    
    inspection_data['marker-color'] = set_color (result, type)
    geojson['properties'] = inspection_data

    return geojson
 
def result_generator():
    use_params = {
        'Inspection_Start': '2/1/2013',
        'Inspection_End': '2/1/2015',
        'Zip_Code': '98101'
    }
    
    '''
    Get data. Either from source or from saved file.
    '''
    # html, encoding = get_inspection_page(**use_params)
    html, encoding = load_inspection_page('kc.html')
    
    results = []
    parsed = parse_source(html, encoding)
    content_col = parsed.find("td", id="contentcol")
    data_list = restaurant_data_generator(content_col)
    for data_div in data_list:
        metadata = extract_restaurant_metadata(data_div)
        inspection_data = get_score_data(data_div)
        metadata.update(inspection_data)
        results.append (metadata)
    return results
 
if __name__ == '__main__':
    '''
    Get arguments.
    '''
    usage = 'Usage: mashup.py ["average" | "highscore" |, "inspections" [<NumberToDisplay> ["reverse"]]]'
    parser = argparse.ArgumentParser()
    parser.add_argument("type", nargs='?', default = 'average')
    parser.add_argument("number", type = int, nargs='?', default = 10)
    parser.add_argument("direction", nargs='?', default='normal')
    args = parser.parse_args()

    if args.type.lower() not in  ['average',  'highscore', 'inspections',]:
        print usage
        exit(0)
        
    if args.number <= 0:
        print 'NumberToDisplay must be greater than 0'
        exit(0)   
       
    if args.direction.lower() not in  ['normal', 'reverse',]:
        print usage
        exit(0)

    total_result = {'type': 'FeatureCollection', 'features': []}
    results = result_generator()
    

    if args.number > len(results):
        args.number = len(results)
        

    '''
    Sort.
    '''
    if args.type == 'average':
        results = sorted(results, key=lambda data: data['Average Score'], reverse=args.direction.lower() == 'reverse')
    elif args.type == 'highscore':
        results = sorted(results, key=lambda data: data['High Score'], reverse=args.direction.lower() == 'reverse')
    else:
        results = sorted(results, key=lambda data: data['Total Inspections'], reverse=args.direction.lower() == 'reverse')
   
    results = results[:args.number]
    for result in results:
        print result
        geojson = get_geojson(result, args.type)
        total_result['features'].append(geojson)
        
    with open('my_map.json', 'w') as fh:
        json.dump(total_result, fh)
        
    url = "http://geojson.io/#data=data:application/json," + urllib.quote(json.dumps(total_result))
    webbrowser.open(url,new=2)


