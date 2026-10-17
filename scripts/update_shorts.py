"""Fetch recent short-form video candidates from YouTube Data API. Requires YOUTUBE_API_KEY."""
import json,os,re,urllib.parse,urllib.request,datetime,pathlib
KEY=os.environ.get('YOUTUBE_API_KEY','')
if not KEY: raise SystemExit('YOUTUBE_API_KEY is not set')
def api(path,**params):
 params['key']=KEY
 url='https://www.googleapis.com/youtube/v3/'+path+'?'+urllib.parse.urlencode(params)
 with urllib.request.urlopen(url,timeout=30) as res:return json.load(res)
channel=api('channels',part='id',forHandle='@u0_um').get('items',[])
if not channel:raise SystemExit('YouTube channel @u0_um was not found')
channel_id=channel[0]['id']
items=[];page=None
for _ in range(3):
 args=dict(part='id',channelId=channel_id,order='date',type='video',videoDuration='short',maxResults=50)
 if page:args['pageToken']=page
 data=api('search',**args)
 items.extend(x['id']['videoId'] for x in data.get('items',[]) if x.get('id',{}).get('videoId'))
 page=data.get('nextPageToken')
 if not page:break
ids=list(dict.fromkeys(items))
def seconds(duration):
 m=re.fullmatch(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',duration)
 return (int(m[1] or 0)*3600+int(m[2] or 0)*60+int(m[3] or 0)) if m else 99999
shorts=[]
for i in range(0,len(ids),50):
 data=api('videos',part='contentDetails,snippet,status',id=','.join(ids[i:i+50]),maxResults=50)
 for v in data.get('items',[]):
  if v.get('status',{}).get('privacyStatus')!='public':continue
  if seconds(v.get('contentDetails',{}).get('duration',''))<=180:shorts.append(v['id'])
path=pathlib.Path(__file__).resolve().parents[1]/'shorts.json'
path.write_text(json.dumps({'videos':shorts,'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'note':'Short-form candidates <=180 seconds; YouTube API does not expose a definitive Shorts flag.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated',len(shorts),'short-form candidates')
