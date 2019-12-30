# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 16:47:54 2019

@author: vinuales
"""

import woffu_helpers as helper

class Woffu_Requests:
    agreements = '/agreements'
    events = '/agreements/[AGREEMENT]/events'
    agreementevent = '/agreements/events/[EVENT]'
    requests = '/requests/updated'
    requests_documents = '/requests/[REQUEST]/documents'
    documents_download = '/documents/[DOCUMENT]/download'
    users = '/users'
    user = '/users/[USER]'
    companies = '/companies/[COMPANY]/locations'
    company = '/companies/company-details/[COMPANY]'
    schedule = '/schedules/[SCHEDULE]'
    jobtitles = '/jobtitles/[JOBTITLE]'
   
class Woffu:
    
    def __init__(self, config_endpoint, config_key, config_proxies=None, config_debug=False):
        self.base = config_endpoint
        self.key = config_key
        self.proxies = config_proxies
        self.debug = config_debug
        self.companies = dict()
           
    def getParamAPI(key, alone=True):
        if alone is True: 
            return ('?api_key=' + key)
        else:
            return ('&api_key=' + key)
    
    def doCurlAPI(self, url, payload):
        import requests
        if (self.debug):
            print("Request: {} \nPayload: {}".format(url,payload))

        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': 'Basic {}'.format(self.key)}
        if (self.debug):
            print(headers)
        response = requests.get(url, data=payload, headers=headers, proxies=self.proxies)

        if response.status_code == 200:
            if (helper.is_json(response.content)):
                return response.json()
            else:
                # Case it is a file, return mime and content
                d = dict()
                d['mime'] = response.headers['Content-Type']
                d['content'] = response.content
                return d
        else:
            print("Request response code: {}".format(response.status_code))
            print("Request response body: {}".format(response.content))
            return None

    def getCompanyName(self, company_id):
        
        if (company_id not in self.companies):
            url = self.base + Woffu_Requests.company
        
            print(">>Company: {}".format(company_id))
            request = url.replace('[COMPANY]',str(company_id))
            response = self.doCurlAPI(request, None)
            
            if response is not None:
                if (self.debug):
                    helper.dump_json(response)
                    
            self.companies[company_id] = response
            
        return self.companies[company_id]["Name"] 
    
    def getCompanies(self, json = None):
        from jsonpath_rw import parse as parse_jsonpath

        if (json is None):
            print(">> Getting Agreements...")
            json = self.getAgreements()
            
        results = parse_jsonpath('$..CompanyId').find(json)
        
        if (self.debug):
            print("Companies: {}".format(results[0].value))
            
        return results[0].value
    
    def getAgreementsId(self, json = None):
        from jsonpath_rw import parse as parse_jsonpath
            
        results = parse_jsonpath('$..AgreementId').find(json)
        
        if (self.debug):
            print("AgreementId: {}".format(results[0].value))
            
        return results[0].value    
    
    def getUsers(self):
        request = self.base + Woffu_Requests.users
        users = self.doCurlAPI(request, None)
        if users is not None:
            if (self.debug):
                helper.dump_json(users)
        return users
    
    def getUser(self, user_id):
        url = self.base + Woffu_Requests.user
        
        print(">>User: {}".format(user_id))
        request = url.replace('[USER]',str(user_id))
        response = self.doCurlAPI(request, None)
        if response is not None:
                if (self.debug):
                    helper.dump_json(response)
        return response 
    
    def getUsersIdList(self, json = None):
        from jsonpath_rw import parse as parse_jsonpath

        if (json is None):
            print(">> Getting Users...")
            json = self.getUsers()
            
        results = parse_jsonpath('$..UserId').find(json)
        
        if (self.debug):
            print("Users: {}".format(results[0].value))
            
        return results[0].value   
    
    def getRequestsDocuments(self, requests_id):
        url = self.base + Woffu_Requests.requests_documents
        
        print(">>Request: {}".format(requests_id))
        request = url.replace('[REQUEST]',str(requests_id))
        response = self.doCurlAPI(request, None)
            
        if response is not None:
                if (self.debug):
                    helper.dump_json(response)
        return response     
    
    def getDocumentDownload(self, document_id):
        url = self.base + Woffu_Requests.documents_download
        
        print(">>Document: {}".format(document_id))
        request = url.replace('[DOCUMENT]',str(document_id))
        response = self.doCurlAPI(request, None)
            
        return response       
    
    def getAgreements(self):
        request = self.base + Woffu_Requests.agreements
        response = self.doCurlAPI(request, None)
        if response is not None:
            if (self.debug):
                helper.dump_json(response)
        return response
    
    def getAgreementEvents(self, agreements):
        url = self.base + Woffu_Requests.events        
        response = dict()
        
        ids = self.getAgreementsId(agreements)
        
        if isinstance(ids, list):
            for agreement in ids:
                print(">>Agreement: {}".format(agreement))
                request = url.replace('[AGREEMENT]',str(agreement))
                agreement_response = self.doCurlAPI(request, None)
                #parsed = json.loads()            
                response.update(agreement = agreement_response)
        else:
            print(">>Agreement: {}".format(ids))
            request = url.replace('[AGREEMENT]',str(ids))
            agreement_response = self.doCurlAPI(request, None)        
            response.update({ids : agreement_response})
            
        if response is not None:
                if (self.debug):
                    helper.dump_json(response)
        return response    
    
    def getAgreementEvent(self, event_id):
        url = self.base + Woffu_Requests.agreementevent
        
        print(">>AgreementEvent: {}".format(event_id))
        request = url.replace('[EVENT]',str(event_id))
        response = self.doCurlAPI(request, None)
            
        if response is not None:
                if (self.debug):
                    helper.dump_json(response)
        return response      
    
    def getRequests(self, params=None):
        request = self.base + Woffu_Requests.requests +'?'
        if params is None:
            request += helper.doDict2QueryString({'fromDate': helper.getDateFrom(1)})
        else:
            request += helper.doDict2QueryString({'fromDate': params})
        response = self.doCurlAPI(request, None)
        if response is not None:
            if (self.debug):
                helper.dump_json(response)
        return response

    def getSchedule(self, schedule_id):
        url = self.base + Woffu_Requests.schedule
        
        print(">>Schedule: {}".format(schedule_id))
        request = url.replace('[SCHEDULE]',str(schedule_id))
        response = self.doCurlAPI(request, None)
            
        if response is not None:
                if (self.debug):
                    helper.dump_json(response)
        return response    

    def getJobTitle(self, jobtitle_id):
        url = self.base + Woffu_Requests.jobtitles
        
        print(">>JobTitle: {}".format(jobtitle_id))
        request = url.replace('[JOBTITLE]',str(jobtitle_id))
        response = self.doCurlAPI(request, None)
            
        if response is not None:
                if (self.debug):
                    helper.dump_json(response)
        return response    
