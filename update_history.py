from pathlib import Path
from urllib.request import Request, urlopen
import csv, io, sys
CFG={
 'l6':('https://www.mk-mode.com/rails/loto/LOTO6_ALL.csv',43,6,1,2138,'data/LOTO6_ALL.csv'),
 'l7':('https://www.mk-mode.com/rails/loto/LOTO7_ALL.csv',37,7,2,695,'data/LOTO7_ALL.csv')}
ANCH={
'l6':{1:([2,8,10,13,27,30],[39]),2:([1,9,16,20,21,43],[5]),20:([7,29,33,35,37,39],[19]),21:([5,7,13,19,38,41],[42]),40:([5,17,25,34,38,39],[2]),101:([21,27,29,30,36,40],[23]),120:([15,18,22,25,36,40],[14])},
'l7':{1:([7,10,12,17,23,28,34],[3,15]),2:([20,24,29,31,33,34,35],[12,32]),3:([2,7,8,11,14,23,31],[5,15]),20:([2,5,13,20,21,23,28],[11,22]),50:([3,4,7,8,15,24,29],[11,16])}}
def decode(b):
 for enc in ('cp932','shift_jis','utf-8-sig','utf-8'):
  try:return b.decode(enc)
  except UnicodeDecodeError:pass
 raise ValueError('encoding')
def ndraw(s):
 d=''.join(c for c in s if c.isdigit());return int(d) if d else None
def run(key):
 url,mx,pick,bonus,minlast,out=CFG[key]
 req=Request(url,headers={'User-Agent':'Mozilla/5.0 LOTO-AI/6.1'})
 raw=urlopen(req,timeout=30).read(); text=decode(raw)
 rows=list(csv.reader(io.StringIO(text)))[1:]; parsed=[]
 for a in rows:
  if len(a)<2+pick+bonus:continue
  d=ndraw(a[0]);
  try: main=sorted(map(int,a[2:2+pick])); bon=list(map(int,a[2+pick:2+pick+bonus]))
  except: continue
  if d is not None:parsed.append((d,main,bon))
 parsed.sort();
 if not parsed:raise ValueError(f'{key}: empty')
 ids=[x[0] for x in parsed]
 if len(ids)!=len(set(ids)) or ids!=list(range(ids[0],ids[-1]+1)):raise ValueError(f'{key}: draw sequence')
 for d,main,bon in parsed:
  if len(main)!=pick or len(set(main))!=pick or any(x<1 or x>mx for x in main):raise ValueError(f'{key}: main {d}')
  if len(bon)!=bonus or len(set(bon))!=bonus or any(x<1 or x>mx or x in main for x in bon):raise ValueError(f'{key}: bonus {d}')
 if parsed[-1][0]<minlast:raise ValueError(f'{key}: stale #{parsed[-1][0]}')
 by={d:(m,b) for d,m,b in parsed}
 for d,(m,b) in ANCH[key].items():
  if d not in by or by[d][0]!=m or sorted(by[d][1])!=sorted(b):raise ValueError(f'{key}: anchor {d}')
 Path(out).write_bytes(raw);print(key, len(parsed), parsed[-1][0], 'PASS')
for k in CFG:run(k)
