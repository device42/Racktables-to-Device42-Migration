[Device42](http://www.device42.com/) is a comprehensive data center inventory management and IP Address management software
that integrates centralized password management, impact charts and applications mappings with IT asset management.

This repository contains sample script to take Inventory information from a RackTables installation and send it to Device42 appliance using the REST APIs.
## Version
-----------------------------
    * 5.3

## Assumptions
-----------------------------
    * The script assumes that you are running RackTables 0.20.7 and above
    * This script works with Device42 10.5.0 and above

### Requirements
-----------------------------
    * python 2.7.x
    * pymysql (you can install it on ubuntu with `sudo pip install pymysql`, other similar commands for other OS)
    * requests (you can install it with sudo pip install requests or sudo apt-get install python-requests)
	* allow remote connections to RackTables MySQL port 3306

### Usage
-----------------------------

    * copy conf.sample to conf
    * in conf add D42 URL/credentials
```
# ====== Device42 upload settings ========= #
D42_USER = 'device42 user'
D42_PWD = 'device42 password'
D42_URL = 'https:// device42 server IP address'
```

    * add RackTables DB info/credentials
```
# ====== MySQL Source (Racktables) ====== #
DB_IP = 'racktables server IP'
DB_PORT = '3306'
DB_NAME = 'racktables database name'
DB_USER = 'racktables user'
DB_PWD = 'racktables password'
```
	* adjust log settings
```
# ====== Log settings ==================== #
LOGFILE = 'migration.log'
STDOUT = True # print to STDOUT
DEBUG = True # write debug log
DEBUG_LOG = 'debug.log'
```
	* other setings
```
# ====== Other settings ========= #
CHILD_AS_BUILDING = True
ROW_AS_ROOM = True
PDU_MOUNT = 'left'
PDU_ORIENTATION = 'front'
```

- CHILD_AS_BUILDING: Racktables uses a concept of location and sub-location (container within container). Device42 uses a concept of Buildings and Rooms. In case CHILD_AS_BUILDING is set to True, sub-locations will be uploaded as Rooms to Device42. Otherwise, sub-locations will be uploaded as Buildings.
- ROW_AS_ROOM: Racktables uses a concept of Rows as subordinate to locations (or sub-locations). Device42 uses concept of Rooms. In case ROW_AS_ROOM is set to true, Rows will be uploaded as Rooms to Device42. Otherwise, rows will be uploaded as rows.
**Note: **Rooms are required because racks are mounted to rooms, not to buildings! So, please set at least one of previous settings to True.
- PDU_MOUNT: Can be one of: 'left', 'right', 'above', 'below'. Used for Zero-U PDU migration. Default is 'left'.
- PDU_ORIENTATION: Can be 'front' or  'back'. Used for Zero-U PDU migration. Default is 'front'.

Run the script and enjoy! (```python racktables2device42.py```)
If you have any questions - feel free to reach out to us at support at device42.com



### Compatibility
-----------------------------
    * Script runs on Linux and Windows


### Gotchas
-----------------------------
    * Devices without names are not migrated
    * PDU migration is still a work in progress
    * Order of function calls in main() function is important. Do not change it!
      For example: subnets must be migrated before IP addresses in order for addresses to join appropriate subnets.
    * If patch panels have more than 1 port type, we will create modular patch panel in D42
    * For following, we will truncate data from your racktables instance:
	    * Maximum Port type name length = 12
	    * Maximum Hardware name length = 48
	    * Maximum Pdu type name length = 64
