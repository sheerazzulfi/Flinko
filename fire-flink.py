from OpenSSL import crypto, SSL

def cert_gen(
    emailAddress="emailAddress",
    commonName="commonName",
    countryName="NT",
    localityName="localityName",
    stateOrProvinceName="stateOrProvinceName",
    organizationName="organizationName",
    organizationUnitName="organizationUnitName",
    serialNumber=0,
    validityStartInSeconds=0,
    validityEndInSeconds=10*365*24*60*60,
    KEY_FILE = "private.key",
    CERT_FILE="selfsigned.crt"):
    #can look at generated file using openssl:
    #openssl x509 -inform pem -in selfsigned.crt -noout -text
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = countryName
    cert.get_subject().ST = stateOrProvinceName
    cert.get_subject().L = localityName
    cert.get_subject().O = organizationName
    cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress
    cert.set_serial_number(serialNumber)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validityEndInSeconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open(CERT_FILE, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(KEY_FILE, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))

cert_gen()




import time
from aifc import Error

import requests
import json
import sys


class Test_Failed(Error):
    pass

token = sys.argv[1]

def login(token):
    s = requests.Session()
    head = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    head["Authorization"] = "Bearer " + token
    suiteid = 'SUITE1002'
    baseUrl = 'https://preprod1.fireflink.com'
    pes = s.post(baseUrl+':8081/dashboardexecution/optimize/v1/dashboard/execution/suite/' + suiteid, headers=head)
    rus = s.post(baseUrl+':8081/project/optimize/v1/suite/runSetting/' + suiteid, headers=head)
    ruo= json.loads(rus.content)
    out = json.loads(pes.content)
    exid = out['responseObject']['id']

    time.sleep(3)
    sc = 0
    while (sc < 1):
        r1 = s.get(baseUrl+':8081/dashboardexecution/optimize/v1/dashboard/execution/' + exid, headers=head)
        c1 = json.loads(r1.content)
        fr1 = c1['responseObject']['executionStatus']
        print('status : ' + fr1 + '......')
        if (fr1 == "Completed" or fr1 == "Terminated"):
            if fr1 == 'Completed':
                r2 = s.get(baseUrl+':8210/optimize/v1/executionResponse/result/' + exid, headers=head)
                c2 = json.loads(r2.content)
                fr2 = c2['responseObject']['suiteStatus']
                if fr2 == 'FAIL':
                    raise Test_Failed
                elif fr2 == 'WARNING':
                    print('End Result : ' +'Warning')
                elif fr2 == 'Aborted':
                    print('End Result : ' +'Aborted')
                else:
                    print("End Result : " + 'Test Passed')
                sc = 1
            elif (fr1 == 'Terminated'):
                print("End Result : " + fr1)
                sc = 1
        time.sleep(10)

login(token)
