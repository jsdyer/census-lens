"""Generate static metropolitan age profiles and the results sitemap from the checked edition."""
from html import escape
from xml.etree import ElementTree as ET
import json

BASE='https://coolcode.ca/census-lens/'
TABLE='https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710014801'
PLAN='https://www.statcan.gc.ca/en/census-release-plans'

def write(stage, path, title, intro, body):
    folder=stage/path
    folder.mkdir(parents=True, exist_ok=True)
    (folder/'index.html').write_text(f'''<!doctype html><html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)} | Census Lens</title><meta name="description" content="{escape(intro,quote=True)}"><link rel="canonical" href="{BASE}{path}/"><link rel="stylesheet" href="/census-lens/style.css"></head><body><header><nav><a href="/">CoolCode</a> <a href="/census-lens/">Census Lens</a></nav><div class="heading"><h1>{escape(title)}</h1><p>{escape(intro)}</p></div></header><main>{body}<p><a href="{TABLE}">Statistics Canada, table 17-10-0148-01</a> · <a href="https://www.statcan.gc.ca/en/reference/licence">Statistics Canada Open Licence</a></p></main></body></html>''',encoding='utf-8')
    return BASE+path+'/'

def build_ages(stage):
    edition=json.loads((stage/'data/age-estimates.json').read_text())
    areas=sorted(edition['places'].items(),key=lambda x:x[1]['name'])
    links=[]; urls=[]
    for identifier, place in areas:
        name=place['name']; years=sorted(place['years'],reverse=True)
        usable=next((y for y in years if all(v is not None for v in place['years'][y].values())),None)
        if not usable: continue
        v=place['years'][usable]; ch,sen=v['children'],v['seniors']
        intro=f'On July 1, {usable}, Statistics Canada estimated {ch:,} residents aged 0–14 and {sen:,} aged 65 or older in {name}.'
        rows=[]
        for year in years:
            cells=''.join('<td>'+('Unavailable' if val is None else f'{val:,}')+'</td>' for val in (place['years'][year][k] for k in ['children','seniors','total']))
            rows.append(f'<tr><th scope="row">{year}</th>{cells}</tr>')
        path='ages/'+identifier.lower()
        larger='the two groups were equal in size' if ch==sen else f'there were {abs(ch-sen):,} more '+('children than seniors' if ch>sen else 'seniors than children')
        content=f'''<p>In {usable}, {larger}. This comparison uses residents across the whole census metropolitan area (CMA) or census agglomeration (CA) on 2021 boundaries. The city municipality may cover a smaller area.</p><p><a href="../">Compare other Canadian areas</a> · <a href="../../">Compare two 2021 Census community profiles</a></p><h2>Age estimates by year</h2><div style="overflow-x:auto"><table><thead><tr><th>July 1</th><th>Age 0–14</th><th>Age 65+</th><th>All ages</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><p>Annual estimates can change with revisions. The publisher lists the status of each vintage in the table notes. Source retrieved {edition["checked"]}.</p>'''
        urls.append(write(stage,path,'Children and seniors in '+name,intro,content))
        links.append(f'<li><a href="{identifier.lower()}/">{escape(name)}</a></li>')
    intro=f'Compare the number of children aged 0–14 with adults aged 65 or older in {len(links)} Canadian metropolitan areas and agglomerations, from {edition["start"]} to {edition["end"]}.'
    urls.append(write(stage,'ages','Where do children outnumber seniors in Canada?',intro,'<p>Choose the metropolitan area or agglomeration that includes your community. Each page shows counts on July 1, using consistent 2021 boundaries.</p><ul>'+''.join(links)+'</ul>'))
    root=ET.Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for url in sorted(urls): ET.SubElement(ET.SubElement(root,'url'),'loc').text=url
    ET.ElementTree(root).write(stage/'sitemap.xml',encoding='utf-8',xml_declaration=True)
