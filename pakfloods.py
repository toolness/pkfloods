"""
    usage: pakfloods.py <access-token>

    If you don't provide an access token, this program will display
    this help, followed by a new access token you can use.

    If you provide an access token, this script will print a RSS 2.0 feed
    containing the contents of the messages on the wall of the PKFloods
    Facebook group:

      http://www.facebook.com/PKFloods

    If you have any questions, please contact @toolness on Twitter or
    http://www.facebook.com/toolness.
"""

import urllib2
import sys
import xml.dom.minidom
import StringIO
import datetime

try:
    import json
except ImportError:
    import simplejson as json

# If this app id/secret doesn't work anymore, register a new FB app here:
#
# http://www.facebook.com/developers/createapp.php

app_id = "155761901105095"
app_secret = "a34c2a4c8ef508944eff920c71ff72c6"

profile_url = "https://graph.facebook.com/PKFloods/feed?access_token=%s"
access_token_url = ("https://graph.facebook.com/oauth/access_token?"
                    "type=client_cred&client_id=%s&client_secret=%s")

sample_feed = {
    u'data': [
        {u'created_time': u'2010-08-28T02:23:06+0000',
         u'from': {u'id': u'1', u'name': u'John Doe'},
         u'id': u'147148715311063_151731111519490',
         u'message': u"on behalf of Pakistani people is sincerely THANKFUL to people of Holland (Netherland), and 'public and private broadcasters' for a Nation wide collecting day on 26th August, 2010.\n\nOut of \u20ac16 Million Euro raised -- \u20ac14 Million Euro is raised by people of Holland. Watch [3FM-Holland] 'Wake Up Everybody (Holland for \nPakistan)' song  [ http://www.youtube.com/watch?v=T_brn9zjLDI&translated=1  ]\n\nIt has touched my heart, and the humanity made me cry. Thank you Dutch & Holland.\n- From a Pakistani.",
         u'to': {u'data': [{u'category': u'Nonprofit',
                            u'id': u'147148715311063',
                            u'name': u'"Floods in Pakistan - Join and Help"'}]},
         u'type': u'status',
         u'updated_time': u'2010-08-28T02:23:06+0000'},
        {u'comments': {u'count': 1,
                       u'data': [{u'created_time': u'2010-08-26T18:22:39+0000',
                                  u'from': {u'id': u'2',
                                            u'name': u'Jane Doe'},
                                  u'id': u'147148715311063_151369468222321_253063',
                                  u'message': u'Allah g karam karien..........'}]},
         u'created_time': u'2010-08-26T17:51:29+0000',
         u'from': {u'category': u'Nonprofit',
                   u'id': u'147148715311063',
                   u'name': u'"Floods in Pakistan - Join and Help"'},
         u'icon': u'http://static.ak.fbcdn.net/rsrc.php/z2E5Y/hash/8as8iqdm.gif',
         u'id': u'147148715311063_151369468222321',
         u'likes': 2,
         u'link': u'http://www.facebook.com/photo.php?pid=408774&fbid=151369454888989&id=147148715311063',
         u'message': u'This is the situation some 3 weeks after the floods passed thru Thul. Villages still submerged',
         u'picture': u'http://photos-e.ak.fbcdn.net/hphotos-ak-snc4/hs415.snc4/47785_151369454888989_147148715311063_408774_2342635_s.jpg',
         u'type': u'photo',
         u'updated_time': u'2010-08-26T18:22:39+0000'}     
        ]
    }

def mkelem(dom, element_name, value):
    elem = dom.createElement(element_name)
    elem.appendChild(dom.createTextNode(value))
    return elem

def iso8601_to_datetime(timestamp):
    return datetime.datetime.strptime(timestamp,
                                      "%Y-%m-%dT%H:%M:%S+0000")

def rfc822(dt):
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

def make_rss_feed(json_feed):
    impl = xml.dom.minidom.getDOMImplementation()
    dom = impl.createDocument(None, "rss", None)
    dom.documentElement.setAttribute("version", "2.0")
    channel = dom.createElement("channel")
    channel.appendChild(mkelem(dom, "title", "PKFloods Facebook Feed"))
    channel.appendChild(mkelem(dom, "link", "http://www.facebook.com/PKFloods"))
    channel.appendChild(mkelem(dom, "description",
                               "Feed for wall of PKFloods Facebook group, "
                               "for import into Ushahidi"))
    channel.appendChild(mkelem(dom, "pubDate",
                               rfc822(datetime.datetime.utcnow())))

    for item in json_feed['data']:
        item_node = dom.createElement("item")
        pubdate = iso8601_to_datetime(item['created_time'])
        item_node.appendChild(mkelem(dom, "pubDate",
                                     rfc822(pubdate)))
        item_node.appendChild(mkelem(dom, "title",
                                     "Message from %s at %s" %
                                     (item['from']['name'],
                                      item['created_time'])))
        if 'message' in item:
            item_node.appendChild(mkelem(dom, "description", item['message']))

        if item['type'] == 'photo':
            item_node.appendChild(mkelem(dom, "link", item['picture']))

        item_node.appendChild(mkelem(dom, "guid", item['id']))
        channel.appendChild(item_node)

    dom.documentElement.appendChild(channel)
    buf = StringIO.StringIO()
    dom.writexml(buf, encoding="utf-8")

    # This is nicer for debugging...
    #return dom.toprettyxml(indent="  ", encoding="utf-8")

    return buf.getvalue().encode("utf-8")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "usage: %s <access_token>" % sys.argv[0]
        print
        print "If you don't have an access token, use this:"
        print
        f = urllib2.urlopen(access_token_url % (app_id, app_secret))
        print f.read()
        sys.exit(1)

    access_token = sys.argv[1]

    f = urllib2.urlopen(profile_url % access_token)
    feed = json.loads(f.read())
    print make_rss_feed(feed)
