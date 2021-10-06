'''Provides a number of "web based" utilities eg gate check and marshaling.'''

##from _typeshed import self
import argparse
import sys
import base64
import mimetypes
import apps.ems as ae
import mods.database as md
import mods.log as ml
import ssl

import io

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse,parse_qs

import time
import pprint

html_gate_check_src = open('resources/HTML_gate_check.html','r').read()
html_item_lookup_src = open('resources/HTML_item_lookup.html','r').read()

good_sound = base64.b64encode(open('resources/Bike Horn-SoundBible.com-602544869.wav','rb').read()).decode("utf-8")
bad_sound = base64.b64encode(open('resources/Electronic_Chime-KevanGC-495939803_mono.wav','rb').read()).decode("utf-8")

hostName = "0.0.0.0"
hostPort = 9000
parser = argparse.ArgumentParser(description='Starts the Digital Evacuation Handling Center web services')
parser.add_argument('-a','-auth', type=str, default="db_auth.json", help="relative path to database authentication file", metavar="PATH")
#parser.add_argument('-b','-book', type=str, default="bookmarks.json", help="relative path to EMS screen bookmarks", metavar="PATH")
args = parser.parse_args()

level = "DEBUG"
db = md.DEHCDatabase(config=args.a, level=level, quickstart=False)

# ----------------------------------------------------------------------------

level = "DEBUG"

allowed_files = ['/qr-code-scanner/tce.png',
    '/qr-code-scanner/index.html',
    '/qr-code-scanner/package.json',
    '/qr-code-scanner/qr_packed.js',
    '/qr-code-scanner/qrCodeScanner.js',
    '/qr-code-scanner/styles.css']

#parent_path = path = Path(__file__).parent

logger = ml.get(name="Main", level=level)
logger.debug("Application has started.")
class MyServer(BaseHTTPRequestHandler):
    def gate_check_html_replacer(cleared,evacuee,vessel_id,bgcol):        
        gate_check_html_replace = {}
        if cleared:
            gate_check_html_replace["#bgcol#"] = bgcol
            gate_check_html_replace["#cleared#"] = "Cleared To Board"            
            gate_check_html_replace["#audio#"] = f'data:audio/wav;base64, {good_sound}' 
        else:
            gate_check_html_replace["#bgcol#"] = bgcol
            gate_check_html_replace["#cleared#"] = "Not Permitted : see gate staff"
            gate_check_html_replace["#audio#"] = f'data:audio/wav;base64, {bad_sound}'             
        try:
            photo = db.photo_load_base64(evacuee['_id'])
        except:
            photo = ""
            

        gate_check_html_replace["#photo#"] =   f'<img src="data:image/png;base64, {photo}" alt="Red dot" />'
        gate_check_html_replace["#vessel#"] = "vessel"
        gate_check_html_replace["#display name#"] = evacuee['Display Name']
     
        html_gate_check_src_copy = html_gate_check_src
        for key,value in gate_check_html_replace.items():
            html_gate_check_src_copy = html_gate_check_src_copy.replace(key,value)
        
        return html_gate_check_src_copy               


    def gate_check_clearence(self,container_id,evacuee_id):
        cleared_to_evac = False
        url_data = parse_qs(urlparse(self.path).query)
        #print(url_data['contid'][0])
        evacuees = db.container_children_all(container=url_data['contid'][0], result="DOC")
        #print(evacuees)
        #if url_data['physid'][0] in evacuees:
        #    print("ok")
        
        for evacuee in evacuees:
            print(evacuee['_id'])
            if evacuee['_id'] == url_data['physid'][0]:
                print("evac ok")
                cleared_to_evac = True
                
        
        return cleared_to_evac

    def lookup_item_html(self,item_id):                
        self.send_response(200)            
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        
        item_data = {"Display Name" : "Not Found"} #needs a blank init otherwise it'll throw an error if they aren't in the list
        try:
            item_data = db.item_get(item_id)
        except:
            pass

        try:
            photo = db.photo_load_base64(item_id)
        except:
            photo = ""
        #pprint(evacuee_data)
        #pprint(clearance)
        gate_check_html_replace = {}
        gate_check_html_replace["#photo#"] =   f'<img src="data:image/png;base64, {photo}" alt="Red dot" />'
        gate_check_html_replace["#display name#"] = item_data['Display Name']
        data_pane = "<table>"
        for key,value in item_data.items():
            if (type(value) is list) and (key != "flags"): #flags man, who'se idea was that?
                data_pane += "<table>"
                data_pane += f"<tr><td rowspan=0>{key}</td><td></td></tr>"
                for subitem in value:
                    print(subitem)
                    sub_item_data = db.item_get(subitem)
                    data_pane += f'''<tr><td></td><td><a href="https://10.8.0.50:9000/lookupitem?physid={subitem}">{sub_item_data['Display Name']}</a></td></tr>'''
                data_pane += "</table>"
            else:
                data_pane += f"<tr><td>{key}</td><td>{value}</td></tr>"
        data_pane += "</table>"
        gate_check_html_replace["#data list#"] = data_pane

        html_src_copy = html_item_lookup_src
        for key,value in gate_check_html_replace.items():
            html_src_copy = html_src_copy.replace(key,value)

        
        self.wfile.write(bytes(str(html_src_copy), "utf-8"))


    def gate_check_html(self,container_id,evacuee_id):                
        self.send_response(200)            
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Evacuate?</title></head>", "utf-8"))
        print(self.path)
        

        #items = db.container_children(container=url_data['physid'][0], result="DOC")
        from pprint import pprint
        clearance =  self.gate_check_clearence(container_id,evacuee_id)
        evacuee_data = {"Display Name" : "Not Found"} #needs a blank init otherwise it'll throw an error if they aren't in the list
        try:
            evacuee_data = db.item_get(evacuee_id)
        except:
            pass

        pprint(evacuee_data)
        pprint(clearance)

        if clearance:
            
            self.wfile.write(bytes(self.gate_check_html_replacer(evacuee_data,container_id,"#0aa832"), "utf-8"))
            #self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
            #0aa832
            pass
        else:
            self.wfile.write(bytes(self.gate_check_html_replacer(evacuee_data,container_id,"red"), "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

        

    def do_GET(self):
        path = urlparse(self.path).path
        url_data = parse_qs(urlparse(self.path).query)
        if path == "/gatecheck":
            self.gate_check_html(url_data['contid'][0],url_data['physid'][0])
        elif path == "/lookupitem":
            self.lookup_item_html(url_data['physid'][0])
        elif (path in allowed_files):
            #try:                
                self.send_response(200)            
                self.send_header("Content-type", mimetypes.guess_type(path))
                self.end_headers()   

                self.wfile.write(bytes(open('resources/' + path,'rb').read()))            
            #except:
            #    self.send_response(500)            
            #    self.end_headers()            
                
        else:
            self.send_response(500)            
            self.end_headers()



myServer = HTTPServer((hostName, hostPort), MyServer)
myServer.socket = ssl.wrap_socket (myServer.socket, 
        keyfile="certs/server.pem", 
        certfile='certs/server.pem', server_side=True)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
# ----------------------------------------------------------------------------



#app = ae.EMS(db=db, bookmarks=args.b, level=level, autorun=True)

# ----------------------------------------------------------------------------

logger.debug("Application is ending.")
sys.exit(0)
