import re
COLORS={'sky','emerald','rose','amber','indigo'}
def validate(x):
    def fail():raise ValueError('課表資料格式不正確。')
    def text(v,n,required=False):
        if not isinstance(v,str) or len(v)>n or (required and not v.strip()):fail()
    def num(v,lo,hi):
        if type(v)!=int or not lo<=v<=hi:fail()
    if not isinstance(x,dict) or x.get('version')!=2:fail()
    s=x.get('settings');cs=x.get('courses')
    if not isinstance(s,dict) or not isinstance(cs,list) or len(cs)>1000:fail()
    text(s.get('title'),100,True);text(s.get('semester'),100)
    ts=s.get('times')
    if not isinstance(ts,list) or len(ts)!=10:fail()
    prev='00:00'
    for p in ts:
        if not isinstance(p,list) or len(p)!=2 or any(not isinstance(t,str) or not re.fullmatch(r'([01]\d|2[0-3]):[0-5]\d',t) for t in p):fail()
        if p[0]>=p[1] or p[0]<prev:fail()
        prev=p[1]
    cats=s.get('categories')
    if not isinstance(cats,dict):fail()
    for k in COLORS:text(cats.get(k),30,True)
    if type(s.get('weekend'))!=bool or s.get('view') not in ['grid','list']:fail()
    ids=set()
    for c in cs:
        if not isinstance(c,dict):fail()
        text(c.get('id'),100,True);text(c.get('name'),100,True)
        if c['id'] in ids:fail()
        ids.add(c['id'])
        for k,n in [('teacher',80),('location',100),('note',1000)]:text(c.get(k),n)
        num(c.get('day'),1,7);num(c.get('startSlot'),1,10);num(c.get('endSlot'),1,10)
        if c['startSlot']>c['endSlot'] or c.get('color') not in COLORS:fail()
    for i,a in enumerate(cs):
        for b in cs[:i]:
            if a['day']==b['day'] and a['startSlot']<=b['endSlot'] and a['endSlot']>=b['startSlot']:raise ValueError('課程衝堂，無法儲存。')
    return x
