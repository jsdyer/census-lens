"""Retain the published July 1 age totals for Canadian metropolitan areas and agglomerations."""
import csv
import io
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from public_download import download_bytes

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://www150.statcan.gc.ca/n1/tbl/csv/17100148-eng.zip'
AGES = {'All ages':'total', '0 to 14 years':'children', '65 years and older':'seniors'}

def collect(archive):
    places = {}
    with zipfile.ZipFile(archive) as bundle, bundle.open('17100148.csv') as source:
        reader = csv.DictReader(io.TextIOWrapper(source, encoding='utf-8-sig'))
        for row in reader:
            key = AGES.get(row['Age group'])
            if key is None or row['Gender'] != 'Total - gender': continue
            name = row['GEO']
            if not re.search(r'\((?:CMA|CA)\)',name) or ' part,' in name: continue
            if row['UOM'] != 'Persons' or row['SCALAR_FACTOR'] != 'units': raise ValueError('Unexpected population unit')
            code = row['DGUID']
            if not re.fullmatch('[A-Za-z0-9]+',code): raise ValueError('Unexpected geography identifier')
            place=places.setdefault(code,{'name':name, 'years':{}})
            values=place['years'].setdefault(row['REF_DATE'],{})
            if key in values: raise ValueError('Duplicate age estimate')
            values[key] = int(row['VALUE']) if row['VALUE'] else None
    if len(places)<100: raise ValueError('Incomplete geographic collection')
    years=sorted({y for p in places.values() for y in p['years']})
    for p in places.values():
        for values in p['years'].values():
            if values.keys()!=set(AGES.values()): raise ValueError('Missing age grouping')
            if all(v is not None for v in values.values()) and not 0<=values['children']+values['seniors']<=values['total']:
                raise ValueError('Invalid age totals')
    return {'checked':datetime.now(timezone.utc).date().isoformat(),'start':years[0],'end':years[-1],'count':len(places),'places':places}

def main():
    content=collect(Path(sys.argv[1]) if len(sys.argv)>1 else io.BytesIO(download_bytes(URL,limit=100_000_000,timeout=120)))
    target=ROOT/'web/data/age-estimates.json'
    temp=target.with_suffix('.tmp')
    temp.write_text(json.dumps(content,separators=(',',':'),ensure_ascii=False)+'\n')
    temp.replace(target)
    print(f'{content["count"]} areas, {content["start"]}–{content["end"]}')

if __name__=='__main__': main()
