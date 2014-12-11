[Device42](http://www.device42.com/) is a comprehensive data center inventory management and IP Address management software 
that integrates centralized password management, impact charts and applications mappings with IT asset management.

This repository contains sample script to take Inventory information from a RackTables install and send it to Device42 appliance using the REST APIs.

## Assumptions
-----------------------------
    * The script assumes that you are running RackTables  0.20.7 and above
    * This script works with Device42 5.7.3.1396022962 and above

### Requirements
-----------------------------
    * python 2.7.x
    * pymysql (you can install it with sudo pip install pymysql)
    * requests (you can install it with sudo pip install requests or sudo apt-get install python-requests)
	* allow remote connections to RackTables MySQL port 3306

### Usage
-----------------------------
    * add D42 URL/credentials
    * add RackTables DB info/credentials
    * adjust log settings as set on the top
    * Run the script and enjoy!
    * If you have any questions - feel free to reach out to us at support at device42.com
    
### Compatibility
-----------------------------
    * Script runs on Linux and Windows



*Detailed Instructions:*
[Migrating RackTables data to Device42](http://blog.device42.com/2014/05/migrating-racktables-data-to-device42/)
