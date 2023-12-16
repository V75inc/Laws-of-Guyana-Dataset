from langchain.document_loaders import PyPDFLoader
import re
import string
import json




def extract_law(
    pdf_location="",
    section_content=[], 
    invalid_list=[], 
    filtered_list=[], 
    pdf_id="", 
    title="",
    category="",
    page_start=0,
    page_stop=0,
    output="",
    override_list=[],
    invalid3=[]
    ):


    invalid_list.extend(section_content)
    structured_data=[]

    page_number = page_start
    pag = []
    if page_start != 0: page_start = page_start - 1

    # patterns 
    find_pattern_space_dot = r'\b\d+(?:[A-Za-z]{1,2})?\s?\.\B'
    split_pattern_space_dot = r'(\b\d+(?:[A-Za-z]{1,2})?\s?\.\B)'

    # open pages 
    with open('pdf_text.json', 'r') as file:
        pages = json.load(file)

    # add content to pages 
    if not pages:

        loader = PyPDFLoader(pdf_location)
        pages = loader.load_and_split()
        for page_num in range(page_start, page_stop):
            print(page_num)
            pag.append(pages[page_num].page_content)

        with open('pdf_text.json', "w") as json_file:
            json.dump(pag, json_file, indent=4)


        with open('pdf_text.json', 'r') as file:
                pages = json.load(file)

    # add pages by range 
    for page_num in range(page_start, page_stop):
        pag.append(pages[page_num])


    alphabet_letters = list(string.ascii_uppercase)
    alphabet_letters.insert(0, '')
    structured_data = []
    letter_count = 0
    abc_num = 0

    for ll in pag:
        content=""
        can_skip = True

        # remove and split
        ll=ll.replace("\n", "")

        ww= ll.split('   ')
        # ww= ll.split(' \n')


        for i in ww:
            for invalid in filtered_list:
                if invalid in i:
                    can_skip = True
                    break

            if re.findall(find_pattern_space_dot , i):
                can_skip = False

            if not can_skip:
                ii = re.sub('\s+', ' ', i).strip()
                content=content + ii

        result = re.split(split_pattern_space_dot, content)
        idxx = 0
        result2 = []
        for i in range(len(result)):
            if re.findall(find_pattern_space_dot, result[i]):
                print("error: "+result[i])
                if result[i].strip() not in invalid3:
                    idxx = int(re.sub(r'[a-zA-Z.]', "", result[i]))

            if re.findall(r'\b\d{4}\.\B', result[i]) or result[i] in override_list or int(idxx) > len(section_content):
                if result2 == []: result2.append(result[i])
                else:
                    result2[-1] += result[i]
            else:
                if re.findall(find_pattern_space_dot, result[i]) and ' ' in result[i]:
                    res = result[i].replace(" ", "")
                    result2.append(res)
                else:
                    result2.append(result[i])

        letter = False
        
        for i in result2:
            if re.findall(find_pattern_space_dot, i) and ' ' not in i:
                if re.findall(r'[a-zA-Z]', i):
                    idx= int(re.sub(r'[a-zA-Z.]', "", i))
                    letter_count += 1
                    abc_num +=1
                    letter = True
                elif  re.findall(r'\b\d+\.', i):
                    idx = int(i.replace(".",""))    
                    letter = False
                    abc_num = 0
                if letter:
                    if abc_num >= 26: 
                        new_abc_num = abc_num - 26 
                        cat = category + " " + str(idx) + alphabet_letters[new_abc_num]+alphabet_letters[new_abc_num]
                    else:
                        cat = category + " " + str(idx) + alphabet_letters[abc_num]
                    section_name = section_content[idx + letter_count]
                    print("\nAddingg: " + cat + "   " + section_name)
                else:
                    cat = category + " " + str(idx)
                    section_name = section_content[idx + letter_count]
                    print("\nAdding: " + cat + "   " + section_name)

                ol={
                    "title": title,
                    "category": cat,
                    "name": section_name,
                    "text": "",
                    "source": "https://drive.google.com/uc?export=view&id="+ pdf_id +"#page=" + str(page_number)
                }
                
                structured_data.append(ol)
                
            elif structured_data:
                if len(structured_data) == 0: structured_data.append({})
                for titlee in section_content:
                    if titlee in i and  titlee != "":
                        print("removing: "+ titlee)
                        i = i.replace(titlee, "")
                        break
                structured_data[-1]["text"] += "" + i
                skipp = False
                print("updating...")
            


        page_number += 1

    with open(output, "w") as json_file:
        json.dump(structured_data, json_file, indent=4)




section_content = []


invalid_list = [
    " ",
    "",
    "LAW OF GUYANA",
    'LAWS OF GUYANALAWS OF GUYANA'
    # "LAWS OF GUYANAConstitution"
    
]

filtered_list = [
    'LAWS OF GUYANA 62 Cap. 1:01 Constitution of the Co-operative Republic of Guyana L.R.O. 1/2012',
    'LAWS OF GUYANA page_number_ Cap. 1:01 Constitution of the Co-operative Republic of Guyana L.R.O. 1/2012',
    'Constitution of the Co-operative Republic of Guyana Cap. 1:01 page_plus_one L.R.O. 1/2012',
    '[Subs idiary] Constitu tion of the Orders of Gu yana L.R.O. 1/2012 ',
    'LAWS OF GUYANA page_plus_one Cap. 1:01 Constitution of the Co-operative Republic of Guyana',
    'Constitution of the Co-operative Republic of Guyana Cap. 1:01 page_plus_one',
    'Constitution of the Co-operative Republic of Guyana Cap. 1:01 page_plus_one [Subs idiary] Constitu tion of the Orders of Gu yana L.R.O. 1/2012'
    # 'L.R.O. 1/2012',
    # 'Cap. 1:01',
    'LAWS OF GUYANA',
    # 'rule 30 or 31.'
    # "LAWS OF GUYANAConstitution"
]




# fixed 
json_example_path = "zexample.json"
json_page_path = 'zpage.json'

category="Article"

title = "PUBLIC SERVICE COMMISSION RULES"

dd = extract_law(
    pdf_location="content/Chapter 001:01/Cap.101 Constitution_0.pdf",
    section_content=section_content, 
    invalid_list=invalid_list, 
    filtered_list=filtered_list, 
    pdf_id="1T0RhAMjvwVP0rcegwZTc19T6J28eNAha", 
    title=title,
    category=category,
    page_start= 348,
    page_stop= 376,
    output=json_page_path,
    override_list=[], #['29.'],
    invalid3=[] # ['The Commission shall determine the seniority of the officer in any case not covered by rule 30 or 31.']
)
