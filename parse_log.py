#
#
#   parses a log file for port configs attached to each mac address
#
#

import sqlite3
import os
from os import name

def clearScreen():
    if name == "nt":
        os.system("cls")
    else:
        os.system("clear")

db_name = ""
file = ""
while True:
    clearScreen()
    db_name = raw_input("Please input database name: ")
    clearScreen()
    file = raw_input("Please input name of switch log to add to database: ")
    break

con = sqlite3.connect(db_name+".db")
c = con.cursor()

file = file + ".txt"

mac_data = []
ports = []
always_print = False
i=-5

with open(file) as infile:
    for line in infile:
        if "sh mac address" in line:
            always_print = True
        if "Multicast Entries" in line:
            always_print = False
        if always_print == True:
            mac_data.append(line.split())
            i += 1

c.execute("""CREATE TABLE configs (
            mac_address text,
            port text,
            vlan integer
            )""")
con.commit()

mac_data = mac_data[4:]
print i
for r in mac_data[:-1]:
    ports.append(r[4])
    c.execute("INSERT INTO configs VALUES ('{}', '{}', '{}')".format(r[1], r[4], r[0]))
    
con.commit()

found_port = False
config_list = []
c.execute("alter table configs add column config 'text'")
con.commit()

temp_line = []

for port in ports:
    temp = "interface " + port
    with open(file) as infile:
        for line in infile:
            #print line
            #temp_line.append(line)
            #print temp_line
            templine = line.strip()
            if temp == templine:
                found_port = True
            if line.startswith("!"):
                found_port = False
            if found_port == True:
                if line == "":
                    continue
                else:
                    if(line.startswith("interface " + port)):
                        continue
                    config_list.append(line)
        port_config = "".join(config_list)
    
        c.execute("UPDATE configs SET config = ? WHERE port = ?", (port_config , port)) 
        config_list = []   
        

con.commit()
con.close()