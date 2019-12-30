# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 18:46:22 2019

@author: vinuales
"""

import woffu_helpers as helper

class Trello_Labelname:
    alta = 'ALTA TRABAJADOR'
    baja = 'BAJA TRABAJADOR'

class Trello:
    
    def __init__(self, tconfig,  config_debug=False, config_proxy=None):
        from trello import TrelloClient
        
        self.client = TrelloClient(api_key=tconfig['tk'], api_secret=tconfig['ts'], proxies=config_proxy)
        #if (config_proxy):
        #    self.client = TrelloClient(api_key=tconfig['tk'], api_secret=tconfig['ts'], proxies=config_proxy)
        #else: 
        #    self.client = TrelloClient(api_key=config_key, api_secret=config_secret)

        self.requests_board_id = tconfig['tboard']
        self.debug = config_debug
        self.board = None
        self.labels = None
        self.motives = tconfig["requests"]
    
    def getAllboards(self):
        all_boards = self.client.list_boards()
        print(">>Requests pending: {}".format(all_boards))
        return all_boards
    
    def getRequestsBoard(self):
        self.board = self.client.get_board(self.requests_board_id)
        lists = self.board.list_lists()        
        pending = lists[0]      
        if (self.debug):
            pending_cards = pending.list_cards()
            print(">>Requests pending: {}".format(pending_cards))
        return pending
    
    def getLabels(self):
        if (self.labels is None):
            self.labels = self.board.get_labels()
            
        if (self.debug):
            print(">>Labels: {}".format(self.labels))
            
        return self.labels
    
    def getLabel(self, name):
        if (self.labels is None):
            self.getLabels()

        label = next((x for x in self.labels if name in x.name), None)
        if (self.debug):
            print(">>Label: {}".format(label))
        return label
        
    def isCardNameCreated(self, query): #board,        
        if (self.debug):
            print("Search Card Name: {}".format(query))
          
        boards = list()
        if (self.board is not None):
            boards.append(self.board.id)
        else: 
            boards.append(self.requests_board)
        cards = self.client.search(query, partial_match=False, models=['cards'], board_ids=boards)
        
        if (self.debug):
            print("Card Name: {}  Matches: {}".format(query,len(cards)))
            print("Results: {}".format(cards))
        
        if (len(cards) > 0):
            for c in cards:
                if (c.name == query):
                    return True
            return False
        else: 
            return False
        
    def addRequests(self, requests, woffu):
        import json
        
        pending = self.getRequestsBoard()
        
        for request in requests:
            print("Request: {} {}".format(request['$id'], request['RequestId']))
            checklist_names = list()
            checklist_states = list()
            checklist_title = 'Datos de la solicitud'
            cardname_prefix = ''
            user_name = ''
            company_id = None
            duedate = None  
            labels = list()
            files = list()
            
            # If request status is not accepted yet, not added to Trello board
            if (request['RequestStatusId'] < 20):
                print("Obviamos request: Request status {}".format(request['RequestStatusId']))
                continue
            
            # User name
            if (request['UserId'] is not None):
                user = woffu.getUser(request['UserId'])
                company_id = user['CompanyId']
                if (user['FirstName'] and user['LastName']):
                    user_name = str(user['FirstName']) + " " + str(user['LastName'])
                    #checklist_names.append("Nombre: " + user_name)
                    #checklist_states.append(True)
                else:          
                    if (user['FirstName'] or user['LastName']):
                        user_name = (str(user['FirstName']) if user['FirstName'] else "Vacío") + " " + (str(request['LastName']) if request['LastName'] else "Vacío")
                        #checklist_names.append("Nombre: " + user_name)
                        #checklist_states.append(False)
                    else: 
                        user_name = 'Nombre trabajador vacío'
                        #checklist_names.append("Nombre: Vacío")
                        #checklist_states.append(False)  
                    
            # User motive
            # Comment: If we only consider selected Motives, then empty is no valid
            if (request['AgreementEventId'] is not None ):
                motive = woffu.getAgreementEvent(request['AgreementEventId'])
                if (motive['Name'] in self.motives):
                    if (motive['Name'] is not None ):
                        checklist_names.append("Motivo: " + str(motive['Name']))
                        checklist_states.append(True)
                        label = self.getLabel(str(motive['Name']))
                        if label is not None:
                            labels.append(label)
                        cardname_prefix = str(motive['Name']) + ': '
                else:
                    continue
#                else:
#                    cardname_prefix = 'Motivo vacío: '
#                    checklist_names.append("Motivo: Vacío")
#                    checklist_states.append(False)
#            else:
#                cardname_prefix = 'Motivo vacío: '
#                checklist_names.append("Motivo: Vacío")
#                checklist_states.append(False)
                    
            # Generate Card Name
            card_name = ("[" + str(request['RequestId']) + "] [" + str(woffu.getCompanyName(company_id)) + "] " + cardname_prefix + user_name)
            if (self.isCardNameCreated(card_name)):
                continue
            
            # Start date
            if (request['StartDate'] is not None ):
                checklist_names.append("Fecha Inicio: " + str(helper.getDateFormat(request['StartDate'])))
                checklist_states.append(True)
            else:
                checklist_names.append("Fecha Inicio: Vacío")
                checklist_states.append(False)
                
            # End date
            if (request['EndDate'] is not None ):
                checklist_names.append("Fecha Fin: " + str(helper.getDateFormat(request['EndDate'])))
                checklist_states.append(True)
            else:
                checklist_names.append("Fecha Fin: Vacío")
                checklist_states.append(False)                
            
            # Comments = Description
            if (request['QuickDescription'] is not None ):
                checklist_names.append("Comentarios: " + str(request['QuickDescription']))
                checklist_states.append(True)
            else:
                checklist_names.append("Comentarios: Vacío")
                checklist_states.append(False)  
                
            # Request document download
            # Warning: Docs is always NULL, even if request has documents
            # => Always checking
            #if (True): #request['Docs'] is not None ):
            documents = woffu.getRequestsDocuments(request['RequestId'])
            if (self.debug):
                print("Documents: {} ".format(documents))
            if (documents['Documents'] is not None ):
                for d in documents['Documents']:
                    file = woffu.getDocumentDownload(d["DocumentId"])
                    file['name'] = d['Name']
                    files.append(file)
                if (self.debug):
                    print("Files: {} ".format(files))
                if (files):
                    fl = list()
                    for f in files:
                        fl.append(f['name'])
                    checklist_names.append("Doc Adjunto: " + ', '.join(fl))
                    checklist_states.append(True)
                else:
                    checklist_names.append("Doc Adjunto: Vacío")
                    checklist_states.append(False)
                    
            
            card = pending.add_card(name=card_name, desc=None, labels=labels, due=duedate, source=None, position=None, assign=None)
            card.add_checklist(checklist_title, checklist_names, checklist_states)
            if (len(files) > 0):
                for f in files:
                    if (int(f['length']) < 10485760):
                        card.attach(name=f['name'], mimeType=f['mime'], file=f['content'])
                    else:
                        card.comment("El fichero " + f['name'] + " es demasiado pesado para adjuntar en Trello :( ")
                    #try:
                    #    card.attach(name=f['name'], mimeType=f['mime'], file=f['content'])
                    #finally:
                    #    
                    #    card.comment("El fichero " + f['name'] + " es demasiado pesado para adjuntar en Trello :(")
                        #return False
        #            card.attach(name=f['name'], mimeType=f['mime'], file=f['content'])
            
            if (self.debug):
                card.comment(str(request))
            
        if (self.debug):
            pending_cards = pending.list_cards()
            print(pending_cards)
        
    def addUserRequests(self, users, woffu = None):
        import json
        import datetime
        
        pending = self.getRequestsBoard()        
        
        for user in users:
            print("User: {} {}".format(user['$id'], user['UserId']))
            labels = list()            
            
            checklist_names = list()
            checklist_states = list()
            checklist_title = ''
            cardname_prefix = ''       
            duedate = None

            if (user['Active'] is False):
                continue
            
            # ID
            if (user['UserId'] is not None ):
                checklist_names.append("ID: " + str(user['UserId']))
                checklist_states.append(True)
            else:
                checklist_names.append("ID: Vacío")
                checklist_states.append(False)     
                
            # User name
            if (user['FirstName'] and user['LastName']):
                checklist_names.append("Nombre: " + str(user['FirstName']) + " " + str(user['LastName']))
                checklist_states.append(True)
            else:          
                if (user['FirstName'] or user['LastName']):
                    checklist_names.append("Nombre: " + (str(user['FirstName']) if user['FirstName'] else "Vacío") + " " + (str(user['LastName']) if user['LastName'] else "Vacío"))
                    checklist_states.append(False)
                else: 
                    checklist_names.append("Nombre: Vacío")
                    checklist_states.append(False)  
                    
            # NIN: DNI
            if (user['NIN'] is not None ):
                checklist_names.append("DNI: " + str(user['NIN']))
                checklist_states.append(True)
            else:
                checklist_names.append("DNI: Vacío")
                checklist_states.append(False)       
                
            # SSN: NAF
            if (user['SSN'] is not None ):
                checklist_names.append("NSS: " + str(user['SSN']))
                checklist_states.append(True)
            else:
                checklist_names.append("NSS: Vacío")
                checklist_states.append(False)
                
            # Birthday
            if (user['Birthday'] is not None ):
                checklist_names.append("Fecha de Nacimiento: " + str(helper.getDateFormat(user['Birthday'])))
                checklist_states.append(True)
            else:
                checklist_names.append("Fecha de Nacimiento: Vacío")
                checklist_states.append(False)
                
            # Start Date
            if (user['EmployeeStartDate'] is not None ):
                checklist_names.append("Fecha Inicio: " + str(helper.getDateFormat(user['EmployeeStartDate'])))
                checklist_states.append(True)
                if (datetime.datetime.strptime(user['EmployeeStartDate'], '%Y-%m-%dT%H:%M:%S.%f') > datetime.datetime.now()):
#                    label = self.getLabel("ALTA TRABAJADOR")
#                    if label is not None:
#                        labels.append(label)
                    duedate = user['EmployeeStartDate']
#                    if (duedate is not None):
#                        checklist_title = "Checklist Alta y Baja Trabajador"
#                        cardname_prefix = "Alta y Baja: "
#                    else:
                    checklist_title = "Checklist Alta Trabajador"
                    cardname_prefix = "Alta usuario: "
                elif (user['EmployeeEndDate'] is None):
                    cardname_prefix = "Alta usuario: "
            else:
                checklist_names.append("Fecha Inicio: Vacío")
                checklist_states.append(False)      
                
            # End date
            if (user['EmployeeEndDate'] is not None ):
                checklist_names.append("Fecha Fin: " + str(helper.getDateFormat(user['EmployeeEndDate'])))
                checklist_states.append(True)
#                label = self.getLabel("BAJA TRABAJADOR")
#                if label is not None:
#                    labels.append(label)
                if (duedate is not None):
                    if (datetime.datetime.strptime(user['EmployeeStartDate'], '%Y-%m-%dT%H:%M:%S.%f') > datetime.datetime.now()):
                        checklist_title = "Checklist Alta y Baja Trabajador"
                        cardname_prefix = "Alta usuario: "
                    else:
                        duedate = user['EmployeeEndDate']                    
                        checklist_title = "Checklist Baja Trabajador"
                        cardname_prefix = "Baja usuario: "
                else:
                    duedate = user['EmployeeEndDate']                    
                    checklist_title = "Checklist Baja Trabajador"
                    cardname_prefix = "Baja usuario: "
#            else:
#                checklist_names.append("Fecha Fin: Vacío")
#                checklist_states.append(False)
                
            # Generate Card name
            card_name = ("[" + str(user['UserId']) + "] [" + str(woffu.getCompanyName(user['CompanyId'])) + "] " + cardname_prefix + str(user['FirstName']) + " " + str(user['LastName']))
            if (self.isCardNameCreated(card_name)):
                continue
            
            if (cardname_prefix is None):
                continue
            
            # Job Title
            if (user['JobTitleId'] is not None ):
                jobtitle = woffu.getJobTitle(user['JobTitleId'])
                if (jobtitle['Name'] is not None ):
                    checklist_names.append("Cargo: " + str(jobtitle['Name']))
                    checklist_states.append(True)
                else:
                    checklist_names.append("Cargo: Vacío")
                    checklist_states.append(False)
            else:
                checklist_names.append("Cargo: Vacío")
                checklist_states.append(False)
                
            # Department
            if (user['DepartmentId'] is not None ):
                department = woffu.getDepartment(user['DepartmentId'])
                if (department['Name'] is not None ):
                    checklist_names.append("Departamento: " + str(department['Name']))
                    checklist_states.append(True)
                else:
                    checklist_names.append("Departamento: Vacío")
                    checklist_states.append(False)
            else:
                checklist_names.append("Departamento: Vacío")
                checklist_states.append(False)
                
            # Office
            if (user['OfficeId'] is not None ):
                office = woffu.getOffice(user['OfficeId'])
                if (office['Name'] is not None ):
                    checklist_names.append("Centro de Trabajo: " + str(office['Name']))
                    checklist_states.append(True)
                else:
                    checklist_names.append("Centro de Trabajo: Vacío")
                    checklist_states.append(False)
            else:
                checklist_names.append("Centro de Trabajo: Vacío")
                checklist_states.append(False)
                
#            # Bank account: avoided
#            if (None is not None ):
#                checklist_names.append("Cuenta Bancaria: " + str(user['JobTitleId']))
#                checklist_states.append(True)
#            else:
#                checklist_names.append("Cuenta Bancaria: Vacío")
#                checklist_states.append(False) 
#                
#            # Address: avoided
#            if (None is not None ):
#                checklist_names.append("Dirección Postal: " + str(user['JobTitleId']))
#                checklist_states.append(True)
#            else:
#                checklist_names.append("Dirección Postal: Vacío")
#                checklist_states.append(False) 

            # E-mail
            if (user['Email'] is not None ):
                checklist_names.append("E-mail: " + str(user['Email']))
                checklist_states.append(True)
            else:
                checklist_names.append("E-mail: Vacío")
                checklist_states.append(False) 

            # Responsable
            if (user['ResponsibleUserId'] is not None ):
                responsible = woffu.getUser(user['ResponsibleUserId'])
                if (responsible['FirstName'] is not None ):
                    checklist_names.append("Responsable: " + str(responsible['FirstName'] + " " + responsible['LastName']))
                    checklist_states.append(True)
                else:
                    checklist_names.append("Responsable: Vacío")
                    checklist_states.append(False)
            else:
                checklist_names.append("Responsable: Vacío")
                checklist_states.append(False)
                
            # Supervisor
            if (user['AuthorizingUserId'] is not None ):
                responsible = woffu.getUser(user['AuthorizingUserId'])
                if (responsible['FirstName'] is not None ):
                    checklist_names.append("Supervisor: " + str(responsible['FirstName'] + " " + responsible['LastName']))
                    checklist_states.append(True)
                else:
                    checklist_names.append("Supervisor: Vacío")
                    checklist_states.append(False)
            else:
                checklist_names.append("Supervisor: Vacío")
                checklist_states.append(False)  
                
            # Attributes
            user_attributes = woffu.getUserAttributes(user['UserId'])
            if (user_attributes):
                #checklist_names.append("Atributos: " + str(responsible['FirstName'] + " " + responsible['LastName']))
                #checklist_states.append(True)
                for s in user_attributes:
                    checklist_names.append(s['Name'] + ": " + str(s['Value'] if s['Value'] is not None else 'Vacío' ))
                    checklist_states.append(True if s['Value'] is not None else False)                
            else:
                checklist_names.append("Atributos (telf, dirección, etc): Vacío")
                checklist_states.append(False)

            # Skills
            user_skills = woffu.getUserSkills(user['UserId'])
            if (user_skills):
                #checklist_names.append("Habilidades: " + str(responsible['FirstName'] + " " + responsible['LastName']))
                #checklist_names.append("Habilidades: Sí que tiene :)")
                #checklist_states.append(True)
                for s in user_skills:
                    checklist_names.append(s['Name'] + ": " + str(s['Value'] if s['Value'] is not None else 'Vacío' ))
                    checklist_states.append(True)
                
            else:
                checklist_names.append("Habilidades: Vacío")
                checklist_states.append(False)                  
                
#            # Salary
#            if (None is not None ):
#                checklist_names.append("Salario: " + str(user['Email']))
#                checklist_states.append(True)
#            else:
#                checklist_names.append("Salario: Vacío")
#                checklist_states.append(False) 
              
            # Schedule
            if ((user['ScheduleId'] is not None) or (user['InheredScheduleId'] is not None) ): #InheredScheduleId?
                schedule_id = (user['ScheduleId'] if user['ScheduleId'] is not None else user['InheredScheduleId'])
                schedule = woffu.getSchedule(schedule_id)
                if (schedule['Name'] is not None ): #'TimeFrame'
                    checklist_names.append("Horario: " + str(schedule['Name']))
                    checklist_states.append(True)
                else:
                    checklist_names.append("Horario: Vacío")
                    checklist_states.append(False) 
            else:
                checklist_names.append("Horario: Vacío")
                checklist_states.append(False) 

                
            user_contract = woffu.getUserContract(user['UserId'])
            # User contract
            if (user_contract):
                checklist_names.append("Tipo Contrato: " + str(user_contract["ContractTypeName"].split("_ContractType_",1)[1]))
                checklist_states.append(True)
                checklist_names.append("Modalidad: " + str(user_contract["ContractModalityName"].split("_ContractModality_",1)[1]))
                checklist_states.append(True)                
            else:
                checklist_names.append("Tipo Contrato: Vacío")
                checklist_states.append(False)
                checklist_names.append("Modalidad: Vacío")
                checklist_states.append(False)                 


            card = pending.add_card(name=card_name, desc=None, labels=labels, due=duedate, source=None, position=None, assign=None)
            card.add_checklist(checklist_title, checklist_names, checklist_states)
            if (self.debug):
                card.comment(str(user))
                if (user_attributes):
                    card.comment(str(user_attributes))
                if (user_skills):
                    card.comment(str(user_skills))
        
        if (self.debug):
            pending_cards = pending.list_cards()
            print(pending_cards)        
        