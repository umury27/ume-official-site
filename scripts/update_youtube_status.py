import os,json,re,urllib.request,urllib.parse,datetime,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1]
key=os.environ.get('YOUTUBE_API_KEY')
if not key:
    sys.exit('YOUTUBE_API_KEY is missing. Set a GitHub Actions secret.')
html=(root/'index.html').read_text(encoding='utf-8')
match=re.search(r'<script id="home-schedule-data" type="application/json">(.*?)</script>',html,re.S)
entries=json.loads(match.group(1)) if match else []
ids=[]
for e in entries:
    url=e.get('url','')
    m=re.search(r'(?:[?&]v=|youtu\.be/|youtube\.com/(?:live|shorts|embed)/)([A-Za-z0-9_-]{11})',url)
    if m: ids.append(m.group(1))
ids=list(dict.fromkeys(ids))
statuses={}
for start in range(0,len(ids),50):
    query=urllib.parse.urlencode({'part':'snippet,liveStreamingDetails','id':','.join(ids[start:start+50]),'key':key})
    req=urllib.request.Request('https://www.googleapis.com/youtube/v3/videos?'+query,headers={'User-Agent':'UiUmeHomepage/1.0'})
    with urllib.request.urlopen(req,timeout=25) as response: payload=json.load(response)
    for item in payload.get('items',[]):
        snippet=item.get('snippet',{}); details=item.get('liveStreamingDetails',{});
        status=snippet.get('liveBroadcastContent')
        if status=='live': value='live'
        elif details.get('actualEndTime'): value='completed'
        elif status=='upcoming': value='upcoming'
        elif details.get('actualStartTime'): value='live' # no end yet; verify on next run
        else: value='completed' if details.get('scheduledStartTime') else 'unknown'
        statuses[item['id']]=value
(root/'youtube-status.json').write_text(json.dumps({'statuses':statuses,'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated',len(statuses),'videos')
