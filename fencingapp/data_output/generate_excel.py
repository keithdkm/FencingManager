'''
Reads data from the Tournament data and event data  from fencing time website and creates a 
spreadsheet of all the competitors with a pivot table breaking them down by rating.
Leaves a spreadsheet with the data in the Fencing folder 
'''
#  Prgram notes - Ensure that excel is closed first
#               - if the code crashes, reporting Attribute not found in gencache, the delete the gen_py
#                 directory in %username%/Appdata/Local/temp
#               - if problems persist reinstall pywin32

#  Needed improvements - Remove the requirement to have excel not running. See the DispatchEx method
#                      - integrate with backend db. Pull tournaments, events, entrants from there
#                      - add fencers names to pivot table
#                      - add national ranking to fencer data
#                      - update spreadsheet with pool data from fencingtimelive after pools are published

import pandas as pd
import requests
from re import findall
from lxml import html
from datetime import datetime
import win32com.client as win32  # enables script communication to excel. use 'yconda install pywin32'
                                 # https://github.com/mhammond/pywin32
                                 # http://docs.activestate.com/activepython/2.6/pywin32/PyWin32.HTML
                                 # http://docs.activestate.com/activepython/2.4/pywin32/html/com/win32.constantsom/HTML/QuickStartClientCom.html#StaticDispatch
import numpy as np
import pathlib
import os
import sys
import time
from itertools import count

# 1.[ ] rewrite to parse returned web data with beautifulSoup
class cd: 
    """Context manager for changing the current working directory"""
    """ and then restoring the original when complete"""
    ## I'd like to rewrite this to use pathlib
    def __init__(self, newPath):                   
        self.newPath = os.path.expanduser(newPath)
    
    
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    
    def __exit__(self, etype, value, traceback):
                    
        os.chdir(self.savedPath)

##################################################
class Fencer():
    
    def __init__(self, l_name,f_name,):
        pass
####################################################
class Event():
    
    def __init__(self,name,event_time,link,):  #initializes with name of event, date/time of event and downloads entrants from usfa
        self.name = name
        self.short_name = name.split(" ")[0]
        self.link = link
        self.event_date = event_time
        self.entrants = Event.get_entrants(self)  # dataframe with a list of event entrants
    
    
    # enhancement: check fencingtimelive first and if event is there download from there. 
    # Then check USFA and record differnce in a scratch list
    # if fencingtimelive doesn't have event then populate with USFA data only
    # on competition day, coulde generate another scratch list

    
    
    def get_entrants(self):  #retrieves  data from  USFA website and formats into a pandas dataframe
        PAT = r'([a-zA-Z\- ]+), *([a-zA-Z\-]+ [a-zA-Z\-/(/)]* [a-zA-Z\-/(/)]*) *([A-EU])(\d\d)* +([\S]+) *([a-zA-Z\.\-\(\) ]+)* */* *([a-zA-Z\.\-\(\) ]+)*'
                   
        try:
            html_ = requests.get(self.link,verify=False)
            html_.raise_for_status()
        except requests.exceptions.HTTPError as e:
              print (e)
              print("no entrants found for event")
              sys.exit(1)

        raw_ =  pd.read_html(html_.json()['entrants_table'])[0].iloc[:,1:3]
        # This should be rewritten using beautifulSoup   
        basic = (pd.DataFrame((findall(PAT,a[1][0])[0] for a in raw_.iterrows()), #split fencer data into columns
                              columns = ['Last Name',
                                         'First Name', 
                                         'Rating',
                                         'Year', 
                                         'Country', 
                                         'Club', 
                                         'Division'])
                     .assign(
                             Year = lambda x: pd.to_numeric(x.Year,downcast = 'integer'),
                             PoolRound= " ",  # add additional columns for pool data
                             TF = " ",
                             TR	= " ",
                             WinLoss= " "
                            )

                    )
        return(basic)

   
    def get_date_time(self):
        pass
            
    def __getitem__(self,i):
        return self.entrants.iloc[i]
        
    def __len__(self):
        return len(self.entrants.index)
    
    def __str__(self):
        return(f'The {self.name} has {len(self.entrants.index)} competitors')
        

    def __repr__(self):            
        return(f'{self.name} with {len(self.entrants.index)} competitors on '
               f'{self.event_date.strftime("%A, %B %#d" + self.day_suffix() +" at %#I:%M%p")}') 


     
    def day_suffix(self):  #calculates suffix for date
        if 4 <= self.event_date.day <= 20 or 24 <= self.event_date.day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][self.event_date.day % 10 - 1]
        return suffix
    
    
    def write_To_Excel(self,writer,sheet_name):           
                
        return self.entrants.to_excel(writer,sheet_name)
#################################################### 
class Tournament():   
                   
    def __init__(self,name):
        # Future - automatically pick out the events Naomi is fencing in. Find //*[@id="events-by-day"] usinng this XPatch query and this one to find registered event /html/body/div[2]/div[1]/div/div/div/div/div[1]/div[4]/div/div[2]/div[2]/div[8]/div[6]/div/span[1]/span[2]
        #      /html/body/div[2]/div[1]/div/div/div/div/div[1]/div[4]/div/div[2]/div[2]/div[8]/div[6]/span[3]/a
        JWF  = Event("Junior Womens's Foil", datetime(2019,11,10,8,0),
                     'https://member.usafencing.org/details/tournaments/4158/entrants?event_id=28837&_=1573346339192')
        CWF  = Event("Cadet Women's Foil" , datetime(2019,11,11,8,0),
                     'https://member.usafencing.org/details/tournaments/4158/entrants?event_id=28844&_=1573346339193')
        # DIIWF = Event("DivII Women's Foil", datetime(2019,10,19,8,0),
        #              'https://member.usafencing.org/details/tournaments/3877/entrants?event_id=28821')
        # Y14WF = Event("Y14 Women's Foil", datetime(2019,7,4,8,0),
                    #  'https://member.usafencing.org/details/tournaments/3697/entrants?event_id=24859&_=1561651014786')
        # DIWF = Event("DivI Women's Foil", datetime(2019,10,20,8,0),
        #              'https://member.usafencing.org/details/tournaments/3877/entrants?event_id=28815')
        # tournament also needs location, date range, link to USFA website, organizing club, contact info    
        self.name = name
        self.events = {
                       JWF.short_name:JWF,
                       CWF.short_name:CWF,
                    #    DIIWF.short_name:DIIWF,
                    #    Y14WF.short_name:Y14WF,
                    #    DIWF.short_name:DIWF
                       }
        self.fpath = pathlib.PurePath("c:/Users/kdkmb/OneDrive/Documents/Fencing/" )
        self.fname = name
        self.temp = pathlib.Path(os.path.abspath(__file__)).parent/'temp'/'fencing_temp.xlsx'
       
    def __getitem__(self,event):
        return self.events[event]
            
        #     def __str__(self):    needs work to figure out how to get to the events sorted by their date and then pfrmat the date for printing
        #         return(f"{self.name}  {sorted(self.events.values(), key = lambda ev: ev.event_date)}")
             
    def create_workbook(self):
        '''creates a temporary excel file in the temp directory containing a 
        sheet of entrant data for each event '''
        with pd.ExcelWriter(self.temp) as writer:  # create temporary file      
            for event in self.events.values():            
                event.write_To_Excel(writer, event.short_name)              
               
    def build_tables(self):   # 
        ''' opens the excel file containing the event data for the tournament 
        and calls macros to format the tables, create pivot tables
        and create event analysis graphs'''
        def create_excel_table (sheet):
            ''' creates and formats excel tables for each set of data'''            
            sheet.ListObjects.Add(win32.constants.xlSrcRange, sheet.Range("A:L"),  win32.constants.xlYes).Name #= sheet
            sheet.Select()
            
            sheet.Columns("D:D").HorizontalAlignment = win32.constants.xlRight  # align Rating and Year
            sheet.Columns("E:E").HorizontalAlignment = win32.constants.xlLeft   # so they appear concatenated
           
            sheet.Columns("A:L").EntireColumn.AutoFit()    # make all columns the right width

            sheet.Columns("A:A").Delete()    #remove the number index column
            sheet.Range("C2").Select()
            excel.ActiveWindow.FreezePanes = True    # freeze spreadsheet table names
            t_name = excel.ActiveCell.ListObject.Name   # retrieve Excel table name for this sheet
            sheet.ListObjects(t_name).ListColumns("WinLoss").DataBodyRange.Formula =\
            '=IF(OR(ISBLANK([@TF]),ISBLANK([@TR])),"",IF([@TF]>[@TR],"Win","Loss"))' 
            # put win/loss formula in column
            for col in ["PoolRound","TF","TR"]: 
                sheet.ListObjects(t_name).ListColumns(col).DataBodyRange.Clear()
            return None

        def add_pivot(sheet,location=(1,1),filters=[],columns=[],
                      rows=[],sumvalue="",sortfield=""):

            """Build a pivot table using the provided source location data        
               and specified fields"""

            # Build the Pivot Table
            p_tname = f"PivotTable{next(tablecount)}"
            
            t_name = excel.Range("A1").ListObject.Name   # retrieve Excel table name for this sheet

            sourcedata = sheet.ListObjects(t_name)        
        
            pc = wb.PivotCaches().Add(SourceType=win32.constants.xlDatabase,        
                                         SourceData=sourcedata)

            pt = pc.CreatePivotTable(TableDestination=f"{sheet.Name}!R{location[0]}C{location[1]+1}",        
                                     TableName=p_tname,        
                                     DefaultVersion=win32.constants.xlPivotTableVersion10)
        

            pt.AddDataField(pt.PivotFields(sumvalue[9:]),sumvalue,win32.constants.xlCount)
                

            for fieldlist,fieldc in ((filters,win32.constants.xlPageField),        
                                     (columns,win32.constants.xlColumnField),        
                                     (rows,win32.constants.xlRowField)):
        
                for i,val in enumerate(fieldlist):        
                    pt.PivotFields(val).Orientation = fieldc
                    pt.PivotFields(val).Position = i+1

            if len(sortfield) != 0:                  
                pt.PivotFields(sortfield[0]).AutoSort(sortfield[1], sumvalue)

            pt.RowAxisLayout (win32.constants.xlCompactRow) 
            pt.ColumnGrand = True
            pt.RowGrand = True
            pt.TableStyle2 = "PivotStyleLight9" #change to comact  design, with totals 
            pt.PivotFields("Division").ShowDetail = False
            pt.PivotFields("Division").AutoSort (win32.constants.xlDescending,"Count of Rating")
            sheet.Columns("P:P").ColumnWidth = 2.10


            # Uncomment the next command to limit output file size, but make sure
        
            # to click Refresh Data on the PivotTable toolbar to update the table
        
            # sheet.PivotTables(tname).SaveData = False

            return p_tname

        
        tablecount = count(1)   #counter for Pivot Table creation

        try:
            excel = win32.gencache.EnsureDispatch( 'Excel.Application')
        except Exception as e :
            print (e.args)
            raise SystemExit ('Communication to Excel failed')

        try:
            wb = excel.Workbooks.Open(self.temp)
        except : 
            raise SystemExit ('File not found', sys.exc_info()[0])
        
    
        excel.Visible = False   # run excel in the background

        

        for sheet in self.events:
            print (f'creating table {sheet}')       
            create_excel_table(wb.Worksheets(sheet))  #convert excel data in each event sheet into formal excel table
            
            add_pivot(sheet=wb.Worksheets(sheet),
                      location=(2,14), 
                      rows=["Division","Club"],
                      columns=["Rating"],
                      sumvalue="Count of Rating")

        # Save the final spreadsheet
        p = pathlib.Path.joinpath(self.fpath, self.fname + time.strftime("_%y%m%d_%H%M%S")+".xlsx")
        wb.SaveAs(str(p)) # create final time-stamped spreadsheet in fencing directory

        # Tidy up
        excel.Application.Quit()  #close excel
        os.remove(self.temp)  #remove the temporary file
        print(f'File saved as {str(p.name)}')

########  MAIN ###########################################################
# 

NovNAC = Tournament("2019 November NAC")
try:
    NovNAC.create_workbook()
except:
    SystemExit('Excel file already open')

print(f'created spreadsheet for {NovNAC.name}')
NovNAC.build_tables()