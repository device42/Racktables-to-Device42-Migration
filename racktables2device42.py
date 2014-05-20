#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

#############################################################################################################
# v1.0.0 of python script that connects to RackTables DB and migrates data to Device42 appliance using APIs
# Refer to README for further instructions
#############################################################################################################


import sys
import pymysql as sql
import ipaddress
import codecs
import requests
import base64 
import struct
import socket
import re
import json



# ====== MySQL Source (Racktables) ====== #
DB_IP       = 'RT_IP'
DB_NAME  = 'racktables'
DB_USER   = 'RT_USER'
DB_PWD    = 'RT_PWD'
# ====== Log settings  ==================== #
LOGFILE    = 'migration.log'
STDOUT    = 'True'
# ====== Device42 upload settings ========= #
D42_USER   = 'D42_USER'
D42_PWD    = 'D42_PASSWORD'
D42_URL     = 'D42_API_URL'
DRY_RUN     = False



class Logger():
    def __init__(self, logfile, stdout):
        self.logfile  = LOGFILE
        self.stdout = STDOUT

    def writer(self, msg):  
        if LOGFILE and LOGFILE != '':
            with codecs.open(self.logfile, 'a', encoding = 'utf-8') as f:
                f.write(msg.strip()+'\r\n')  # \r\n for notepad
        if self.stdout == 'True':
            try:
                print msg
            except:
                print msg.encode('ascii', 'ignore') + ' # < non-ASCII chars detected! >'

class REST():
    def __init__(self):
        self.password = D42_PWD
        self.username = D42_USER
        self.base_url   = D42_URL
        
    def uploader(self, data, url):
        payload = data
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(self.username + ':' + self.password),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        r = requests.post(url, data=payload, headers=headers, verify=False)
        msg =  unicode(payload)
        logger.writer(msg)
        msg = 'Status code: %s' % str(r.status_code)
        logger.writer(msg)
        msg = str(r.text)
        logger.writer(msg)

    def fetcher(self, url):
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(self.username + ':' + self.password),
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        r = requests.get(url, headers=headers, verify=False)
        msg = 'Status code: %s' % str(r.status_code)
        logger.writer(msg)
        msg = str(r.text)
        logger.writer(msg)
        return r.text
        
    def post_subnet(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/subnets/'
            msg =  '\r\nPosting data to %s ' % url
            logger.writer(msg)
            self.uploader(data, url)

    def post_ip(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/ip/'
            msg =  '\r\nPosting IP data to %s ' % url
            logger.writer(msg)
            self.uploader(data, url)
            
    def post_device(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/device/'
            msg =  '\r\nPosting device data to %s ' % url
            logger.writer(msg)
            self.uploader(data, url)
            
    def post_location(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/buildings/'
            msg =  '\r\nPosting location data to %s ' % url
            logger.writer(msg)
            self.uploader(data, url)
            
    def post_room(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/rooms/'
            msg =  '\r\nPosting room data to %s ' % url
            logger.writer(msg)
            self.uploader(data, url)
            
    def post_rack(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/racks/'
            msg =  '\r\nPosting rack data to %s ' % url
            logger.writer(msg)
            self.uploader(data, url)
    
    def post_pdu(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/pdus/'
            msg =  '\r\nPosting PDU data to %s ' % url
            logger.writer(msg)
            self.uploader(data, url)

    def post_pdu_update(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/pdus/rack/'
            msg =  '\r\nUpdating PDU data to %s ' % url
            logger.writer(msg)
            self.uploader(data, url)
            
    def get_pdu_models(self):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/pdu_models/'
            msg =  '\r\nFetching PDU models from %s ' % url
            logger.writer(msg)
            self.fetcher(url)
        
    def get_racks(self):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/racks/'
            msg =  '\r\nFetching racks from %s ' % url
            logger.writer(msg)
            data = self.fetcher(url)
            return data
            
    def get_devices(self):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/devices/'
            msg =  '\r\nFetching devices from %s ' % url
            logger.writer(msg)
            data = self.fetcher(url)
            return data
            
    def get_racks(self):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/racks/'
            msg =  '\r\nFetching racks from %s ' % url
            logger.writer(msg)
            data = self.fetcher(url)
            return data

    def post_hardware(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/hardwares/'
            msg =  '\r\nAdding hardware data to %s ' % url
            logger.writer(msg)
            self.uploader(data, url)
            
    def post_device2rack(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/device/rack/'
            msg =  '\r\nAdding device to rack at %s ' % url
            logger.writer(msg)
            self.uploader(data, url)
    
        
class DB():
    def __init__(self):
        self.con = None
        self.tables = []
        self.rack_map = {}
        
    def connect(self):
        self.con = sql.connect(host=DB_IP,  port=3306,  db=DB_NAME, user=DB_USER, passwd=DB_PWD)

        
    def convert_ip(self, raw_ip):
        ip = str(ipaddress.ip_address(raw_ip))
        return ip
        
        
    def get_ips(self):
        net = {}
        adrese = []
        if not self.con:
            self.connect()
        with self.con:
            cur = self.con.cursor()
            q = "SELECT * FROM IPv4Address" 
            
            cur.execute(q)
            ips = cur.fetchall()
        
        for line in ips:
            ip_raw, name, comment, reserved = line
            ip = self.convert_ip(ip_raw)
            adrese.append(ip)
          
            net.update({'ipaddress':ip})
            msg =  'IP Address: %s' % ip
            logger.writer(msg)

            net.update({'tag':name})
            msg =  'Label: %s' % name
            logger.writer(msg)
            rest.post_ip(net)
            
        return adrese


    def get_subnets(self):
        subs = {}
        if not self.con:
            self.connect()
        with self.con:
            cur = self.con.cursor()
            q = "SELECT * FROM IPv4Network" 
            cur.execute(q)
            subnets = cur.fetchall()
        for line in subnets:
            id, raw_sub, mask, name, x = line
            subnet = self.convert_ip(raw_sub)
            subs.update({'network':subnet})
            subs.update({'mask_bits':str(mask)})
            subs.update({'name':name})
            rest.post_subnet(subs)


    def get_devices(self):
        if not self.con:
            self.connect()
        with self.con:
            cur = self.con.cursor()
            # get object IDs
            q = 'SELECT id FROM Object'
            cur.execute(q)
            idsx = cur.fetchall()
        ids = [x[0] for x in idsx]
        
        with self.con:
            for id in ids:
                q = """SELECT 
                        Object.name as Description, Object.label as Name, Object.asset_no as Asset, Attribute.name,Dictionary.dict_value as Type
                        FROM Object
                        LEFT JOIN AttributeValue ON Object.id = AttributeValue.object_id 
                        LEFT JOIN Attribute ON AttributeValue.attr_id = Attribute.id
                        LEFT JOIN Dictionary ON Dictionary.dict_key = AttributeValue.uint_value
                        WHERE Object.id = %s AND Object.objtype_id != 2""" % id
                        
            
                cur.execute(q)
                data = cur.fetchall()
                self.process_data(data, id)
    
    
    def process_data(self, data, id):
        for raw in data:
            deviceData = {}
            device2rack = {}
            raw = ['' if not x else x for x in raw]
            notes, name,  asset, type, ver = raw
            if '[[' in ver:
                ver = ver[2:-2]
            if "|" in ver:
                ver = ver.split('|')[0]
            if name: # we are not migrating devices without name
                if type.lower() == 'hw type':
                    if '%GPASS%' in ver:
                        manufacturer, hardware =  ver.split("%GPASS%")
                    elif len(ver.split()) > 1:
                        venmod =  ver.split()
                        manufacturer = venmod[0]
                        hardware = ' '.join(venmod[1:])
                    else:
                        manufacturer = ver
                        hardware = ver
                        
                    deviceData.update({'name':name})
                    deviceData.update({'asset_no':asset})
                    deviceData.update({'hardware':hardware})
                    deviceData.update({'hw_size':3})
                    deviceData.update({'manufacturer':manufacturer})
                    deviceData.update({'notes':notes})
                    # add device to rack:
                    lname = self.get_local_rack_name(id)
                    rack_id = self.rack_map.get(lname)
                    try:
                        floor,  height,  depth,  mount = self.get_hardware_size(id)
                    except:
                        print 'EXCEPTION: ', id
                    if rack_id:
                        device2rack.update({'device':name})
                        device2rack.update({'rack_id':rack_id})
                        device2rack.update({'start_at':floor})

                elif type.lower() == 'sw type':
                    try:
                        os, version = ver.split('%GSKIP%')
                        ver = os
                    except:
                        ver = ver.replace('%GSKIP%', ' ')
                        version = ''
                    deviceData.update({'name':name})
                    deviceData.update({'asset_no':asset})
                    deviceData.update({'os':ver})
                    deviceData.update({'osver':version})
                    deviceData.update({'notes':notes})
                if deviceData:
                    rest.post_device(deviceData)
                if device2rack:
                    rest.post_device2rack(device2rack)
                            
    def get_locations(self):
        if not self.con:
            self.connect()
        with self.con:
            cur = self.con.cursor()
            q = 'SELECT name, comment FROM Object WHERE objtype_id = 1562'
            cur.execute(q)
        data = cur.fetchall()
        for row in data:
            locationData = {}
            raw = ['' if not x else x for x in row]
            name, notes = raw
            locationData.update({'name':name})
            locationData.update({'notes':notes})
            rest.post_location(locationData)
            
            # ROOMS
            # Since Rack tables does not have 'room' attribute, we need to create one in order to relate racks and buildings
            # room name is based on building name
            roomData = {}
            room_name = name + '_room'
            building      = name
            roomData.update({'name':room_name})
            roomData.update({'building':name})
            rest.post_room(roomData)
                
                
                
    def get_racks(self):
        if not self.con:
            self.connect()
        with self.con:
            cur = self.con.cursor()
            q = """select 
                    `O`.`name` AS `name`,`O`.`comment` AS `comment`,`AV_H`.`uint_value` AS `height`,`R`.`name` AS `row_name`,`L`.`name` AS `location_name` 
                    from (((((((`Object` `O` 
                    left join `AttributeValue` `AV_H` on(((`O`.`id` = `AV_H`.`object_id`) and (`AV_H`.`attr_id` = 27)))) 
                    left join `AttributeValue` `AV_S` on(((`O`.`id` = `AV_S`.`object_id`) and (`AV_S`.`attr_id` = 29)))) 
                    left join `RackThumbnail` `RT` on((`O`.`id` = `RT`.`rack_id`))) 
                    left join `EntityLink` `RL` on(((`O`.`id` = `RL`.`child_entity_id`) and (`RL`.`parent_entity_type` = 'row') and (`RL`.`child_entity_type` = 'rack')))) 
                    join `Object` `R` on((`R`.`id` = `RL`.`parent_entity_id`))) 
                    left join `EntityLink` `LL` on(((`R`.`id` = `LL`.`child_entity_id`) and (`LL`.`parent_entity_type` = 'location') and (`LL`.`child_entity_type` = 'row')))) 
                    left join `Object` `L` on((`L`.`id` = `LL`.`parent_entity_id`))) where (`O`.`objtype_id` = 1560)
                """
            cur.execute(q)
        data = cur.fetchall()
        for line in data:
            rackData = {}
            line = ['' if not x else x for x in line]
            name, notes, size, row, building = line
            rackData.update({'name':name})
            rackData.update({'notes':notes})
            rackData.update({'size':size})
            rackData.update({'row':row})
            rackData.update({'building':building})
            # room name is generated based on building name.
            # Plese take a look at the get_locations() for more details
            room_name = building + '_room'
            rackData.update({'room':room_name})
            rest.post_rack(rackData)
    
    def get_pdus(self):
        if not self.con:
            self.connect()
        with self.con:
            cur = self.con.cursor()
            q = """SELECT 
                    Object.id,Object.name as Description, Object.label as Name, Object.asset_no as Asset, 
                    Object.comment as Comment,Dictionary.dict_value as Type, RackSpace.atom as Position, 
                    (SELECT Object.name FROM Object WHERE Object.id = RackSpace.rack_id) as RackID
                    FROM Object
                    LEFT JOIN AttributeValue ON Object.id = AttributeValue.object_id 
                    LEFT JOIN Attribute ON AttributeValue.attr_id = Attribute.id
                    LEFT JOIN Dictionary ON Dictionary.dict_key = AttributeValue.uint_value
                    LEFT JOIN RackSpace ON RackSpace.object_id = Object.id
                    WHERE Object.objtype_id = 2  
                """
            cur.execute(q)
        data = cur.fetchall()
        for line in data:
            pduData = {}
            line = ['' if not x else x for x in line]
            id, name, description, asset, comment, venmodurl, position, rack_name = line
            venmod, url = venmodurl[2:-2].split('|')
            vendor, model =  venmod.split("%GPASS%")
            rack_id, rack_name = self.get_rack_id(id)
            pduData.update({'name':name})
            pduData.update({'notes':comment})
            rest.post_pdu(pduData)

            
            # We have created the PDU, now we are going to update it
            if position.lower() == 'rear':
                orientation = 'back'
            else:
                orientation = 'front'
            pduData.update({'pdu':name})
            #pduData.update({'pdu_id': int(id)})
            # ----------- COMMENT -------------- #
            # GET /api/1.0/pdu_models/ should return all of the PDU models with their names, 
            # which would allow us to create a mapping model_name = pdu_model_id in order to 
            # update PDU's with model names. Currently, GET does not return names so we will skip this for now.
            # rest.get_pdu_models()
            # ----------- COMMENT -------------- #
            pduData.update({'rack_id':rack_id})
            pduData.update({'where':'right'})
            pduData.update({'orientation':orientation})
            pduData.update({'notes':comment})
            rest.post_pdu_update(pduData)
     

    def get_local_rack_name(self, objectid):
        if not self.con:
            self.connect()
        with self.con:
            # get name of the rack containing object_id
            cur = self.con.cursor()
            q = """SELECT 
                Object.name FROM Object WHERE Object.id = ANY(
                SELECT RackSpace.rack_id
                FROM RackSpace
                WHERE RackSpace.object_id = %s
                )
                """ % objectid
            cur.execute(q)
        data = cur.fetchone()
        rack_name = data[0]
        return rack_name
        
            
    def get_rack_id(self, objectid):
        if not self.con:
            self.connect()
        with self.con:
            # get name of the rack containing object_id
            cur = self.con.cursor()
            q = """SELECT 
                Object.name FROM Object WHERE Object.id = ANY(
                SELECT RackSpace.rack_id
                FROM RackSpace
                WHERE RackSpace.object_id = %s
                )
                """ % objectid
            cur.execute(q)
        data = cur.fetchone()
        rack_name = data[0]
        
        # get rack_id based on rack_name
        if data:
            raw = rest.get_racks()
            racks = json.loads(raw)
            for i in range(0, len(racks['racks'])):
                rname =  racks['racks'][i]['name']
                if rack_name.lower() == rname.lower():
                    rack_id = racks['racks'][i]['rack_id']
                    return rack_id, rname
        
        
    def get_patch_panels(self):
        pass
        """
        We cannot migrate patch panels since RackTables DB dos not have  
        any of the info required for successfull migration 
        (i.e. patch_panel_id, mac_id, device_id, device
        """

    def get_device_data(self):
        rest.get_devices()
        
    def get_rack_data(self):
        raw = rest.get_racks()
        racks = json.loads(raw)
        for i in range(0, len(racks['racks'])):
            rname =  racks['racks'][i]['name']
            rack_id = racks['racks'][i]['rack_id']
            self.rack_map.update({rname:rack_id})
        
    
        
    def get_hardware(self):
        if not self.con:
            self.connect()
        with self.con:
            # get hardware items (except PDU's)
            cur = self.con.cursor()
            q = """SELECT 
                    Object.id,Object.name as Description, Object.label as Name, Object.asset_no as Asset,Dictionary.dict_value as Type
                    FROM Object
                    LEFT JOIN AttributeValue ON Object.id = AttributeValue.object_id 
                    LEFT JOIN Attribute ON AttributeValue.attr_id = Attribute.id
                    LEFT JOIN Dictionary ON Dictionary.dict_key = AttributeValue.uint_value
                    WHERE Attribute.id=2 AND Object.objtype_id != 2
                """ 
            cur.execute(q)
        data = cur.fetchall()
        for line in data:
            hwdData = {}
            line = [0 if not x else x for x in line]
            id, description, name, asset, type = line

            if '%GPASS%' in type:
                vendor, model =  type.split("%GPASS%")
            elif len(type.split()) > 1:
                venmod =  type.split()
                vendor = venmod[0]
                model = ' '.join(venmod[1:])
            else:
                vendor = type
                model = type
            self.get_hardware_size(id)
            size = self.get_hardware_size(id)
            if size:
                floor,  height,  depth,  mount = size
                    
                hwdData.update({'notes':description})
                hwdData.update({'type':1})
                hwdData.update({'size':height})
                hwdData.update({'depth':depth})
                hwdData.update({'name':model})
                hwdData.update({'manufacturer':vendor})
                rest.post_hardware(hwdData)
                        
                

    def get_hardware_size(self, id):
        if not self.con:
            self.connect()
        with self.con:
            # get hardware items
            cur = self.con.cursor()
            q = """SELECT unit_no,atom FROM RackSpace WHERE object_id = %s """ % id
            cur.execute(q)
        data = cur.fetchall()
        if data != ():
   
            front    = 0
            interior = 0
            rear     = 0
            floor    = 0
            depth  =  1 # 1 for full depth (default) and 2 for half depth
            mount  = 'front_mount' # can be [front_mount | rear_mount]
            i = 1
            
            for line in data:
                flr, tag  = line
                
                if i == 1:
                    floor = int(flr) -1  # '-1' since RT rack starts at 1 and Device42 starts at 0.
                else: 
                    if int(flr) <  floor:
                        floor = int(flr) -1 
                i += 1
                if tag == 'front':
                    front += 1
                elif tag == 'interior':
                    interior += 1
                elif tag == 'rear':
                    rear += 1
            
            if front and interior and rear: # full depth
                height = front
                return  floor,  height,  depth,  mount
            
            elif front and interior and not rear: #half depth, front mounted
                height = front
                depth = 2
                return floor,  height,  depth,  mount
            
            elif interior and rear and not front: # half depth,  rear mounted
                height = rear
                depth = 2
                mount = 'rear_mount'
                return floor,  height,  depth,  mount
                
            else:
                return None, None, None, None



def main():
    db = DB()
    db.get_subnets()
    db.get_ips()
    db.get_locations() # also creates ROOMS !!!
    db.get_racks()
    db.get_rack_data()
    db.get_hardware()
    db.get_devices()
    db.get_pdus()
  


if __name__ == '__main__':
    logger = Logger(LOGFILE, STDOUT)
    rest = REST()
    main()
    print '\n[!] Done!'
    sys.exit()

