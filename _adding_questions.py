import ast
import json
from langchain.chat_models import ChatOpenAI
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.llms import Cohere


def is_valid_json(json_string):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError:
        return False            
    
    
def update_double_quote(llm_response):
    if is_valid_json(llm_response):
        llm_response = json.loads(llm_response)
        return llm_response
    else:
        parsed_dict = ast.literal_eval(llm_response)
        return parsed_dict


def extract_generation_text(json_string):
    try:
        data = json.loads(json_string)
        if 'generations' in data:
            generations = data['generations']
            if generations:
                generation_info = generations[0]
                if generation_info and isinstance(generation_info, list):
                    for item in generation_info:
                        if 'text' in item:
                            return item['text']
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except (KeyError, IndexError) as e:
        print(f"Key error or index error: {e}")

    return None


def llm_chat_prompt(
        provider: str,
        api_key: str = "",
        api_base: str = "",
        api_version: str = "",
        model_name: str = "gpt-3.5-turbo", 
        temperature: int = 0,
        prompt_messages: list = [],
        prompt_variables: dict = {},
        max_tokens: int = 2048
    ):

    # we'll need to convert the prompt_messages dict to an array of tuples
    prompt_tuples = [(role, message) for entry in prompt_messages for role, message in entry.items()]
    template = ChatPromptTemplate.from_messages(prompt_tuples)
    llm = None
    
    # OPENAI
    if provider == "openai":   
        llm = ChatOpenAI(
            temperature = temperature,
            model_name=model_name,
            openai_api_key = api_key,
            max_tokens = max_tokens
        )
        
        if llm:
            messages = template.format_messages(**prompt_variables)
            message = llm(messages)
            if(message):
                return message.content
            
    # AZURE OPENAI        
    if provider == "azureopenai":   

        llm = AzureChatOpenAI(
            temperature = temperature,
            openai_api_version = api_version,
            openai_api_key = api_key,
            openai_api_base = api_base,
            deployment_name = model_name
        )
        
        if llm:
            messages = template.format_messages(**prompt_variables)
            message = llm(messages)
            if(message):
                return message.content
    
    # COHERE
    if provider == "cohere":
        llm = Cohere(
            temperature = temperature,
            model = model_name,
            cohere_api_key=api_key
        )
                
        if llm:
            messages = template.format(**prompt_variables)
            generations = llm.generate([messages])
            if(generations):
                result = generations.json()
                message = extract_generation_text(result)
                if message:
                    return message
    return None




def add_question(
        num = 0,
        lis = [],
        lis2 = [],
        data = [],
        n=0,
        file_path = "zexample.json"
    ):
    lis = []
    dic = {}


    for name in data:
        nn = 0
        for d in data[name]:
            nn +=1
            # summarize 
            if len(d['text']) > 1000:
                print("Creating Summary...")
                            
                m=[{"system": "review the 'CONTEXT': '{content}'. You objective is to summarize and return the main points in bollet points."}]
                v={"content": d['text']}


                oo= llm_chat_prompt(
                    provider=provider,
                    model_name=model_name,
                    api_base=api_base,
                    api_key=api_key,
                    api_version=api_version,
                    temperature=0,
                    prompt_messages=m,
                    prompt_variables=v
                )
                print("length: "+str(len(oo))+" "+" summary: "+ oo)
                d['text'] = oo 

            # fix vocabulary
            print("Fixing Vocabulary...")
            m=[{"system": "review the 'CONTEXT': '{content}'. You objective is to correct all grammer errors, remove space and symbols. Return a json object with the same structure."}]
            v={"content": d}

            gram= llm_chat_prompt(
                provider=provider,
                model_name=model_name,
                api_base=api_base,
                api_key=api_key,
                api_version=api_version,
                temperature=0,
                prompt_messages=m,
                prompt_variables=v
            )
            
            print("Creating Questions...")
            
            # add questions 
            m=[{"system": "review and ask a list of questions related to the 'CONTEXT': '{content}'. You objective is to create a list of 'questions' for the answers in the 'CONTEXT'. Questions must be specific and don't mention in your question that i provided the context. return json object containing 'questions'."}]
            v={"content": d}

            oo= llm_chat_prompt(
                provider=provider,
                model_name=model_name,
                api_base=api_base,
                api_key=api_key,
                api_version=api_version,
                temperature=0,
                prompt_messages=m,
                prompt_variables=v
            )

            try:
                print("Checking Data...")
                dicc = update_double_quote(gram)
                ques = update_double_quote(oo)
                dicc['questions'] = ques['questions']
                lis.append(dicc)
                
                print("Dumping Data...")
                with open(file_path, 'r') as file:
                    data2 = json.load(file)
                    if type(data2) != dict: data2 = {}
                    if name not in data2: data2[name]=lis 
                    else: data2[name].append(dicc)
                
                with open(file_path, "w") as json_file:
                    json.dump(data2, json_file, indent=4)

            except:
                print("Error!!!")
                print("Complete: "+str(nn -1)+ "   Total: "+ str(len(data[name]))+ "  Name: "+ name)

                with open(file_path, 'r') as file:
                    data2 = json.load(file)
                    if type(data2) != dict: data2 = {}
                    if name not in data2: data2[name]=lis 
                    else: data2[name].extend(lis)
                    
                with open(file_path, "w") as json_file:
                    json.dump(data2, json_file, indent=4)

                break
            print("\nComplete: "+str(nn)+ "   Total: "+ str(len(data[name]))+ "  Name: "+ name)

        dic[name]=lis
        lis = []

    if dic:            
        # Write to the JSON file
        with open(file_path, "w") as json_file:
            json.dump(dic, json_file, indent=4)





# llm
provider= "azureopenai"
model_name= "gpt-35-short"
api_key= ""
api_base= "https://gpt-4-east2-launch.openai.azure.com"
api_version= "2023-07-01-preview"



json_example_path = "zexample.json"
json_page_path = 'zpage.json'


with open(json_page_path, 'r') as file:
    data = json.load(file)

add_question(data=data, file_path=json_example_path)


