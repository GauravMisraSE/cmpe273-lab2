import urllib2
import json
import logging
logging.basicConfig(level=logging.DEBUG)
from spyne import Application, srpc, ServiceBase, \
    Integer, Unicode
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication

class Check(ServiceBase):
    @srpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def checkcrime(lat, lon, radius):
        url ="https://api.spotcrime.com/crimes.json?lat={}&lon={}&radius={}&key=.".format(lat, lon, radius)
        obj= urllib2.urlopen(url)
        data=json.load(obj)
        total_crime=[]
        ctype=[]
        streets=[]
        s1=[]
        s2=[]
        s4=[]
        s3=[]
        time=[]
        eventcount= {"12:01am-3am": 0,
        "3:01am-6am" : 0,
        "6:01am-9am" : 0,
        "9:01am-12noon" : 0,
        "12:01pm-3pm" : 0,
        "3:01pm-6pm" : 0,
        "6:01pm-9pm" : 0,
        "9:01pm-12midnight": 0}
        for i in data['crimes']:
            total_crime.append(i['cdid'])
            streets.append(i['address'])
            ctype.append(i['type'])
            time.append(i['date'])

        x=len(streets)
        for z in range(0,x):
            name=streets[z]
            if ('OF' in name):
                s1.append(name)
            elif ('&' in name):
                s2.append(name)
            else:
                s4.append(name)
        len1=len(s1)
        len2=len(s2)
        for loop in range(0,len1):
            s1[loop]=s1[loop][s1[loop].index('OF')+2:]
        for loop in range(0,len2):
            s3.append(s2[loop][s2[loop].index('&')+1:])
            s3.append(s2[loop][:s2[loop].index('&')])
        mergedlist=s1+s3+s4
        wordfreq = [mergedlist.count(p) for p in mergedlist]
        freqdict= dict(zip(mergedlist,wordfreq))
        aux = [(freqdict[key], key) for key in freqdict]
        aux.sort()
        aux.reverse()
        st1=aux[0]
        st2=aux[1]
        st3=aux[2]
        crimefreq= [ctype.count(p) for p in ctype]
        crimefreqdict= dict(zip(ctype, crimefreq))
        lentime=len(time)
        for loop in data['crimes']:
            time = loop["date"]
            hour = int(time[9:11])
            min = int(time[12:14])
            if time[-2].lower() == "a":
                if ((hour==12 and min > 0) or hour==1 or hour == 2 or (hour==3 and min==0)):
                    eventcount["12:01am-3am"] += 1
                elif (hour==3 or hour==4 or hour == 5 or (hour==6 and min==0)):
                    eventcount["3:01am-6am"] += 1
                elif (hour==6 or hour==7 or hour == 8 or (hour==9 and min==0)):
                    eventcount["6:01am-9am"] += 1
                elif (hour==9 or hour==10 or hour == 11 or (hour==12 and min==0)):
                    eventcount["9:01am-12noon"] += 1
            else:
                if ((hour==12 and min > 0) or hour==1 or hour == 2 or (hour==3 and min==0)):
                    eventcount["12:01pm-3pm"] += 1
                elif (hour==3 or hour==4 or hour == 5 or (hour==6 and min==0)):
                    eventcount["3:01pm-6pm"] += 1
                elif (hour==6 or hour==7 or hour == 8 or (hour==9 and min==0)):
                    eventcount["6:01pm-9pm"] += 1
                elif (hour==9 or hour==10 or hour == 11 or (hour==12 and min==0)):
                    eventcount["9:01pm-12midnight"] += 1
        reply={
               "total_crime": len(total_crime),
                "the_most_dangerous_streets": [st1[1],st2[1],st3[1]],
                "crime_type_count": crimefreqdict,
                "event_time_count": eventcount
              }
        return reply

application = Application([Check],
    tns='spyne.examples.hello',
    in_protocol=HttpRpc(validator='soft'),
    out_protocol=JsonDocument()
)

if __name__ == '__main__':
    # You can use any Wsgi server. Here, we chose
    # Python's built-in wsgi server but you're not
    # supposed to use it in production.
    from wsgiref.simple_server import make_server

    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()
