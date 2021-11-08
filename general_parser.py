'''
This code is to be used on resume PDFs.
Each function is designed to extract a particular section of the resume.
USE CASE: python3 pdf_parse.py *full path of resume to be parsed*
RESULT: result.txt can be found in pwd of system
Dependencies: python3.7, pandas, dateparser, stanza, pdftotext
NOTE: To execute this script via jupyter, make sure you install stanza via anaconda
command: conda install -c stanfordnlp stanza
'''
#stanza.download('en') UNCOMMENT IF RUNNING SCRIPT FIRST TIME
import sys
import stanza
import os
import pdftotext
import textract
import pandas as pd
import re
from io import StringIO
from collections import OrderedDict
from dateutil.parser import parse
from dateparser import parse
nlp=stanza.Pipeline(lang='en', processors='tokenize,ner',verbose=False)

class ResumeParser:

    def __init__(self):
        pass

    class my_dictionary(dict):
        '''
        This class's main purpose is to include a function
        which can add a key-value pair to an ordered dictionary.
        This is useful at the time of finding the positions of
        all sections.
        '''
        def __init__(self):
            self = OrderedDict()

        def add(self, key, value):
            self[key] = value

    def convert_pdf(self,f):
        '''
        Takes filepath as input and converts pdf to text file
        '''
        pdf=pdftotext.PDF(f)
        textfile=StringIO()
        textfile.writelines(pdf)
        return textfile

    def sep_section(self,f):
        '''
        This function helps separate the text in the left column
        of the resume from that of the right side. It looks at the
        number of spaces between text in each line and appends the
        text on the right side into a list sequentially.
        '''
        left=[]
        right=[]
        str=f.getvalue()
        Lines=str.splitlines()
        for line in Lines:
            left.append(line.split('       ')[0])
        for line in Lines:
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
                pass
        Ord_Lines=left+right
        return Ord_Lines

    def is_dur(self,str):
        '''
        str: input string
        functionality: checks if passed string reprsents a duration
        returns: bool=True if string represents duration, False Otherwise
        '''
        if '-' not in str and 'to' not in str and '–' not in str:
            bool=False
        elif '-' in str:
            sdate=str.split('-')[0]
            sdate=sdate.strip()
            edate=str.split('-')[1]
            edate=edate.strip()
            if parse(sdate)!=None:
                bool=True
            else:
                bool=False
        elif 'to' in str:
            sdate=str.split('to')[0]
            sdate=sdate.strip()
            edate=str.split('to')[1]
            edate=edate.strip()
            if parse(sdate)!=None:
                bool=True
            else:
                bool=False
        elif '–' in str:
            sdate=str.split('–')[0]
            sdate=sdate.strip()
            edate=str.split('–')[1]
            edate=edate.strip()
            if parse(sdate)!=None:
                bool=True
            else:
                bool=False
        else:
            bool=False
        return bool

    def is_sec(self,f):
        '''
        This function counts the number of lines that have doubled column text to determine
        whether the resume has one columns or two.
        If the only text after a split represents a date, it is taken as one single line.
        '''
        split=True
        flag_arr=[]
        pos_arr=[]
        lc,o,t=0,0,0
        str=f.getvalue()
        Lines=str.splitlines()
        n=len(Lines)
        for i in range (0,n):
            flag_arr.append(0)
            pos_arr.append(0)
        for line in Lines:
            lc+=1
            line=line.lstrip()
            try:
                c=0
                s=0
                flag=0
                for i in line:
                    s+=1
                    if i==' ':
                        c+=1
                    else:
                        c=0
                    if c>7:
                        c=s
                        pos=c
                        pos_arr[lc]=c
                        flag_arr[lc]=1
            except:
                pass
        lc=0
        for line in Lines:
            lc+=1
            if lc==n:
                break
            elif flag_arr[lc]==1:
                if pos_arr[lc]!=0:
                    str=line[pos_arr[lc]:len(line)]
                    dur=self.is_dur(str)
                    if len(str)==0:
                        o+=1
                    elif dur==True:
                        o+=1
                    else:
                        t+=1
                else:
                    o+=1
            else:
                o+=1
        if o>0.63*n:
            split=False
        else:
            split=True
        return split

    def find_and_sort(self,f,Lines):
        '''
        This function uses a list of keywords pertaining to certain categories to find
        the starting point of the essential sections in a resume and stores these starting
        points in a dictionary. It returns a sorted dictionary which has the starting points
        of sections in ascending order.
        '''
        #Linecount variable
        lc=0
        #Experience keywords
        exp=["Experience","Work Experience","Experiences","Experience/Internships","Professional Experiences",
         "Positions of Responsibility","Entrepreneurial Experience","EXPERIENCE\n","Professional Experience",
        "Job Qualification","Professional Qualifications","Job Qualifications","Job Experience","Job Responsibilities","Work",
        "Working Experience","Work Profile in Current Industry","Internships","Internship","Internship/Trainings","Current Job Experience"]
        #Programming keywords
        pro=["Programming Skills","Programming Languages","Technical Skills","Hard Skills","Programming","Technical Skills and Interests","Technical Strengths"]
        #Project keywords
        projects=["Projects","Technical Projects","Key Projects","Notable Projects","Defining Projects","Defining Work",
        "Course Projects","Personal projects",'Projects:\n',"Project","Undergraduate Project","Minor Projects"]
        #achievements keywords
        acc=["Accomplishments","Achievements","Top Achievements","Top Accomplishments",
        "Scholastic Achievements","Academic Achievements","'Achievements and Responsibilities'"]
        #fellowship keywords
        fell=["Fellowships/Awards","Fellowships","Awards and Fellowships","Fellowships and Awards","Awards & Fellowships", "Fellowships & Awards"]
        #software keywords
        sw=["Softwares","Software Skills","Software","Software Known","IT & english skills"]
        #about keywords
        abt=["About Me","Personal Details","Background","About","Career Summary","Life Philosophy","Professional Summary",
        "Job Profile: -","My Life Philosophy","Most Proud Of","Objective","Career Objective","Personal Profile","Personal Information","Summary"]
        #awards keywords
        aw=["Certifications and Awards","Certifications & Awards","Awards","Awards/Certification","Certifications/Awards",
        "Awards and Certifications","Awards & Certifications","Awards and Recognition","Awards & Recognition","Recognition and Awards","Recognition & Awards",
        "Honors and Awards","Honors & Awards","Awards & Honors","Awards and Honors","Honours and Awards",
        "Honours & Awards","Awards & Honours","Awards and Honours","Honors","Honours","Awards & Achievements","Awards and Achievements","Achievements & Awards",
        "Achievements and Awards","Awards & Scholarships","Awards and Scholarships","Scholarships & Awards",
        "Scholarships and Awards","Scholarships","Fellowships/Awards","HONORS & AWARDS"]
        #Research keywords
        res=["Publications","Researcher","Research Experience","Undergraduate Researcher","Graduate Researcher",
        "Research Interest","Research Interests","Research Work","Research","Research Activities","Research Publications",
        "Research Publication"]
        #Interest keywords
        ints=["Interests","Interest","Areas of Interest","Area of Interest","Area of Interests","Other Interests","Hobbies","My Hobbies"]
        #soft skills
        ss=["Soft Skills","Soft Skill Set","Personal Strengths","Best Qualities","Personal Traits","Personality Traits"]
        #skills keywords
        sk=["Skills","Strengths","Skills and Strengths","Strengths and Skills","Skills & Strengths","Strength",
        "Areas of Expertise","Key Areas of Expertise","Strengths & Skills","Key Skills","Key Strengths","I.T. Skills","it skills",
        "Skills and Abilities","Skills & Abilities ","Skill sets"]
        #volunteer work keywords
        vw=["Volunteering","Volunteer Work","Community Outreach","Social Activities","Community Contribution","Teaching",
        "Teaching Experience"]
        #Philosophy keywords
        phil=["Life Philosophy","My Life Philosophy","Most Proud Of"]
        #courses keywords
        crs=["Relevant Courses","Courses","Courses/Certificates","Courses/Certifications","Courses and Certifications",
        "Courses & Certification","Certifications/Courses","Certifications and Courses","Certification & Courses",
        "Coursework","Courseworks","Other Qualifications","Other Qualification","Certifications","Certificates",
        "Certificates/Online Courses","Certification","Professional Qualification","Courses Taken","Courseworks","Course Works",
        "CourseWork","Course Work","COURSEWORKS","Online Certifications"]
        #activities keywords
        acts=["Co-Curricular Activities","Extra-Curricular Activities","Extra Curricular Activities","Co-Curriculars","Extra-Curricular Activities",
        "Co-Curricular","Professional Affiliations & Activities","Extra-Curriculars","CO/EXTRA-CIRRUCULAR","Extracurricular Activity"]
        #references keywords:
        ref=["Reference","References","Referres"]
        #languages keywords
        lang=["Languages","Languages Known","Language Proficiency"]
        #edu keywords
        edu=["Education","Education Qualification","Educational Qualification","Educational Qualifications","Academic Qualification",
        "Academic Qualifications","Educational Credentials","Education Background","Professional & Educational Qualifications",
        "Education / Courses"]

        pointer_dict = {
        'edu':0,
        'exp':0,
        'pro':0,
        'projects':0,
        'acc':0,
        'fell':0,
        'abt':0,
        'sw':0,
        'aw':0,
        'res':0,
        'ints':0,
        'ss':0,
        'sk':0,
        'vw':0,
        'phil':0,
        'crs':0,
        'acts':0,
        'ref':0,
        'lang':0
        }

        punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        for line in Lines:
            lc+=1
            line=line.lower()
            for x in line:
                   if x in punctuations:
                       line=line.replace(x, "")
            for i in edu:
                i=i.replace("\n","")
                if i.lower()==line.strip():
                    pointer_dict['edu']=lc
            for i0 in exp:
                i0=i0.replace("\n", "")
                if i0.lower()==line.strip():
                    pointer_dict['exp']=lc
            for i1 in pro:
                i1=i1.replace("\n", "")
                if i1.lower()==line.strip():
                    pointer_dict['pro']=lc
            for i2 in projects:
                i2=i2.replace("\n", "")
                if i2.lower()==line.strip():
                    pointer_dict['projects']=lc
            for i3 in acc:
                i3=i3.replace("\n", "")
                if i3.lower()==line.strip():
                    pointer_dict['acc']=lc
            for i4 in fell:
                i4=i4.replace("\n", "")
                if i4.lower()==line.strip():
                    pointer_dict['fell']=lc
            for i5 in sw:
                i5=i5.replace("\n", "")
                if i5.lower()==line.strip():
                    pointer_dict['sw']=lc
            for i6 in abt:
                i6=i6.replace("\n", "")
                if i6.lower()==line.strip():
                    pointer_dict['abt']=lc
            for i7 in aw:
                i7=i7.replace("\n", "")
                if i7.lower()==line.strip():
                    pointer_dict['aw']=lc
            for i8 in res:
                i8=i8.replace("\n", "")
                if i8.lower()==line.strip():
                    pointer_dict['res']=lc
            for i9 in ints:
                i9=i9.replace("\n","")
                if i9.lower()==line.strip():
                    pointer_dict['ints']=lc
            for i10 in ss:
                i10=i10.replace("\n", "")
                if i10.lower()==line.strip():
                    pointer_dict['ss']=lc
            for i11 in sk:
                i11=i11.replace("\n", "")
                if i11.lower()==line.strip():
                    pointer_dict['sk']=lc
            for i12 in vw:
                i12=i12.replace("\n", "")
                if i12.lower()==line.strip():
                    pointer_dict['vw']=lc
            for i13 in phil:
                i13=i13.replace("\n", "")
                if i13.lower()==line.strip():
                    pointer_dict['phil']=lc
            for i14 in crs:
                i14=i14.replace("\n", "")
                if i14.lower()==line.strip():
                    pointer_dict['crs']=lc
            for i15 in acts:
                i15=i15.replace("\n", "")
                if i15.lower()==line.strip():
                    pointer_dict['acts']=lc
            for i16 in ref:
                i16=i16.replace("\n", "")
                if i16.lower()==line.strip():
                    pointer_dict['ref']=lc
            for i17 in lang:
                i17=i17.replace("\n", "")
                if i17.lower()==line.strip():
                    pointer_dict['lang']=lc
        #OrderedDict
        dict=self.my_dictionary()
        for i in sorted(pointer_dict, key=pointer_dict.get, reverse=False):
            dict.add(i,pointer_dict[i])
        return dict

    def extract_basic(self,f,response):
        '''
        This function extracts the name, mobile number and
        email ID from the resume using simple search patterns.
        '''
        str=f.getvalue()
        Lines=str.splitlines()
        lc,n,e,p=0,0,0,0
        for line in Lines:
            lc+=1
            #Extract Name
            if 'Name' in line and 'Father' not in line and 'Mother' not in line and 'RESUME' not in line:
                response['name']=line
                n=1
            if lc==1:
                line1=line.lower()
                line1=line1.strip()
                if '@' in line:
                    words=line.split()
                    if len(words)>=3:
                        str=" ".join(words[0:2])
                        response['name']=str
                        n=1
                elif line1=='resume' or line1=='curriculum vitae' or line1=='cv' or line1=='my resume' or 'Last Updated' in line or '@' in line:
                    n=0
                else:
                    words=line.split()
                    if len(words)!=0:
                        str=" ".join(words[0:2])
                        response['name']=str
                        n=1
                    else:
                        n=0
            elif lc==2 and n==0:
                line=line.strip()
                words=line.split()
                if len(words)<=4:
                    if 'Mob' not in line:
                        if any(i.isdigit() for i in words)==True and len(words)<=2:
                            n=0
                        else:
                            str=" ".join(line.split())
                            response['name']=str
                            n=1
                else:
                    n=0
            elif lc==3 and n==0:
                str=" ".join(line.split())
                response['name']=str.split('  ')[0]
                n=1
            #Extract Email and Phone number
            words=line.split()
            for word in words:
                if '@' in word and e==0:
                    response['email']=word
                    e=1
                elif (word[0]=='+' and len(word)>=8 and len(word)<=20 and p==0) or (word.isdigit() and len(word)>=8 and len(word)<=18 and p==0):
                    if 'Mob.' in word:
                        response['phone_number']=word
                        p=1
                    else:
                        response['phone_number']=word
                        p=1
                elif (p==0 and word[0]=='9' and len(word)>8) or (word[0]=='4' and len(word)>8 and p==0) or (word[0]=='3' and len(word)>8 and p==0):
                    response['phone_number']=word
                    p=1
                elif 'Contact' in line or 'Phone' in line or 'Mob' in line and p==0:
                    response['phone_number']=line
                    p=1
        return response

    def extract_edu(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the education section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,start=0,0,0
        end=len(Lines)
        if sec_dict['edu']!=0:
            start=sec_dict['edu']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
        for line in Lines:
            lc+=1
            if start!=0:
                if lc in range(start+1,end):
                    line=line.replace('\xa0',"")
                    line=line.replace('\x11',"")
                    response['education'].append(line)
        return response

    def create_edu(self):
        edu={
        'ID':"",
        'school':"",
        'degree':"",
        'fieldOfStudy':"",
        'startDate':"",
        'endDate':""
        }
        return edu

    def subsec_edu(self,Lines,response):
        #Requirements for formatting the education section
        Qual=["phd","mcom","mtech","masters","mba","mcom","master of commerce","masters of commerce","ms","bcom","btech",#"ba",
        "diploma","graduate through commerce","bachelor of technology","b.tech","bachelors of technology","commerce graduate","bs",
        "intermediate","high school","secondary"]
        inst=['university',"institute","institution","school","academy","college","universitetas","universitetas","iit","iiit","iim","nit","niit","puc"]
        fos=["computer science","information technology","computer and communication","computers and communication","electronics","eletrical engineering","automotive design",
            "mechanical engineering","civil engineer","automotive engineering","chemical engineering","math","physics","biology","chemistry","aviation","physical","metallurgy","earth sciences",
            "economics","political science","history","geography","arts","management","commerce"]
        univ=[]
        deg=[]
        dates=[]
        count,lc,flag,lim,df,cf=0,0,0,0,0,0
        sum=[]
        CGPA="N/A"
        for line in Lines:
            lc+=1
            line1=line.lower()
            for i in fos:
                if i in line1:
                    str=i
            bool=any(ele in line1 for ele in inst)
            if bool==True:
                edu=self.create_edu()
                count+=1
                edu['ID']=count
                try:
                    edu['degree']=Lines[lc].strip()
                    if lim==0:
                        temp=edu['degree'].lower()
                        temp=temp.strip()
                        for i in fos:
                            if i in temp:
                                edu['fieldOfStudy']=i
                        flag=1
                        lim==1
                    if flag==0:
                        for x in fos:
                            if x in line1:
                                edu['degree']=x
                        edu['fieldOfStudy']=Lines[lc].split('in')[1]
                    if edu['fieldOfStudy']=="":
                        edu['fieldOfStudy']=edu['degree']
                except:
                    pass
                if df==0:
                    temp_doc=nlp(line)
                    for ent in temp_doc.ents:
                        if ent.type=='DATE':
                            date=ent.text
                            try:
                                edu['startDate']=date.split('–')[0]
                                edu['endDate']=date.split('-')[1]
                                df=1
                            except:
                                pass
                            if edu['endDate']=='':
                                try:
                                    edu['startDate']=date.split('–')[0]
                                    edu['endDate']=date.split('–')[1]
                                    df=1
                                except:
                                    pass
                    else:
                        words=line.split(',')
                        for word in words:
                            for q in Qual:
                                if q in word.lower():
                                    try:
                                        edu['degree']=word.strip()
                                        if df==0:
                                            date=edu['fieldOfStudy'].split('    ')
                                            num=len(date)
                                            try:
                                                edu['fieldOfStudy']=date[0]
                                                edu['startDate']=date[num-1].split('-')[0]
                                                edu['endDate']=date[num-1].split('-')[1]
                                            except:
                                                try:
                                                    edu['startDate']=date.split('–')[0]
                                                    edu['endDate']=date.split('–')[1]
                                                    df=1
                                                except:
                                                    pass
                                    except:
                                        pass
                        word1=word.lower()
                        for i in inst:
                            if i in word1:
                                edu['school']=word.strip()
                sum.append(edu)
        if len(sum)!=0:
            response['education']=sum
        return response

    def extract_exp(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the Experience section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc=0
        s=0
        start=0
        end=len(Lines)
        if sec_dict['exp']!=0:
            start=sec_dict['exp']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
        for line in Lines:
            lc+=1
            if start!=0:
                if lc in range(start+1,end):
                    line=line.replace('\xa0',"")
                    line=line.replace('\x11',"")
                    response['experiences'].append(line)
        return response

    def create_exp(self):
        exp={
        "company":"",
        "title":"",
        "description":"",
        "startDate":"",
        "endDate":""
        }
        return exp

    def subsec_exp(self,Lines,response):
        lc=0
        sum=[]
        sep=[]
        for line in Lines:
            lc+=1
            line=line.strip()
            temp_doc=nlp(line)
            for ent in temp_doc.ents:
                if ent.type=='DATE':
                    flag=1
                    exp=self.create_exp()
                    date=ent.text
                    sep.append(lc)
                    ln=Lines[lc-2]
                    if ln.isupper():
                        try:
                            exp['company']=ln.strip().split('|')[0]
                            exp['title']=ln.strip().split('|')[1]
                        except:
                            exp['company']=ln.strip()
                            exp['title']=exp['company']
                    elif ',' in line:
                        try:
                            words=line.split(',')
                            exp['company']=words[1]
                            exp['title']=words[2]
                        except:
                            pass
                    else:
                        exp['company']=Lines[lc-1].strip()
                        exp['title']=ln.strip()
                    try:
                        exp['startDate']=date.split('-')[0]
                        exp['endDate']=date.split('-')[1]
                        sum.append(exp)
                    except:
                        try:
                            exp['startDate']=line.split('–')[0]
                            exp['endDate']=line.split('–')[1]
                            sum.append(exp)
                        except:
                            pass
        num=len(sep)
        iter=list(zip(sep,sep[1:] + sep[:1]))
        counter=0
        for i in iter:
            lst=Lines[i[0]:i[1]]
            str=" ".join(lst)
            try:
                if len(lst)!=0:
                    sum[counter]['description']=str
                    counter+=1
            except:
                pass
        n=len(sum)
        if n==0:
            str="  ".join(Lines)
            exp=self.create_exp()
            exp['title']='ND'
            exp['company']='ND'
            exp['description']=str
            sum.append(exp)
        response['experiences']=sum
        return response

    def extract_skills(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the Skills section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,s2,s3,start,start2,start3=0,0,0,0,0,0,0
        end=len(Lines)
        end2=end
        end3=end2
        if sec_dict['sk']!=0:
            start=sec_dict['sk']
        if sec_dict['sw']!=0:
            start2=sec_dict['sw']
        if sec_dict['pro']!=0:
            start3=sec_dict['pro']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
            elif sec_dict[i]>start2 and s2==0:
                end2=sec_dict[i]
                s2=1
            elif sec_dict[i]>start3 and s3==0:
                end3=sec_dict[i]
                s3=1
        for line in Lines:
            lc+=1
            if lc in range(start+1,end) and start!=0:
                response['skills'].append(line.strip())
            elif lc in range(start2+1,end2) and start2!=0:
                response['skills'].append(line.strip())
            elif lc in range(start3+1,end3) and start3!=0:
                response['skills'].append(line.strip())
        return response

    def extract_projects(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the Projects section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc=0
        s=0
        start=0
        end=len(Lines)
        if sec_dict['projects']!=0:
            start=sec_dict['projects']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
                break
        for line in Lines:
            lc+=1
            if start!=0:
                if lc in range(start+1,end):
                    line=line.replace('\xa0',"")
                    line=line.replace('\x11',"")
                    response['projects'].append(line.strip())
        return response

    def create_pro(self):
        pdict={
        'title':"",
        'description':"",
        'date':""
        }
        return pdict

    def subsec_project(self,Lines,response):
        flag,lc,tp=0,0,0
        summ=[]
        m=[]
        for line in Lines:
            lc+=1
            line=line.strip()
            try:
                if line[0]=='•' or line[0]=='·':
                    tp+=1
                else:
                    if line[0].isupper():
                        pro=self.create_pro()
                        pro['title']=line
                        m.append(lc)
                        summ.append(pro)
                    else:
                        tp+=1
            except:
                tp+=1
        num=len(m)
        iter=list(zip(m,m[1:] + m[:1]))
        counter=0
        for i in iter:
            lst=Lines[i[0]:i[1]]
            str=" ".join(lst)
            try:
                if len(lst)!=0:
                    summ[counter]['description']=str
                    counter+=1
            except:
                tp+=1
        if len(summ)==0:
            str=" ".join(Lines)
            pro=self.create_pro()
            pro['title']='NA'
            pro['date']='NA'
            pro['description']=str
            summ.append(pro)
        response['projects']=summ
        return summ

    def extract_about(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the about section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,start=0,0,0
        end=len(Lines)
        if sec_dict['abt']!=0:
            start=sec_dict['abt']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
                break
        des=[]
        for line in Lines:
            lc+=1
            if start!=0:
                if lc in range(start+1,end):
                    des.append(line.strip())
        str=" ".join(des)
        str=str.replace('\xa0',"")
        str=str.replace('\x11',"")
        response['about'].append(str)
        return response

    def extract_achievements(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the Achievements section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,s2,start,start2=0,0,0,0,0
        end=len(Lines)
        end2=end
        if sec_dict['acc']!=0:
            start=sec_dict['acc']
        if sec_dict['fell']!=0:
            start2=sec_dict['fell']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
                break
            if sec_dict[i]>start2 and s2==0:
                end2=sec_dict[i]
                s2=1
                break
        for line in Lines:
            lc+=1
            if lc in range(start+1,end) and start!=0:
                line=line.replace('\xa0',"")
                line=line.replace('\x11',"")
                response['achievement'].append(line.strip())
            elif lc in range(start2+1,end2) and start2!=0:
                line=line.replace('\xa0',"")
                line=line.replace('\x11',"")
                response['achievement'].append(line.strip())
        return response

    def extract_awards(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the awards section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,start=0,0,0
        end=len(Lines)
        if sec_dict['aw']!=0:
            start=sec_dict['aw']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
                break
        for line in Lines:
            lc+=1
            if lc in range(start+1,end) and start!=0:
                line=line.replace('\xa0',"")
                line=line.replace('\x11',"")
                response['awards'].append(line.strip())
        return response

    def extract_research(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the Research work section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,start=0,0,0
        end=len(Lines)
        if sec_dict['res']!=0:
            start=sec_dict['res']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
                break
        for line in Lines:
            lc+=1
            if lc in range(start+1,end) and start!=0:
                line=line.replace('\xa0',"")
                line=line.replace('\x11',"")
                response['research_work'].append(line.strip())
        return response

    def extract_interests(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the Interests section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,start=0,0,0
        end=len(Lines)
        if sec_dict['ints']!=0:
            start=sec_dict['ints']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
                break
        for line in Lines:
            lc+=1
            if lc in range(start,end) and start!=0:
                line=line.replace('\xa0',"")
                line=line.replace('\x11',"")
                response['interests'].append(line.strip())
        return response

    def extract_softskills(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the Soft Skills section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,start=0,0,0
        end=len(Lines)
        if sec_dict['ss']!=0:
            start=sec_dict['ss']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
                break
        for line in Lines:
            lc+=1
            if lc in range(start+1,end) and start!=0:
                if len(line)!=0:
                    response['soft_skills'].append(line.strip())
        return response

    def extract_volwork(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the volunteer work section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,start=0,0,0
        end=len(Lines)
        if sec_dict['vw']!=0:
            start=sec_dict['vw']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
                break
        for line in Lines:
            lc+=1
            if lc in range(start+1,end) and start!=0:
                line=line.replace('\xa0',"")
                line=line.replace('\x11',"")
                response['volunteer_work'].append(line.strip())
        return response

    def extract_courses(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the Coursework section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,start=0,0,0
        end=len(Lines)
        if sec_dict['crs']!=0:
            start=sec_dict['crs']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
                break
        for line in Lines:
            lc+=1
            if lc in range(start+1,end) and start!=0:
                line=line.replace('\xa0',"")
                line=line.replace('\x11',"")
                response['relevant_courses'].append(line)
        return response

    def create_cert(self):
        cert={
        "title":"",
        "issuer":""
        }
        return cert

    def subsec_cert(self,Lines,response):
        sum=[]
        lc=0
        for line in Lines:
            lc+=1
            line1=line.lower()
            if lc>1:
                if 'from' in line1:
                    try:
                        cert=self.create_cert()
                        cert['title']=line1.split('from')[0].strip()
                        cert['issuer']=line1.split('from')[1].strip()
                        sum.append(cert)
                    except:
                        pass
                elif 'by' in line1:
                    try:
                        cert=self.create_cert()
                        cert['title']=line.split('by')[0].strip()
                        cert['issuer']=line.split('by')[1]
                        sum.append(cert)
                    except:
                        pass
                else:
                    line2=line.strip()
                    words=line.split()
                    num=len(words)
                    if num>1 and (line2[0].isupper() or line2[1].isupper() or line2[2].isupper()):
                        cert=self.create_cert()
                        cert['title']=line.strip()
                        cert['issuer']='NA'
                        sum.append(cert)
        if len(sum)!=0:
            response['relevant_courses']=sum
        return response

    def extract_activities(self,Lines,sec_dict,response):
        '''
        Making use of the my_dictionary object, this
        function extracts the Activities section of a given resume.
        It utilises the sorted values in the Ordered dictionary to
        find a start and end marker for this section.
        '''
        lc,s,start=0,0,0
        end=len(Lines)
        if sec_dict['acts']!=0:
            start=sec_dict['acts']
        for i in sorted(sec_dict, key=sec_dict.get, reverse=False):
            if sec_dict[i]>start and s==0:
                end=sec_dict[i]
                s=1
                break
        for line in Lines:
            lc+=1
            if lc in range(start+1,end) and start!=0:
                line=line.replace('\xa0',"")
                line=line.replace('\x11',"")
                response['activities'].append(line.strip())
        return response

    def extract_info(self,f,Lines,sec_dict):
        '''
        This defines the structure of the response
        object which stores the result and encapsulates
        the function calls to all modularized functions.
        '''
        response ={
        'name':'',
        'email':'NA',
        'phone_number':'NA',
        'about':[],
        'education':[],
        'experiences':[],
        'skills':[],
        'projects':[],
        'achievement':[],
        'awards':[],
        'research_work':[],
        'interests':[],
        'soft_skills':[],
        'volunteer_work':[],
        'relevant_courses':[],
        'activities':[]
        }
        self.extract_basic(f,response)
        self.extract_edu(Lines,sec_dict,response)
        self.subsec_edu(response['education'],response)
        self.extract_exp(Lines,sec_dict,response)
        self.subsec_exp(response['experiences'],response)
        self.extract_skills(Lines,sec_dict,response)
        self.extract_projects(Lines,sec_dict,response)
        self.subsec_project(response['projects'],response)
        self.extract_about(Lines,sec_dict,response)
        self.extract_awards(Lines,sec_dict,response)
        self.extract_achievements(Lines,sec_dict,response)
        self.extract_research(Lines,sec_dict,response)
        self.extract_interests(Lines,sec_dict,response)
        self.extract_softskills(Lines,sec_dict,response)
        fin_skills=response['skills']+response['soft_skills']
        response['skills']=fin_skills
        self.extract_volwork(Lines,sec_dict,response)
        self.extract_courses(Lines,sec_dict,response)
        self.subsec_cert(response['relevant_courses'],response)
        self.extract_activities(Lines,sec_dict,response)
        return response

    def read_file(self,f):
        str=f.getvalue()
        Lines=str.splitlines()
        return Lines

    def parse_resume(self,f,ext):
        '''
        This encapsulates the functionality of the
        entire above code and uses the encapsulated
        functions to parse a resume.
        '''
        PDF=self.convert_pdf(f)
        split=self.is_sec(PDF)
        if split==True:
            Lines=self.sep_section(PDF)
        else:
            Lines=self.read_file(PDF)
        sec_dict=self.find_and_sort(PDF,Lines)
        resp=self.extract_info(PDF,Lines,sec_dict)
        print(resp)
        if len(resp['education'])==0 or len(resp['experiences'])==0:
            print('\n')
            print('Sorry, it looks like we are having trouble reading your resume. Consider making your profile manually.')
        elif len(resp['skills'])==0:
            print('\n')
            print('Hmmm something seems wrong. Consider uploading your skills manually.')
        return resp
