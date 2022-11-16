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
    baseUrl = 'https://backend.fireflink.com'
    pes = s.post(baseUrl+':8081/dashboardexecution/optimize/v1/dashboard/execution/suite/' + suiteid, headers=head, verify=False)
    rus = s.post(baseUrl+':8081/project/optimize/v1/suite/runSetting/' + suiteid, headers=head, verify=False)
    # ruo = json.loads(rus.content)
    out = json.loads(pes.content)
    exid = out['responseObject']['id']

    time.sleep(3)
    sc = 0
    while (sc < 1):
        r1 = s.get(baseUrl+':8081/dashboardexecution/optimize/v1/dashboard/execution/projects/PJT1001' + suiteid, headers=head, verify=False)
        c1 = json.loads(r1.content)
        fr1 = c1['responseObject'][0]['executionStatus']
        # fr1 = c1['responseObject']['_id']
        print('status : ' + fr1 + '......')
        if (fr1 == "Completed" or fr1 == "Cancelled"):
            if fr1 == 'Completed':
                r2 = c1['responseObject'][0]['resultStatus']
                if r2 == 'FAIL':
                    raise Test_Failed
                elif r2 == 'WARNING':
                    print('End Result : ' +'Warning')
                elif r2 == 'Aborted':
                    print('End Result : ' +'Aborted')
                else:
                    print("End Result : " + 'Test Passed')
                sc = 1
            elif (fr1 == 'Cancelled'):
                print("End Result : " + fr1)
                sc = 1
        time.sleep(10)

login(token)
