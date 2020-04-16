import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom # only for pretty
import lxml.etree as EP
import json
import csv

def csvToXml(f): ## csv convert to xml
    
    root = ET.Element("departments")
    tempOfUni = "" # only one root for each univeriste. this temp variable to check this,
    while 1 > 0 :
        line = f.readline()
        if line == "" :
            break
        line = line.split(";")
        if tempOfUni != line[1] : # this statment to control same university name
            tempOfUni = line[1]
            child =ET.SubElement(root, 'university', name=line[1], uType=line[0])
        child2 =ET.SubElement(child, 'item', id=line[3], faculty=line[2])

        second= "no"
        language = ""
        if line[5] == "İngilizce" :
            language = "en"
        if line[6] == "İkinci Öğretim":
            second = "yes"
        ET.SubElement(child2, 'name', lang=language, second=second).text = line[4]
        ET.SubElement(child2, 'period').text = line[8]

        if line[11] == "" or line[11] == "-": #check if you have a special kontejan
            line[11] = "";
        ET.SubElement(child2, 'quota', spec= line[11]).text = line[10] 
        ET.SubElement(child2, 'field').text = line[9]

        if line[12] == "" or line[12] == "-": #control lowest order
            line[12] = ""
        line[13] = line[13].replace("\n","") #control lowest score
        if line[13] == "" or line[13] == "-":
            line[13] = None
        ET.SubElement(child2, 'last_min_score', order=line[12]).text = line[13]

        if line[7] == "" : # scholarship rate if private school, if it's not a private school, this section will be empty.
            line[7] = None
        ET.SubElement(child2, 'grant').text = line[7] # so this statment controls this situation
  
    tree = ET.tostring(root) #at first the tree structure with tostring() was turned into string
    xml_pretty = minidom.parseString(tree).toprettyxml() #it was later converted into pretty with the  xml.dom.minidom library
    
    with open(sys.argv[2],"w", encoding="utf-8") as f:
        f.write(xml_pretty)

def csvToJson(f): #csv convert to json
   
    tempUni = "" # only one root for each univeriste. this temp variable to check this,
    tempFac = "" # only one root for each faculty. this temp variable to check this,
    mylist = []
    indexOfUni = -1
    indexOfitem = -1 
    while 1 > 0 :
        
        line = f.readline()
        if line == "" :
            break
        line = line.split(";")    
        if line[1] !=  tempUni : # this statment to control same university name
            mylist.append({
                'university' : line[1], 'uType' : line[0], 'items' : [] })
            indexOfUni += 1
            indexOfitem = -1 # when you move on to the next college and if the faculty names of the two universities are the same,
            tempFac = "" # a new item won't occur. So temp and indexes need to be reset.
            tempUni = line[1]
    
        if line[2] != tempFac  : # this statment to control same faculty name
            mylist[indexOfUni]['items'].append({'faculty' : line[2], 'department' : [] })
            indexOfitem += 1
            tempFac = line[2]
        second= "no"
        language = ""
        spec = None
        order = None
        min_score = None
        grant = None
        if line[5] == "İngilizce":
            language = "en"
        if line[6] != "" or line[6] != "-":
            second = "yes"
        if line[11] != "" and line[11] != "-":   #check if you have a special kontejan
            spec = int(line[11])
        if line[12] != "" and line[12] != "-": #control lowest order
            order = int(line[12])
        if line[13] != "\n" and line[13] != "-\n" : #control lowest order
            min_score = float(line[13].replace("\n","").replace(",",".")) # no double with comma in English so comma has been replaced with point
        if line[7] != "" and line[7] != "-":
            grant = int(line[7])
        mylist[indexOfUni]['items'][indexOfitem]["department"].append({
            'id' : line[3], 'name' : line[4],
            'lang' : language, 'second' : second,
            'period' : int(line[8]),
            'spec': spec,
            'quota': int(line[10]),
            'field': line[9],
            'last_min_score': min_score,
            'last_min_order': order,
            'grant': grant
        })
    outfile = open(sys.argv[2], "w",encoding="utf-8")        
    data = json.dumps(mylist, ensure_ascii=False, indent = 2)
    outfile.write(data)    
    outfile.close()   

def readCsv():
   
    f = open (sys.argv[1],"r",encoding="utf-8")
    f.readline() # for first row
    if sys.argv[3] == '1' :
        csvToXml(f)
    elif sys.argv[3] == '5' :
        csvToJson(f)
    f.close()
    
def xmlToCsv():

    xmldoc = ET.parse(sys.argv[1]) #open and parse the xml file with xml.etree.ElementTree
    root = xmldoc.getroot()
    data = [] #to keep all data in a 2-dimensional array
    for elem in root: # I dump the Xml file into the tree structure and scan all the information to get it
        for subelem in elem:

            lang = ""
            second = ""
            if subelem[0].attrib['lang'] == "en" :  # this was done title to some rules that were requested from us when converting headers into json files
                lang = "İngilizce"          # so restored according to the rules given when recycling to csv file
            if subelem[0].attrib['second'] == "yes": 
                second = "İkinci Öğretim"
            data.append([elem.attrib['uType'], elem.attrib['name']
            ,subelem.attrib['faculty'], subelem.attrib['id']
            ,subelem[0].text, lang
            ,second, subelem[5].text
            ,subelem[1].text, subelem[3].text
            ,subelem[2].text, subelem[2].attrib['spec']
            ,subelem[4].attrib['order'], subelem[4].text])

    myData = [["ÜNİVERSİTE_TÜRÜ" "ÜNİVERSİTE", "FAKÜLTE", "PROGRAM_KODU","PROGRAM","DİL","ÖĞRENİM_TÜRÜ","BURS","ÖĞRENİM_SÜRESİ",
    "PUAN_TÜRÜ","KONTENJAN","OKUL_BİRİNCİSİ_KONTENJANI","GEÇEN_YIL_MİN_SIRALAMA","GEÇEN_YIL_MİN_PUAN"], 
    data]   # to use the csv library, I assign information and headers to another 2D array      

    myfile=csv.writer(open(sys.argv[2], 'w'), delimiter=';') #creates csv file by semicolon
    myfile.writerow(myData[0]) # to write title
    for line in myData[1]: # to write items
        myfile.writerow(line)

def xmlToJson():
    
    tempUni = "" # only one root for each univeriste. this temp variable to check this,
    tempFac = "" # only one root for each faculty. this temp variable to check this,
    mylist = []
    indexOfUni = -1
    indexOfitems = -1 

    xmldoc = ET.parse(sys.argv[1])
    root = xmldoc.getroot()
    for elem in root:
        for subelem in elem:
            if elem.attrib['name'] !=  tempUni :
                mylist.append({'university' : elem.attrib['name'], 'uType' : elem.attrib['uType'], 'items' : [] })
                indexOfUni += 1
                indexOfitems = -1 # when you move on to the next college and if the faculty names of the two universities are the same,
                tempFac = "" # a new item won't occur. So temp and indexes need to be reset.
                tempUni = elem.attrib['name']
    
            if subelem.attrib['faculty'] != tempFac  :  # this statment to control same faculty name
                mylist[indexOfUni]['items'].append({'faculty' : subelem.attrib['faculty'], 'department' : [] })
                tempFac = subelem.attrib['faculty']
                indexOfitems += 1 
            
            spec = None
            order = None
            min_score = None
            grant = None
            if subelem[2].attrib['spec'] != "":   #check if you have a special kontejan
                spec = int(subelem[2].attrib['spec'])
            if subelem[4].attrib['order'] != "": #control lowest order
                order = int(subelem[4].attrib['order'])
            if subelem[4].text != None : #control lowest order
                min_score = float(subelem[4].text.replace(",",".")) # no double with comma in English so comma has been replaced with point
            if subelem[5].text != None: # if empty , it will throws null
               grant = int(subelem[5].text)
            
            mylist[indexOfUni]['items'][indexOfitems]['department'].append({

                'id' : subelem.attrib['id'],
                'name' : subelem[0].text,
                'lang' : subelem[0].attrib['lang'],
                'second' : subelem[0].attrib['second'],
                'period' : int(subelem[1].text),
                'spec': spec,
                'quota': int(subelem[2].text),
                'field': subelem[3].text,
                'last_min_score': min_score,
                'last_min_order': order,
                'grant': grant
            })
    outfile = open(sys.argv[2], "w",encoding="utf-8") 
    data = json.dumps(mylist, ensure_ascii=False, indent = 2)
    outfile.write(data)
    outfile.close()

def jsonToXml() :
    
    root = ET.Element("departments")
    temp = "" # only one root for each univeriste. this temp variable to check this,
    with open(sys.argv[1]) as f:
        unilist = json.load(f)
    for uni in unilist:
        for item in uni['items']:
           for department in item['department']:
                
                if temp != uni['university']: # this statment to control same university name
                    child =ET.SubElement(root, 'university', name=uni['university'], uType= uni['uType'])
                    temp = uni['university']
                child2 =ET.SubElement(child, 'item', id=department['id'], faculty=item['faculty'])
                spec =""
                min_score = department['last_min_score']
                order = ""
                if department['spec'] != None :
                    spec = str(spec)
                if department['last_min_order'] != None :
                    order = str(department['last_min_order'])
                if min_score != None :
                    min_score = str(min_score).replace(".",",")
                ET.SubElement(child2, 'name', lang=department['lang'], second=department['second']).text = department['name']
                ET.SubElement(child2, 'period').text = str(department['period'])
                ET.SubElement(child2, 'quota', spec= spec).text = str(department['quota']) 
                ET.SubElement(child2, 'field').text = department['field']
                ET.SubElement(child2, 'last_min_score', order= order).text = min_score
                if department['grant'] != None :  # scholarship rate if private school, if it's not a private school, this section will be null.
                    ET.SubElement(child2, 'grant').text = str(department['grant']) # so this statment controls this situation
                else :
                    ET.SubElement(child2, 'grant')

    tree = ET.tostring(root)
    xml_pretty = minidom.parseString(tree).toprettyxml(indent="  ")
    
    with open(sys.argv[2],"w",encoding="utf-8") as f:
        f.write(xml_pretty)


def jsonToCsv():
    
    data = [] #to keep all data in a 2-dimensional array
    with open(sys.argv[1],encoding="utf-8") as f:
        unilist = json.load(f) # I read all the information in jsonda then I visited them all in the form of a list and dictionary
    for uni in unilist:
        for item in uni['items']:
            for department in item['department']:
                
                spec =""
                min_score = department['last_min_score']
                order = ""
                lang = ""
                second = ""
                if department['lang'] == "en" : # this was done title to some rules that were requested from us when converting headers into json files
                    lang = "İngilizce"          # so restored according to the rules given when recycling to csv file
                if  department['second'] == "yes":
                    second = "İkinci Öğretim"
                if department['spec'] != None :
                    spec = str(spec)
                if department['last_min_order'] != None :
                    order = str(department['last_min_order'])
                if min_score != None :   
                    min_score = str(min_score).replace(".",",")

                data.append([uni['uType'], uni['university']
                ,item['faculty'], department['id'], department['name']
                , lang, second, department['grant']
                ,department['period'], department['field'], department['quota']
                ,spec, order ,min_score])

    myData = [["ÜNİVERSİTE_TÜRÜ" "ÜNİVERSİTE", "FAKÜLTE", "PROGRAM_KODU","PROGRAM","DİL","ÖĞRENİM_TÜRÜ","BURS","ÖĞRENİM_SÜRESİ",
    "PUAN_TÜRÜ","KONTENJAN","OKUL_BİRİNCİSİ_KONTENJANI","GEÇEN_YIL_MİN_SIRALAMA","GEÇEN_YIL_MİN_PUAN"], 
    data] # to use the csv library, I assign information and headers to another 2D array         

    outfile=csv.writer(open(sys.argv[2], 'w'), delimiter=';')
    outfile.writerow(myData[0]) # to write title
    for line in myData[1]: # to write items
        outfile.writerow(line)



def valitation():

    doc = ET.parse(sys.argv[1]) # firstly XML has been read and parsed with xml library 
    root = doc.getroot() 
    xmlschema_doc = EP.parse(sys.argv[2]) # XSD has been parsed with lxml
    xmlschema = EP.XMLSchema(xmlschema_doc)
    doc = EP.XML(ET.tostring(root))
    validation_result = xmlschema.validate(doc) #  XML file  has been Confirmed with XSD file
    print(validation_result)
    xmlschema.assert_(doc)
    
def main():

    input_file = sys.argv[1].split(".") # input and output  have been splited with point  
    output_file = sys.argv[2].split(".") # so length should be 2 if it is not then this input or output are wrong
    if len(input_file) == 2 and len(output_file) == 2 : #to check that inputs and outputs are entered correctly
        if sys.argv[3] == "1":
            if output_file[1]== "xml" and input_file[1] == "csv":
                readCsv()
            else :
                print("- XML or CSV extension is incorrect") # user may enter file extension incorrectly , required operations cannot be performed with incorrect extension
        elif sys.argv[3] == "2":                              # So error checking was done here for extensions
            if output_file[1]== "csv" and input_file[1] == "xml":
                xmlToCsv()
            else :
                print("- XML or CSV extension is incorrect")
        elif sys.argv[3] == "3":
            if output_file[1]== "json" and input_file[1] == "xml":
                xmlToJson()
            else :
                print("- XML or JSON extension is incorrect")
        elif sys.argv[3] == "4":
            if output_file[1]== "xml" and input_file[1] == "json":
                jsonToXml()
            else :
                print("- XML or JSON extension is incorrect")
        elif sys.argv[3] == "5":
            if output_file[1]== "json" and input_file[1] == "csv":
                readCsv()
            else :
                print("- CSV or JSON extension is incorrect")
        elif sys.argv[3] == "6":
            if output_file[1]== "csv" and input_file[1] == "json":
               jsonToCsv()
            else :
                print("- CSV or JSON extension is incorrect")
        elif sys.argv[3] == "7":
            
            if output_file[1]== "xsd" and input_file[1] == "xml":
                   valitation()
            else :
                print("- XSD or XML extension is incorrect")
        else :
            print("- You entered the wrong command ")
    else :
        if len(input_file) != 2 :
            print("- You entered the wrong input output file name")
        else :
            print("- You entered the wrong output file name")
main()