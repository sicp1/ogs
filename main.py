from flask import Flask,request, jsonify
import configparser
from openai import OpenAI
import os
import json

app = Flask(__name__)
config = configparser.ConfigParser()
config.read('setup.ini')
llm_configs=[]
client = OpenAI(api_key="<deepseek api key>", base_url=f"http://localhost:{config['LLM']['port']}")

# 读取INI文件

def llm_configs_fresh():
    global llm_configs
    llm_configs=os.listdir("./configs")


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
    return  json.dumps([{"name":item,"id":index} for index,item in enumerate(llm_configs)])


@app.route("/chat",methods=['POST'])
def chat():
    data=request.get_json()
    id=data.get("id")
    prompt=data.get("prompt")
    llm_config = configparser.ConfigParser()
    llm_config.read(f"./configs/{llm_configs[id]}")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": llm_config['DEFAULT']['system']},
            {"role": "user", "content": f"{prompt}"},
        ],
        stream=False,
        temperature=llm_config['DEFAULT']['temperature']
    )
    return  response.choices[0].message.content






if __name__ == '__main__':
    llm_configs_fresh()
    app.run(debug=False,port=config['LOCAL']['port'])