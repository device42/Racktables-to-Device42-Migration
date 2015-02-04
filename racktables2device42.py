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
# v3.2 of python script that connects to RackTables DB and migrates data to Device42 appliance using APIs
# Refer to README for further instructions
#############################################################################################################


import sys
import pymysql as sql
import codecs
import requests
import base64 
import struct
import socket
import time
import re
import json


try:
    requests.packages.urllib3.disable_warnings() 
except:
    pass


# ====== MySQL Source (Racktables) ====== #
DB_IP       = ''
DB_NAME     = ''
DB_USER     = ''
DB_PWD      = ''
# ====== Log settings ==================== #
LOGFILE     = 'migration.log'
STDOUT      = 'True'
# ====== Device42 upload settings ========= #
D42_USER    = 'admin'
D42_PWD     = 'adm!nd42'
D42_URL     = 'https://'
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
            
            
    def post_building(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/buildings/'
            msg =  '\r\nUploading building data to %s ' % url
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
            
    def get_customers(self):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/customers/'
            msg =  '\r\nFetching customers from %s ' % url
            logger.writer(msg)
            data = self.fetcher(url)
            return data


    def get_buildings(self):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/buildings/'
            msg =  '\r\nFetching buildings from %s ' % url
            logger.writer(msg)
            data = self.fetcher(url)
            return data
            

    def get_rooms(self):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/rooms/'
            msg =  '\r\nFetching rooms from %s ' % url
            logger.writer(msg)
            data = self.fetcher(url)
            return data


    def post_customer(self, data):
        if DRY_RUN == False:
            url = self.base_url+'/api/1.0/customers/'
            msg =  '\r\nAdding customer data to %s ' % url
            logger.writer(msg)
            self.uploader(data, url)
        

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
        self.rack_map = []
        self.building_room_map = {}
        
    def connect(self):
        self.con = sql.connect(host=DB_IP,  port=3306,  db=DB_NAME, user=DB_USER, passwd=DB_PWD)

        
    def convert_ip(self, raw_ip):
        ip = socket.inet_ntoa(struct.pack('!I', raw_ip))
        return ip
        
        
    def get_ips(self):
        
        adrese = []
        if not self.con:
            self.connect()
        with self.con:
            cur = self.con.cursor()
            #q = "SELECT * FROM IPv4Address" 
            q = 'SELECT * FROM IPv4Address WHERE IPv4Address.name != ""'
            cur.execute(q)
            ips = cur.fetchall()
        
        for line in ips:
            net = {}
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


    def get_customers(self):
        self.customers = rest.get_customers()


    def add_customer(self, data):
        raw = data.replace('\n', ' ').split()
        customer = ' '.join(raw)
        rest.post_customer({'name':customer})


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
                q = """Select
                            Object.objtype_id,
                            Object.name as Description, 
                            Object.label as Name, 
                            Object.asset_no as Asset, 
                            Attribute.name as Name,Dictionary.dict_value as Type,
                            Object.comment as Comment,
                            RackSpace.rack_id as RackID,
                            Rack.name as rack_name,
                            Rack.row_name,
                            Rack.location_id,
                            Rack.location_name,
                            Location.parent_name

                            FROM Object
                            LEFT JOIN AttributeValue ON Object.id = AttributeValue.object_id 
                            LEFT JOIN Attribute ON AttributeValue.attr_id = Attribute.id
                            LEFT JOIN Dictionary ON Dictionary.dict_key = AttributeValue.uint_value
                            LEFT JOIN RackSpace ON Object.id = RackSpace.object_id
                            LEFT JOIN Rack ON RackSpace.rack_id = Rack.id
                            LEFT JOIN Location ON Rack.location_id = Location.id
                            WHERE Object.id = %s
                            AND Object.objtype_id not in (1560,1561,1562,50275)""" % id
                        
                cur.execute(q)
                data = cur.fetchall()
                self.process_data(data, id)


 
    def process_data(self, data, id):
        deviceData  = {}
        device2rack = {}
        name        = None
        label       = None
        os          = None
        hardware    = None
        note        = None
        customer    = None
    
 
        for x in data:
            type,  rdesc, rname,  rasset, rattr_name,  rtype, \
            rcomment, rrack_id, rrack_name, rrow_name, \
            rlocation_id, rlocation_name,  rparent_name = x
            
            name    = x[1]
            label   = x[3]
            note    = x[-7]
  
            if 'Operating System' in x:
                os  = x[-8]
                if '%GSKIP%' in os:
                    os = os.replace('%GSKIP%', ' ')
                if '%GPASS%' in os:
                    os = os.replace('%GPASS%', ' ')
            if 'SW type' in x:
                os  = x[-8]
                if '%GSKIP%' in os:
                    os = os.replace('%GSKIP%', ' ')
                if '%GPASS%' in os:
                    os = os.replace('%GPASS%', ' ')
            
            if 'Server Hardware' in x:
                hardware = x[-8]
                if '%GSKIP%' in hardware:
                    hardware = hardware.replace('%GSKIP%', ' ')
                if '%GPASS%' in hardware:
                    hardware = hardware.replace('%GPASS%', ' ')
                if '\t' in hardware:
                    hardware = hardware.replace('\t', ' ')
                    
            if 'HW type' in x:
                hardware = x[-8]
                if '%GSKIP%' in hardware:
                    hardware = hardware.replace('%GSKIP%', ' ')
                if '%GPASS%' in hardware:
                    hardware = hardware.replace('%GPASS%', ' ')
                if '\t' in hardware:
                    hardware = hardware.replace('\t', ' ')
            if 'Customer' in x:
                customer = x[-8]
            if note != None:
                note = note.replace('\n', ' ')
                if '&lt;' in note:
                    note = note.replace('&lt;', '')
                if '&gt;' in note:
                    note = note.replace('&gt;', '')
            
        if name != None: 
            # set device data
            deviceData.update({'name':name})
            #deviceData.update({'hw_size':3})
            if hardware:
                deviceData.update({'hardware':hardware})
            if os:
                deviceData.update({'os':os})
            if note:
                deviceData.update({'notes':note})
            if type == 8:
                deviceData.update({'is_it_switch':'yes'})
            elif type == 1504:
                deviceData.update({'type':'virtual'})
        
            
            # add device to rack:        
            rack_id = None
            if not rparent_name:
                rparent_name = ''
            if not rlocation_name:
                rlocation_name = ''
            if not rrow_name:
                rrow_name = ''
            if not rrack_name:
                rrack_name = ''
            
            rack_string = rparent_name +'::'+ rlocation_name +'::'+ rrow_name +'::'+ rrack_name
            for r in self.rack_map:
                if r.startswith(rack_string+'::'):
                    rack_id = r.split('::')[-1]
            
            if rrack_id: # rrack_id is RT rack id
                # if the device is mounted in RT, we will try to add it to D42 hardwares.
                floor,  height,  depth,  mount = self.get_hardware_size(id)
                if not hardware:
                    hardware ='generic'+str(height)+'U'
                self.add_hardware(height, depth, hardware)
                
            # upload device
            if deviceData:
                if hardware:
                    deviceData.update({'hardware':hardware})
                rest.post_device(deviceData)

            if rack_id: #rack_id is D42 rack id
                device2rack.update({'device':name})
                if hardware:
                    device2rack.update({'hw_model':hardware})
                device2rack.update({'rack_id':rack_id})
                device2rack.update({'start_at':floor})
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
                

    def get_buildings(self):
        if not self.con:
            self.connect()
        with self.con:
            cur = self.con.cursor()
            q = """select 
                    `O`.`id` AS `id`,
                    `O`.`name` AS `name`,
                    `O`.`comment` AS `comment`,
                    `P`.`id` AS `parent_id`,
                    `P`.`name` AS `parent_name` 
                    from (`Object` `O` left join (`Object` `P` join `EntityLink` `EL` 
                    on(((`EL`.`parent_entity_id` = `P`.`id`) 
                    and (`P`.`objtype_id` = 1562) 
                    and (`EL`.`parent_entity_type` = 'location') 
                    and (`EL`.`child_entity_type` = 'location')))) on((`EL`.`child_entity_id` = `O`.`id`))) 
                    where (`O`.`objtype_id` = 1562) and `P`.`id` is  NULL  ;
                    """
            cur.execute(q)
        data = cur.fetchall()
        
        for row in data:
            building={}
            id, name, comment, parent_id, parent_name = row
            building.update({'name':name})
            if comment:
                notes = comment.replace('\n', ' ')
                building.update({'notes':notes})
            rest.post_building(building)
            
            
    def get_rooms(self):
        buildings = json.loads((rest.get_buildings()))['buildings']
        if not self.con:
            self.connect()
        with self.con:
            cur = self.con.cursor()
            q = """select 
                    `O`.`id` AS `id`,
                    `O`.`name` AS `name`,
                    `O`.`comment` AS `comment`,
                    `P`.`id` AS `parent_id`,
                    `P`.`name` AS `parent_name` 
                    from (`Object` `O` left join (`Object` `P` join `EntityLink` `EL` 
                    on(((`EL`.`parent_entity_id` = `P`.`id`) 
                    and (`P`.`objtype_id` = 1562) 
                    and (`EL`.`parent_entity_type` = 'location') 
                    and (`EL`.`child_entity_type` = 'location')))) on((`EL`.`child_entity_id` = `O`.`id`))) 
                    where (`O`.`objtype_id` = 1562) and `P`.`id` is  not NULL  ;
                    """
            cur.execute(q)
        data = cur.fetchall()
        for row in data:
            room = {}
            id, name, comment, parent_id, parent_name = row
            self.building_room_map.update({id:parent_name})
            for building in buildings:
                if building['name'] == parent_name:
                    building_id = building['building_id']
                    room.update({'name':name})
                    room.update({'building_id':building_id})
                    rest.post_room(room)
    
    
    def get_racks(self):
        rack_ids = []
        racks = json.loads(rest.get_racks())['racks']
        for rack in racks:
            rack_ids.append(int(rack['rack_id']))
        
        if not self.con:
            self.connect()
        with self.con:
            cur = self.con.cursor()
            q = """select 
                `O`.`name` AS `name`,`O`.`comment` AS `comment`,
                `AV_H`.`uint_value` AS `height`,`R`.`name` AS `row_name`,
                `L`.`id` AS `location_id`,`L`.`name` AS `location_name` 
                from (((((((`Object` `O` left join `AttributeValue` `AV_H` on(((`O`.`id` = `AV_H`.`object_id`) and (`AV_H`.`attr_id` = 27)))) 
                left join `AttributeValue` `AV_S` on(((`O`.`id` = `AV_S`.`object_id`) and (`AV_S`.`attr_id` = 29)))) 
                left join `RackThumbnail` `RT` on((`O`.`id` = `RT`.`rack_id`))) 
                left join `EntityLink` `RL` on(((`O`.`id` = `RL`.`child_entity_id`) and (`RL`.`parent_entity_type` = 'row') 
                and (`RL`.`child_entity_type` = 'rack')))) join `Object` `R` on((`R`.`id` = `RL`.`parent_entity_id`))) 
                left join `EntityLink` `LL` on(((`R`.`id` = `LL`.`child_entity_id`) and (`LL`.`parent_entity_type` = 'location') 
                and (`LL`.`child_entity_type` = 'row')))) left join `Object` `L` on((`L`.`id` = `LL`.`parent_entity_id`))) 
                where (`O`.`objtype_id` = 1560) 
                """
            cur.execute(q)
        rack_data = cur.fetchall()

        for line in rack_data:
            rack = {}
            rack_name, comment, height, row_name,  room_id,  room_name = line
            building_name = self.building_room_map[room_id]
            if comment:
                notes = comment.replace('\n', ' ')
                notes = notes.replace('\t', ' ')
                rack.update({'notes':notes})
            rack.update({'name':rack_name})
            rack.update({'size':height})
            rack.update({'room':room_name})
            rack.update({'building':building_name})
            #rack.update({'first_number':1})
            rack.update({'row':row_name})
            
            rest.post_rack(rack)
  

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
            try:
                venmod, url = venmodurl[2:-2].split('|')
                vendor, model =  venmod.split("%GPASS%")
            except:
                pass
                
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
        if data: 
            rack_name = data[0]
            return rack_name
        else:
            return None
        
            
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



    def create_rack_map(self):
        raw = rest.get_racks()
        racks = json.loads(raw)
        for rack in racks['racks']:
            building = rack['building']
            room     = rack['room']
            row      = rack['row']
            name     = rack['name']
            rack_id  = rack['rack_id']
            rack_string = building +'::'+ room +'::'+ row +'::'+ name +'::'+ str(rack_id)
            self.rack_map.append(rack_string)

        
    def get_device_to_ip(self):
        if not self.con:
            self.connect()
        with self.con:
            # get hardware items (except PDU's)
            cur = self.con.cursor()
            q = """SELECT 
                IPv4Allocation.ip,IPv4Allocation.name, 
                Object.name as hostname
                FROM `racktables_db`.`IPv4Allocation`
                LEFT JOIN Object ON Object.id = object_id"""
            cur.execute(q)
        data = cur.fetchall()
        for line in data:
            devmap = {}
            rawip, nic_name, hostname = line
            ip = self.convert_ip(rawip)
            devmap.update({'ipaddress':ip})
            devmap.update({'device':hostname})
            if nic_name:
                devmap.update({'tag':nic_name})
            rest.post_ip(devmap)
        
        
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
        else:
            return None, None, None, None

    def add_hardware(self, height, depth, name):
        hwdData = {}
        hwdData.update({'type':1})
        if height:
            hwdData.update({'size':height})
        if depth:
            hwdData.update({'depth':depth})
        if name:
            hwdData.update({'name':name})
            rest.post_hardware(hwdData)



def main():
    db = DB()
    db.get_subnets()
    db.get_ips()
    db.get_buildings()
    db.get_rooms()
    db.get_racks()
    db.create_rack_map()
    db.get_hardware()
    db.get_devices()
    db.get_device_to_ip()
    db.get_pdus()

    
  

if __name__ == '__main__':
    logger = Logger(LOGFILE, STDOUT)
    rest = REST()
    main()
    print '\n[!] Done!'
    sys.exit()


