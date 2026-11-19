"""Compact selected characteristics from the official bulk 2021 Census Profile files."""
from source import rows, publish
from datetime import date
URL='https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/details/download-telecharger/comp/GetFile.cfm?Lang=E&FILETYPE=CSV&GEONO='
# characteristic ID, user label, unit, source cell, section
INDICATORS = [
 ('1','Residents in 2021','people','count','Population'), ('2','Residents in 2016','people','count','Population'), ('3','Population change, 2016–21','%','count','Population'),
 ('4','Private dwellings','dwellings','count','Housing'),('5','Dwellings occupied by usual residents','dwellings','count','Housing'),
 ('6','Population density','people/km²','count','Population'),('7','Land area','km²','count','Population'),
 ('40','Median age','years','count','Population'),('57','Average household size','people','count','Housing'),
 ('243','Median household income in 2020','CAD','count','Income'),('244','Median after-tax household income in 2020','CAD','count','Income'),
 ('1416','Tenant households','%','rate','Housing'),('1494','Median monthly shelter costs for rented dwellings','CAD','count','Housing'),
 ('386','Knowledge of English and French','%','rate','Language'),('1529','Immigrants in private households','%','rate','Population'),
 ('2008','Bachelor’s degree or higher, age 15+','%','rate','Education')]
PROVINCES={'10':'NL','11':'PE','12':'NS','13':'NB','24':'QC','35':'ON','46':'MB','47':'SK','48':'AB','59':'BC','60':'YT','61':'NT','62':'NU'}
def main():
    wanted={i[0]:(pos,i[3]) for pos,i in enumerate(INDICATORS)}
    places={}; flags={}
    for code in ['001','002']+[f'{n:03}' for n in range(16,29)]:
        stream=rows(code,URL+code,profile=True); head=next(stream)
        at={k:head.index(k) for k in ('DGUID','GEO_LEVEL','GEO_NAME','ALT_GEO_CODE','TNR_SF','TNR_LF','DATA_QUALITY_FLAG','CHARACTERISTIC_ID','C1_COUNT_TOTAL','C10_RATE_TOTAL')}
        for r in stream:
            if len(r)!=len(head):continue
            char=r[at['CHARACTERISTIC_ID']]
            if char not in wanted:continue
            gid=r[at['DGUID']]; name=r[at['GEO_NAME']]
            level=r[at['GEO_LEVEL']]; region=PROVINCES.get(gid[9:11],'') if level in ('Census subdivision','Province','Territory') else ''
            if gid not in places:
                places[gid]=[name,level,region,r[at['TNR_SF']],r[at['TNR_LF']],r[at['DATA_QUALITY_FLAG']],[None]*len(INDICATORS)]
            pos,which=wanted[char]
            col=at['C10_RATE_TOTAL' if which=='rate' else 'C1_COUNT_TOTAL']; raw=r[col].strip(); flag=r[col+1].strip()
            if flag:flags.setdefault(gid,{})[char]=flag
            places[gid][-1][pos]=float(raw) if '.' in raw else int(raw) if raw else None
    if len(places)<5200 or places['2021A00055915001'][-1][0]!=132603 or '2021A00051209034' not in places:raise ValueError('Incomplete census collection')
    publish({'metrics':INDICATORS,'places':places,'flags':flags},dict(start='2016',end='2021',count=len(places)))
if __name__=='__main__':main()
