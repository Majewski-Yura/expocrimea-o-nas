# coding: utf-8
import concurrent.futures as cf,subprocess,json,re,html,hashlib,sys,time
from pathlib import Path
from urllib.parse import urlsplit,unquote,urljoin
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parent.parent
CACHE=ROOT.parent.parent/'Исходники новостей'/'api';CACHE.mkdir(parents=True,exist_ok=True)
ORIG=ROOT.parent.parent/'Исходники новостей';ORIG.mkdir(exist_ok=True)
OUT=ROOT/'assets/media/news/archive';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tools'));from scrape_news import clean,text,MONTHS

def get_page(i):
 p=CACHE/f'{i}.json'
 headers=CACHE/f'{i}.headers'
 if not p.exists():
  subprocess.run(['curl','-fsSL','--retry','2','--max-time','60','-D',str(headers),f'https://expocrimea.com/wp-json/wp/v2/news?per_page=100&page={i}&_embed','-o',str(p)],check=True)
 data=json.loads(p.read_text());assert isinstance(data,list);return data
first=get_page(1)
header_text=(CACHE/'1.headers').read_text() if (CACHE/'1.headers').exists() else ''
match=re.search(r'X-WP-TotalPages:\s*(\d+)',header_text,re.I)
total_pages=int(match[1]) if match else 8
with cf.ThreadPoolExecutor(max_workers=4) as ex: posts=first+sum(list(ex.map(get_page,range(2,total_pages+1))),[])
posts={x['id']:x for x in posts};print('Posts:',len(posts),flush=True)
articles=[];urls=set()
for post in posts.values():
 raw=post['content']['rendered']
 raw=re.sub(r'<iframe[^>]+src=[\"\x27]([^\"\x27]+)[\"\x27][^>]*>.*?</iframe>',lambda m:'<p><a href="'+html.escape(m[1])+'">Смотреть видео</a></p>',raw,flags=re.S|re.I)
 body=clean(raw)
 featured=post.get('_embedded',{}).get('wp:featuredmedia',[])
 image=featured[0].get('source_url','') if featured and isinstance(featured[0],dict) else ''
 if not image:
  m=re.search(r'<img[^>]+src="([^"]+)"',body);image=html.unescape(m[1]) if m else ''
 tags=[t['name'] for group in post.get('_embedded',{}).get('wp:term',[]) for t in group if isinstance(t,dict) and 'name' in t]
 day=post['date'][:10];y,mo,d=map(int,day.split('-'))
 lead=next((text(p) for p in re.findall(r'<p>(.*?)</p>',body,re.S) if len(text(p))>60),text(body)[:400])
 n={'slug':unquote(post['slug']),'title':text(post['title']['rendered']),'date':day,'date_h':f'{d} {MONTHS[mo-1]} {y}','tags':tags,'image':image,'thumb':image,'lead':lead,'body':body,'source':post['link']}
 articles.append(n)
 if image:urls.add(html.unescape(image))
 urls.update(html.unescape(x) for x in re.findall(r'<img[^>]+src="([^"]+)"',body))
urls={urljoin('https://expocrimea.com/',u) for u in urls if not u.startswith('data:')}
print('Images:',len(urls),flush=True)

def download(url):
 key=hashlib.sha256(url.encode()).hexdigest()[:20]
 suffix=Path(unquote(urlsplit(url).path)).suffix.lower();suffix=suffix if suffix in ['.jpg','.jpeg','.png','.gif','.webp','.svg'] else '.img'
 original=ORIG/(key+suffix);target=OUT/(key+'.jpg')
 try:
  if not original.exists():subprocess.run(['curl','-fsSL','--retry','2','--max-time','45',url,'-o',str(original)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  if suffix=='.svg':
   target=OUT/(key+'.svg');target.write_bytes(original.read_bytes())
  else:
   with Image.open(original) as im:
    if getattr(im,'is_animated',False):target=OUT/(key+suffix);target.write_bytes(original.read_bytes())
    else:
     im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((1440,1440),Image.Resampling.LANCZOS);im.save(target,quality=86,optimize=True)
  return url,'assets/media/news/archive/'+target.name,None
 except Exception as e:
  if original.exists() and original.stat().st_size==0:original.unlink()
  return url,None,str(e)
results=[]
with cf.ThreadPoolExecutor(max_workers=6) as ex:
 for i,r in enumerate(ex.map(download,sorted(urls)),1):
  results.append(r)
  if i%50==0:print('Images processed',i,'/',len(urls),flush=True)
lookup={u:p for u,p,e in results if p};failed=[{'url':u,'error':e} for u,p,e in results if e]
for n in articles:
 old=n['image'];n['image']=lookup.get(urljoin('https://expocrimea.com/',html.unescape(old)),'');n['thumb']=n['image']
 def local_image(m):
  src=html.unescape(m[1]);local=lookup.get(urljoin('https://expocrimea.com/',src))
  return '<img src="../'+local+'" alt="" loading="lazy">' if local else ''
 n['body']=re.sub(r'<img[^>]+src="([^"]+)"[^>]*>',local_image,n['body'])
slugs={n['slug'] for n in articles}
for item in articles:
 item['body']=re.sub(r'href="https?://(?:www\.)?expocrimea\.com/news/([^/"?#]+)/?"',lambda m:'href="'+m[1]+'.html"' if m[1] in slugs else m[0],item['body'])
 if not re.sub('<[^>]+>','',item['body']).strip() and not item['image']:
  item['body']='<p>На старом сайте эта публикация доступна без основного текста и фотографии.</p>'
articles.sort(key=lambda n:(n['date'],n['slug']),reverse=True)
(ROOT/'data/news.json').write_text(json.dumps(articles,ensure_ascii=False,indent=1))
report={'news':len(articles),'range':[articles[-1]['date'],articles[0]['date']],'images':len(lookup),'failed':failed,'without_image':[n['slug'] for n in articles if not n['image']]}
(ROOT/'data/news-import-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
(ORIG/'sources.json').write_text(json.dumps({u:Path(p).name for u,p,e in results if p},ensure_ascii=False,indent=1))
print('Imported:',len(articles),'images:',len(lookup),'failed:',len(failed),flush=True)
