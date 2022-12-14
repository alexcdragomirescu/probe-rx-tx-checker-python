import re
import os
import sys
import csv
import paramiko
from ssh import SSH

currentPath = os.path.dirname(os.path.abspath(sys.argv[0]))
outputPath = os.path.join(currentPath, "output")

switches = {
    '10.20.11.52': {
        'usr': "admin", 'pw': "password",
        'ports': [
            17, 18, 19, 20, 21, 22, 23, 24, 25, 26
        ]},
    '10.20.11.53': {
        'usr': "admin", 'pw': "password",
        'ports': [
            17, 18, 19, 20, 21, 22, 23, 24, 25, 26
        ]},
    '10.20.11.54': {
        'usr': "admin", 'pw': "password",
        'ports': [
            17, 18, 19, 20, 21, 22, 23, 24, 25
        ]},
    '10.20.11.55': {
        'usr': "admin", 'pw': "password",
        'ports': [
            17, 18, 19, 20, 21, 22, 23, 24, 25
        ]}
}

tblHeader = ["Switch", "Port", "State", "RX Centigrade (uW)", "RX THLD (Min/uW)", "RX THLD (Max/uW)",
             "TX Centigrade (uW)", "TX THLD (Min/uW)", "TX THLD (Max/uW)", "Status"]

thld = {
    'RX': {'min': "31.6", 'max': "794.3"},
    'TX': {'min': "251.2", 'max': "794.3"}
}

pattrns = {'switch':
              [r'^\s+(\d+)\s+(\d+)\s+([a-zA-Z0-9-_]+)\s+(\w+)\s+(\w+)\s+([a-zA-Z0-9-_]+)\s+(.*)', None],
           'sfp':
               [r'([RX|TX]+)\sPower:\s+([-+]\d+\.\d+|[+-]inf)\s+dBm\s+\((\d+\.\d+)[\s+|\w+]+\)\s+(\d+\.\d+)\s+'
               r'\w+\s+(\d+\.\d+)\s+\w+\s+(\d+\.\d+)\s+\w+\s+(\d+\.\d+)\s+\w+$', re.X]
}

complPattrn = {}
for ok, ov in pattrns.items():
    if pattrns[ok][1] is not None:
        complPattrn.update({ok: re.compile(pattrns[ok][0], pattrns[ok][1])})
    else:
        complPattrn.update({ok: re.compile(pattrns[ok][0])})

rows = []
for switch in switches:
    sw = SSH(switch, switches[switch]['usr'], switches[switch]['pw'])
    sw.openTransport()
    sw.openSSH()
    switchOutput = sw.execCmd("switchshow")
    for swLn in switchOutput:
        centigrade = {}
        status = ""
        regSw = re.search(complPattrn['switch'], swLn)
        if regSw is not None:
            if int(regSw.group(2)) in switches[switch]['ports']:
                sfpOutput = sw.execCmd("sfpshow " + regSw.group(2))
                for sfpLn in sfpOutput:
                    regSfp = re.search(complPattrn['sfp'], sfpLn)
                    if regSfp is not None:
                        centigrade.update({regSfp.group(1): regSfp.group(3)})

                if thld['RX']['min'] <= centigrade['RX'] <= thld['RX']['max'] and \
                        thld['TX']['min'] <= centigrade['TX'] <= thld['TX']['max'] and \
                        regSw.group(6) == "Online":
                    status = "OK"
                else:
                    status = "NOK"

                rows.append([switch, regSw.group(2), regSw.group(6), centigrade['RX'], thld['RX']['min'],
                             thld['RX']['max'], centigrade['TX'], thld['TX']['min'], thld['TX']['max'], status])

    rows.append("")
    sw.closeTransport()

with open(os.path.join(outputPath, "SFPChecks.csv"), 'wb') as f:
    writer = csv.writer(f)
    writer.writerow(tblHeader)
    for l in rows:
        writer.writerow(l)


