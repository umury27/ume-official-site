"""Discover upcoming/live streams and recent archives for the public channel."""
import datetime,json,os,pathlib,urllib.parse,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
KEY=os.environ.get('YOUTUBE_API_KEY')
if not KEY: raise SystemExit('Missing YOUTUBE_API_KEY secret')
def api(resource,**params):
    params['key']=KEY
    url='https://www.googleapis.com/youtube/v3/'+resource+'?'+urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'UiUmeHomepage/1.0'}),timeout=30) as r:
        return json.load(r)
channel=api('channels',part='id,contentDetails',forHandle='@u0_um').get('items',[])
if not channel: raise SystemExit('Channel @u0_um not found')
cid=channel[0]['id']; ids=[]
# YouTube's uploads playlist is a low-quota source of recent published broadcasts.
uploads=channel[0]['contentDetails']['relatedPlaylists']['uploads']
page=None
for _ in range(2):
    args=dict(part='contentDetails',playlistId=uploads,maxResults=50)
    if page: args['pageToken']=page
    result=api('playlistItems',**args)
    ids += [x.get('contentDetails',{}).get('videoId') for x in result.get('items',[])]
    page=result.get('nextPageToken')
    if not page: break
# Future scheduled streams may not appear in the uploads playlist yet.
for kind in ('upcoming','live'):
    result=api('search',part='id',channelId=cid,eventType=kind,type='video',maxResults=25)
    ids += [x.get('id',{}).get('videoId') for x in result.get('items',[])]
ids=list(dict.fromkeys(x for x in ids if x))
now=datetime.datetime.now(datetime.timezone.utc)
def dt(value):
    if not value:return None
    try:return datetime.datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError:return None
streams=[];statuses={}
for start in range(0,len(ids),50):
    result=api('videos',part='snippet,liveStreamingDetails,status',id=','.join(ids[start:start+50]),maxResults=50)
    for item in result.get('items',[]):
        snippet=item.get('snippet',{}); detail=item.get('liveStreamingDetails') or {}
        if not detail or item.get('status',{}).get('privacyStatus')!='public':continue
        if snippet.get('channelId')!=cid:continue
        scheduled=dt(detail.get('scheduledStartTime'))
        actual=dt(detail.get('actualStartTime'))
        ended=dt(detail.get('actualEndTime'))
        flag=snippet.get('liveBroadcastContent')
        if ended:state='completed'
        elif flag=='live':state='live'
        elif flag=='upcoming' or (scheduled and scheduled>now and not actual):state='upcoming'
        elif actual and not ended:state='live'
        else:state='completed'
        if state=='completed' and (not actual or (now-actual).days>30):continue
        if state=='upcoming' and scheduled and (scheduled-now).days>60:continue
        vid=item['id'];statuses[vid]=state
        streams.append(dict(id=vid,title=snippet.get('title','配信'),url='https://www.youtube.com/watch?v='+vid,image=(snippet.get('thumbnails',{}).get('high') or snippet.get('thumbnails',{}).get('medium') or {}).get('url',''),status=state,scheduled_start=detail.get('scheduledStartTime'),actual_start=detail.get('actualStartTime'),actual_end=detail.get('actualEndTime')))
rank={'live':0,'upcoming':1,'completed':2}
def order(x):
    value=dt(x.get('scheduled_start') if x['status']=='upcoming' else x.get('actual_start')) or now
    return (rank[x['status']],value.timestamp() if x['status']=='upcoming' else -value.timestamp())
streams.sort(key=order)
selected=[];counts={'live':0,'upcoming':0,'completed':0}
for item in streams:
    state=item['status'];limit=3 if state=='live' else 6 if state=='upcoming' else 6
    if counts[state]<limit:selected.append(item);counts[state]+=1
payload={'streams':selected,'statuses':statuses,'updated_at':now.isoformat()}
(ROOT/'youtube-status.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Discovered',len(selected),'streams',counts)
