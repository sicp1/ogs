from flask import Flask,request, jsonify
import configparser
from openai import OpenAI
import os
import json

app = Flask(__name__)
setup_config = configparser.ConfigParser()
setup_config.read('setup.ini')
client = OpenAI(api_key="<deepseek api key>", base_url=f"http://localhost:{setup_config['LLM']['port']}")

class config:

    def __init__(self):
        self.system=""
        self.temperature=""
        self.llm_configs=[]
        self.llm_configs_fresh()
    
    def llm_configs_fresh(self):
        self.llm_configs=os.listdir("./configs")
    
    def config_list(self):
        self.llm_configs_fresh()
        return [{"name":item,"id":index} for index,item in enumerate(self.llm_configs)]
    
    def read(self,id):
        llm_config=configparser.ConfigParser()
        llm_config.read(f"./configs/{self.llm_configs[id]}")

        self.system=llm_config['DEFAULT']['system']
        self.temperature=llm_config['DEFAULT']['temperature']
        return {
            "system":self.system,
            "temperature":self.temperature
        }
    
    def write(self,id,data):
        llm_config=configparser.ConfigParser()
        path=f"./configs/{self.llm_configs[id]}"
        llm_config.read(path)
        llm_config.set("DEFAULT","system",data['system'])
        llm_config.set("DEFAULT","temperature",str(data['temperature']))
        with open(path,"w") as configfile:
            llm_config.write(configfile)
        return "success"
        



# 读取INI文件


@app.route('/test_chat',methods=['POST'])
def test_chat():
    data=request.get_json()
    prompt=data.get("prompt")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": f"{prompt}"},
        ],
        stream=False 
    )
    return response.choices[0].message.content

@app.route("/config_list",methods=['POST'])
def config_list():
    config_tmp=config()
    return json.dumps(config_tmp.config_list())
    
    


@app.route("/config_change",methods=['POST'])
def config_change():
    config_tmp=config()
    data=request.get_json()
    id=data.get("id")
    change_data=data.get("data")
    print(change_data)
    return config_tmp.write(id,change_data)





@app.route("/config_show",methods=['POST'])
def config_show():
    data=request.get_json()
    id=data.get("id")
    config_tmp=config()
    show=config_tmp.read(id)
    return json.dumps(show)



@app.route("/chat",methods=['POST'])
def chat():
    data=request.get_json()
    id=data.get("id")
    messages=data.get("messages")
    config_tmp=config()
    llm_config=config_tmp.read(id)
    messages.insert(0,{"role": "system", "content":llm_config['system']})
    print("messages:",messages)
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False,
        temperature=llm_config['temperature']
    )
    return  response.choices[0].message.content






if __name__ == '__main__':
    app.run(debug=False,port=setup_config['LOCAL']['port'],host="0.0.0.0")