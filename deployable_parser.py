import sys
import os
import string
import pandas as pd
import pdftotext
from io import StringIO
import io
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

class LinkedinParser:

    def read(self,f):
        '''
        Function to read the text file
        '''
        str=f.getvalue()
        Lines=str.splitlines()
        return Lines

    def extract_basics(self,Lines,resp):
        '''
        This function helps separate the text in the left column
        of the resume from that of the right side. It looks at the
        number of spaces between text in each line and appends the
        text on the right side into a list sequentially.It also extracts
        the name, position and location of the candidate.
        '''
        left=[]
        right=[]
        rest=[]
        num,lc,lc2=0,0,0
        for line in Lines:
            lc+=1
            if 'Page 1 of' in line:
                num=lc
                break
            else:
                left.append(line.split('       ')[0])
        for line in Lines:
            lc2+=1
            if 'Page 1 of' in line:
                print('')
            elif lc2>num:
                rest.append(line)
            else:
                try:
                    c=0
                    s=0
                    for i in line:
                        s+=1
                        if i==' ':
                            c+=1
                        else:
                            c=0
                        if c>5:
                            c=s
                            pos=c
                    str=line[pos:len(line)]
                    right.append(str)
                except:
                    print('\n')
        Ord_Lines=[]
        if right[2]!='':
            name=right[2]
            pos=right[3]
            loc=right[4]
            lst=loc.split()
            num=len(lst)
            if num<=3:
                loc=right[4]
            else:
                loc=right[5]
        else:
            name=right[3]
            pos=right[4]
            loc=right[5]
            lst=loc.split()
            num=len(lst)
            if num<=3:
                loc=right[5]
            else:
                loc=right[6]
        resp['name']=name.strip()
        resp['position']=pos.strip()
        resp['location']=loc.strip()
        if resp['location']=='Summary':
            resp['location']="India"
        Ord_Lines=left+right+rest
        return Ord_Lines

    def extract_about(self,Lines,resp):
        '''
        Extracts summary and email ID from resume
        using simple text pattern matching.
        '''
        lc,start,s,e,em,i,p=0,0,0,0,0,0,0
        end=len(Lines)
        sum=[]
        for line in Lines:
            lc+=1
            if "Summary" in line and s==0:
                s==1
                start=lc
            elif "Experience" in line and e==0:
                e=1
                end=lc
            elif "@" in line and em==0:
                em=1
                resp['email']=line
        for line in Lines:
            i+=1
            if i in range(start+1,end) and start!=0:
                line=line.strip()
                line=line.replace("\xa0","")
                sum.append(line)
        str=" ".join(sum)
        resp['summary'].append(str)
        return resp

    def extract_edu(self,Lines,resp):
        '''
        Extracts education from the resume based on
        keywords searching
        '''
        start,ed,lc,i=0,0,0,0
        end=len(Lines)
        edu=[]
        for line in Lines:
            lc+=1
            if 'Education' in line and ed==0:
                lst=line.split()
                num=len(lst)
                if num==1:
                    ed=1
                    start=lc
                    break
        if start!=0:
            for line in Lines:
                i+=1
                if i in range(start+1,end):
                    line=line.strip()
                    line=line.replace("\xa0","")
                    if line!='':
                        resp['education'].append(line)
                    elif line=='\n':
                        print('')
        return resp

    def create_edu(self):
        '''
        A structured response that can hold the relevant
        details of the education section.
        '''
        edu={
        'ID':"",
        'school':"",
        'degree':"",
        'fieldOfStudy':"",
        'location':"India",
        'startDate':"",
        'endDate':""
        }
        return edu

    def subsec_edu(self,Lines,resp):
        '''
        This further sections the education section,
        retrieving and storing only the important elements.
        '''
        x,lc,num=0,0,0
        summary=[]
        mylist=resp['education']
        for i in mylist:
            lc+=1
            if 'College' in i or 'Institute' in i or 'University' in i:
                mydict=self.create_edu()
                mydict['ID']=x
                mydict['school']=i
                try:
                    mydict['degree']=mylist[lc].split(',')[0]
                    mydict['fieldOfStudy']=mylist[lc].split(',')[1]
                    mydict['fieldOfStudy']=mydict['fieldOfStudy'].split('(')[0]
                    str=mylist[lc].split(',')[1]
                    date=str[str.find("(")+1:str.find(")")]
                    mydict['startDate']=date.split('-')[0].strip()
                    mydict['endDate']=date.split('-')[1].strip()
                except:
                    print('')
                summary.append(mydict)
                x+=1
            elif 'college' in i or 'institute' in i or 'university' in i:
                mydict=create_edu()
                mydict['ID']=x
                mydict['school']=i
                try:
                    mydict['degree']=mylist[lc].split(',')[0]
                    mydict['fieldOfStudy']=mylist[lc].split(',')[1]
                    mydict['fieldOfStudy']=mydict['fieldOfStudy'].split('(')[0]
                    str=mylist[lc].split(',')[1]
                    date=str[str.find("(")+1:str.find(")")]
                    mydict['startDate']=date.split('-')[0].strip()
                    mydict['endDate']=date.split('-')[1].strip()
                except:
                    print('')
                summary.append(mydict)
                x+=1
            elif 'School' in i or 'Academy' in i:
                mydict=self.create_edu()
                mydict['ID']=x
                mydict['school']=i
                try:
                    mydict['degree']=mylist[lc].split(',')[0]
                    mydict['fieldOfStudy']=mylist[lc].split(',')[1]
                    mydict['fieldOfStudy']=mydict['fieldOfStudy'].split('(')[0]
                    str=mylist[lc].split(',')[1]
                    date=str[str.find("(")+1:str.find(")")]
                    mydict['startDate']=date.split('-')[0].strip()
                    mydict['endDate']=date.split('-')[1].strip()
                    if mydict['startDate']=='' or mydict['endDate']=='':
                        try:
                            str=mydict['degree'].split('\xa0·\xa0')
                            date=str[str.find("(")+1:str.find(")")]
                            mydict['startDate']=date.split('-')[0].strip()
                            mydict['endDate']=date.split('-')[1].strip()
                        except:
                            print('')
                except:
                    print('')
                summary.append(mydict)
                x+=1
        resp['education']=summary
        return resp

    def extract_skills(self,Lines,resp):
        '''
        Extracts skills from resume based on keywords.
        '''
        start,lc,sk,c,i=0,0,0,0,0
        end=len(Lines)
        skills=[]
        for line in Lines:
            lc+=1
            if 'Top Skills' in line and sk==0:
                sk=1
                start=lc
            elif 'Certifications' in line and c==0:
                c=1
                end=lc
            elif resp['name'] in line and c==0:
                c=1
                end=lc
        if start!=0 and end!=len(Lines):
            for line in Lines:
                i+=1
                if i in range(start+1,end):
                    line=line.strip()
                    if line!='':
                        line=line.replace("\xa0","")
                        resp['skills'].append(line)
        return resp

    def extract_lang(self,Lines,resp):
        '''
        Extracts languages from resume based on sectioning
        and keywords.
        '''
        start,lc,lng,c,i=0,0,0,0,0
        end=len(Lines)
        lang=[]
        for line in Lines:
            lc+=1
            if 'Languages' in line and lng==0:
                start=lc
                lng=1
            elif 'Certifications' in line and c==0:
                end=lc
                c=1
        if start!=0:
            for line in Lines:
                i+=1
                if i in range(start+1,end):
                    line=line.strip()
                    if line!='':
                        line=line.replace("\xa0","")
                        resp['Languages'].append(line)
        return resp

    def extract_courses(self,Lines,resp):
        '''
        Extracts Courses based on search for keywords.
        '''
        start,lc,c,n,i=0,0,0,0,0
        end=len(Lines)
        lang=[]
        for line in Lines:
            lc+=1
            if 'Certifications' in line and c==0:
                start=lc
                c=1
            elif resp['name'] in line and n==0:
                end=lc
                n=1
        if start!=0:
            for line in Lines:
                i+=1
                if i in range(start+1,end):
                    line=line.strip()
                    if line!='':
                        line=line.replace("\xa0","")
                        resp['courses'].append(line)
        return resp

    def create_course(self):
        '''
        Structure to store certificates.
        '''
        cert={
        'title':"",
        'issuer':"NA",
        }
        return cert

    def subsec_course(self,Lines,resp):
        '''
        Extract relevant details of certifications
        '''
        summ=[]
        mylist=resp['courses']
        for i in mylist:
            if i[0].isupper():
                words=i.split()
                num=len(words)
                if num>=2:
                    cert=self.create_course()
                    cert['title']=i
                    summ.append(cert)
                else:
                    cert['title']+=" "
                    cert['title']+=str(i)
        resp['courses']=summ
        return resp

    def extract_pub(self,Lines,resp):
        '''
        Extracts publications if any based on keywords
        and sectioning.
        '''
        start,lc,c,n,i=0,0,0,0,0
        end=len(Lines)
        lang=[]
        for line in Lines:
            lc+=1
            if 'Publications' in line and c==0:
                start=lc
                c=1
            elif resp['name'] in line and n==0:
                end=lc
                n=1
        if start!=0:
            for line in Lines:
                i+=1
                if i in range(start+1,end):
                    line=line.strip()
                    if line!='':
                        line=line.replace("\xa0","")
                        resp['publications'].append(line)
        return resp

    def extract_hon(self,Lines,resp):
        '''
        Looks for honors and awards in the resume
        based on sectioning and keywords.
        '''
        start,lc,c,n,i=0,0,0,0,0
        end=len(Lines)
        lang=[]
        for line in Lines:
            lc+=1
            if 'Honors-Awards' in line and c==0:
                start=lc
                c=1
            elif resp['name'] in line and n==0:
                end=lc
                n=1
        if start!=0:
            for line in Lines:
                i+=1
                if i in range(start+1,end):
                    line=line.strip()
                    if line!='':
                        line=line.replace("\xa0","")
                        resp['achievement'].append(line)
        return resp

    def extract_exp(self,Lines):
        '''
        Extracts experience section in the resume
        based on keywords.
        '''
        lc,start,ex,ed,i=0,0,0,0,0
        end=len(Lines)
        exp=[]
        for line in Lines:
            lc+=1
            if 'Experience' in line and ex==0:
                lst=line.split()
                num=len(lst)
                if num==1:
                    start=lc
                    ex=1
                else:
                    ex=0
            elif 'Education' in line and ed==0:
                lst=line.split()
                num=len(lst)
                if num==1:
                    end=lc
                    ed=1
                else:
                    ed=0
        if start!=0:
            for line in Lines:
                i+=1
                if i in range(start+1,end):
                    line=line.replace("\xa0","")
                    exp.append(line)
        #print(exp)
        return exp

    def create_exp(self):
        '''
        Dictionary to store essential components of
        the experience section.
        '''
        exp={
        'title':"",
        "company":"",
        "location":"",
        "startDate":"",
        "endDate":"",
        "description":""
        }
        return exp

    def subsec_exp(self,EXP,resp):
        '''
        Retrieve essential information from
        experience section via text patterns.
        '''
        c=0
        summ=[]
        for i in EXP:
            c+=1
            if i=='\n' or i=='':
                try:
                    if EXP[c+1]!='\n' and EXP[c+1]!='\x0c\xa0\n' and EXP[c+1]!='\xa0\n':
                        check=EXP[c+1].split()
                        num=len(check)
                        if num<=4:
                            exp_dict=self.create_exp()
                            exp_dict['company']=EXP[c]
                            exp_dict['title']=EXP[c+1]
                            exp_dict['startDate']=EXP[c+2].split('-')[0]
                            exp_dict['endDate']=EXP[c+2].split('-')[1]
                            exp_dict['location']=EXP[c+3]
                            ls=exp_dict['location'].strip()
                            if ls=='':
                                exp_dict['location']='India'
                            else:
                                innt=4
                                while EXP[c+innt]!='':
                                    exp_dict['description']+=EXP[c+innt]
                                    innt+=1
                            summ.append(exp_dict)
                except:
                    print('')
        resp['experiences']=summ
        return resp

    def extract_info(self,fname,MyLines):
        '''
        This function encapsulates all the functions above.
        '''
        resp={
        'name':"",
        'position':"",
        'location':"",
        'email':"",
        'summary':[],
        'education':[],
        'experiences':[],
        'publications':[],
        'skills':[],
        'courses':[],
        'achievement':[],
        'languages':[]
        }
        Lines=self.read(fname)
        Ord_Lines=self.extract_basics(Lines,resp)
        self.extract_about(Ord_Lines,resp)
        self.extract_edu(Ord_Lines,resp)
        self.subsec_edu(Ord_Lines,resp)
        self.extract_skills(Ord_Lines,resp)
        self.extract_courses(Ord_Lines,resp)
        self.subsec_course(Ord_Lines,resp)
        self.extract_pub(Ord_Lines,resp)
        exp=self.extract_exp(MyLines)
        self.subsec_exp(exp,resp)
        self.extract_hon(Ord_Lines,resp)
        return resp

    def convert_using_pdfminer(self,fp):
        '''
        PDFminer is needed to subsection the experience section.
        This function ensures that pdfminer processes the entered
        PDF file.
        '''
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos=set()
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)
        text = retstr.getvalue()
        fp.close()
        device.close()
        retstr.close()
        Ord_Lines=text.splitlines()
        return Ord_Lines

    def convert_pdf(self,f):
        '''
        Takes filepath as input and converts pdf to text file
        '''
        pdf=pdftotext.PDF(f)
        textfile=StringIO()
        textfile.writelines(pdf)
        return textfile

    def generate_parser(self,f):
        '''
        This is the main function, which takes the directory name as a command line
        argument. (See use case above) It makes use of the LinkedinParser class, which is an
        encapsulation of all the previously defined functions.
        '''
        #Call to convert PDF to text file
        PDF=self.convert_pdf(f)
        #Call to help subsec experience section
        MyLines=self.convert_using_pdfminer(f)
        #call to parse resume
        resp=self.extract_info(PDF,MyLines)
        print(resp)
        return resp
