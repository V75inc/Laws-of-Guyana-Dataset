



import json
import re
import string




def extract_law(
    pdf_location="",
    section_content=[], 
    invalid_list=[], 
    filtered_list="", 
    pdf_id="", 
    title="",
    category="",
    page_start=0,
    page_stop=0,
    output="",
    override_list=[]
    ):


    invalid_list.extend(section_content)
    structured_data=[]

    page_number = page_start
    pag = []
    if page_start != 0: page_start = page_start - 1

    with open('pdf_text.json', 'r') as file:
            pages = json.load(file)
            # data.extend(oo)

    for page_num in range(page_start, page_stop):
        # print(page_num)
        pag.append(pages[page_num])


    abc_num = 0
    prev_number = 0
    cont_num = 0
    abc_num = 0
    letter_count = 0
    alphabet_letters = list(string.ascii_uppercase)
    alphabet_letters.insert(0, '')
    skipp = False
    structured_data = []

    n = 0
    cont = [""]
    find_pattern_space_dot = r'\b\d+(?:[A-Za-z]{1,2})?\s?\.\B'
    split_pattern_space_dot = r'(\b\d+(?:[A-Za-z]{1,2})?\s?\.\B)'

    for ll in pag:
        # print("\n\npag")
        # remove \n 
        # print(ll)
        # ll=ll.replace(" \n", "")
        
        # ww= ll.split('   ')
        ww= ll.split('\n')
        content=""
        check_cont = False

        for i in ww:
            # if len(i) < 100 and i.endswith("."):
            #     cont.append(i.strip())
            if check_cont:
                # print(cont[-1]+" "+ i.strip())
                cont[-1] = cont[-1]+" "+ i.strip()
                check_cont = False
                print(cont[-1])

            if re.findall(find_pattern_space_dot, i):
                result = re.split(split_pattern_space_dot, i)
                # print("new: "+result[2].strip())
                cont.append(result[2].strip())
                if not result[2].strip().endswith('.'):
                    check_cont = True
                elif result[2].strip().endswith('.'):
                    print(result[2].strip())
                     
            


    with open("cont.json", "w") as json_file:
        json.dump(cont, json_file, indent=4)




section_content = []

invalid_list = []

filtered_list = []

title = ""

category=""


# fixed 
json_example_path = "zexample.json"
json_page_path = 'zpage.json'




dd = extract_law(
    pdf_location="content/Chapter 001:01/Cap.101 Constitution_0.pdf",
    section_content=section_content, 
    invalid_list=invalid_list, 
    filtered_list=filtered_list, 
    pdf_id="1T0RhAMjvwVP0rcegwZTc19T6J28eNAha", 
    title=title,
    category=category,
    page_start= 343,
    page_stop= 347,
    output=json_page_path,
    override_list=[]
)
