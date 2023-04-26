from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model
from uagents.resolver import RulesBasedResolver
import urllib.request
import requests


TEMPERATURE_ADDRESS = "agent1qwmrvl8w0aduvgh95fdya4nsnkqnax7pu553mra3y8nx2u95cwrsz2zwtvx"
UMIDITY_ADDRESS = " agent1qf5u9l6mcc92fggaxtr3hpkqcw2gqnc55pljphl728lhgehz8lpazq5eygv"
PLUVIOMETER_ADDRESS = "agent1q02gfx2na4ednrkvclwwsdm6dr0wspddy5w8rp22jh4tflghpptlyynmnr0"
ANEMOMETER_ADDRESS = "agent1qf98zrr8r2syt7v8j3vfduvap355tm4x424ctzqnwu4tr5krte9j6fsvnus"


temp = Agent(
    name="temp",
    port=8020,
    seed="temp secret phrase",
    resolve=RulesBasedResolver(
        {
            TEMPERATURE_ADDRESS: "http://127.0.0.1:8020/submit",
            UMIDITY_ADDRESS: "http://127.0.0.1:8021/submit",
            PLUVIOMETER_ADDRESS: "http://127.0.0.1:8022/submit",
            ANEMOMETER_ADDRESS: "http://127.0.0.1:8023/submit",
        }
    ),
)

fund_agent_if_low(temp.wallet.address())


class Message(Model):
    message: str
    data: int
    
class House_env():        
    def update_perception(ctx: Context):
        # Sobe 'crença' | atualiza dado
        if(House_data_temp.checked_temp):
            data = {"temp_status": House_data_temp.status,}  
            ctx.storage.set('desire_temp', data)
    
class House_data_temp():
    aux = 0    
    status = None
    checked_temp = None
        
    def checked_data(ctx: Context):
        # Entra 'banco' pega status da temp 
        url = "http://192.168.18.8/temp"
        response = requests.get(url)
        
        if response.status_code == 200:
            highest_id = 0
            House_data_temp.status = 0.0
            
            data = response.json()
            for item in data["temp_dict"]:
                if item["id"] >= highest_id:
                    highest_id = item["id"]
                    House_data_temp.status = item["temp_status"]
                    House_data_temp.brain_post()

            print("Highest ID:", highest_id)
            print(House_data_temp.status)
            House_data_temp.checked_temp = True
            House_env.update_perception(ctx)
            print(House_data_temp.checked_temp)
        else:
            print("Falha ao fazer a solicitação.") 
            
    def brain_post():
        print("adiciono status ao meu cerebro")
        url = "http://127.0.0.1:8000/datatemp/"
        
        if House_data_temp.status != House_data_temp.aux:
            data = {
                "status": House_data_temp.status,
            }
            response = requests.post(url, data)
            House_data_temp.aux = House_data_temp.status

            if response.status_code == 201:
                print("Post bem-sucedido!")
            else:
                print("Post falhou.")
        else:
            pass
        

@temp.on_interval(period=30.5)
async def waiting_status(ctx: Context):
    House_data_temp.checked_data(ctx)
    if(House_data_temp.checked_temp):
        pass
        # data = ctx.storage.get('desire_temp')
        # msg = Message(message=f'waiting_temp_status', data=data['temp_status'])
        # await ctx.send(DECISION_ADDRESS, msg)        


if __name__ == "__main__":
    temp.run()
