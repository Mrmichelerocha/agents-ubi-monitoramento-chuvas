from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model
from uagents.resolver import RulesBasedResolver
import urllib.request
import requests


TEMPERATURE_ADDRESS = "agent1qwmrvl8w0aduvgh95fdya4nsnkqnax7pu553mra3y8nx2u95cwrsz2zwtvx"
UMIDITY_ADDRESS = " agent1qf5u9l6mcc92fggaxtr3hpkqcw2gqnc55pljphl728lhgehz8lpazq5eygv"
PLUVIOMETER_ADDRESS = "agent1q02gfx2na4ednrkvclwwsdm6dr0wspddy5w8rp22jh4tflghpptlyynmnr0"
ANEMOMETER_ADDRESS = "agent1qf98zrr8r2syt7v8j3vfduvap355tm4x424ctzqnwu4tr5krte9j6fsvnus"


pluv = Agent(
    name="pluv",
    port=8022,
    seed="pluv secret phrase",
    resolve=RulesBasedResolver(
        {
            TEMPERATURE_ADDRESS: "http://127.0.0.1:8020/submit",
            UMIDITY_ADDRESS: "http://127.0.0.1:8021/submit",
            PLUVIOMETER_ADDRESS: "http://127.0.0.1:8022/submit",
            ANEMOMETER_ADDRESS: "http://127.0.0.1:8023/submit",
        }
    ),
)

fund_agent_if_low(pluv.wallet.address())


class Message(Model):
    message: str
    data: int
    
class House_env():        
    def update_perception(ctx: Context):
        # Sobe 'crença' | atualiza dado
        if(House_data_pluv.checked_pluv):
            data = {"pluv_status": House_data_pluv.status,}  
            ctx.storage.set('desire_pluv', data)
    
class House_data_pluv():
    aux = 0    
    status = None
    checked_pluv = None
        
    def checked_data(ctx: Context):
        # Entra 'banco' pega status da pluv 
        url = "http://192.168.0.111/pluv"
        response = requests.get(url)
        
        if response.status_code == 200:
            highest_id = 0
            House_data_pluv.status = 0.0
            
            data = response.json()
            for item in data["pluv_dict"]:
                if item["id"] >= highest_id:
                    highest_id = item["id"]
                    House_data_pluv.status = item["pluv_status"]
                    House_data_pluv.brain_post()

            print("Highest ID:", highest_id)
            print(House_data_pluv.status)
            House_data_pluv.checked_pluv = True
            House_env.update_perception(ctx)
            print(House_data_pluv.checked_pluv)
        else:
            print("Falha ao fazer a solicitação.") 
            
    def brain_post():
        print("adiciono status ao meu cerebro")
        url = "http://127.0.0.1:8000/datapluv/"
        
        if House_data_pluv.status != House_data_pluv.aux:
            data = {
                "status": House_data_pluv.status,
            }
            response = requests.post(url, data)
            House_data_pluv.aux = House_data_pluv.status

            if response.status_code == 201:
                print("Post bem-sucedido!")
            else:
                print("Post falhou.")
        else:
            pass
        

@pluv.on_interval(period=30.5)
async def waiting_status(ctx: Context):
    House_data_pluv.checked_data(ctx)
    if(House_data_pluv.checked_pluv):
        pass
        # data = ctx.storage.get('desire_pluv')
        # msg = Message(message=f'waiting_pluv_status', data=data['pluv_status'])
        # await ctx.send(DECISION_ADDRESS, msg)        


if __name__ == "__main__":
    pluv.run()
