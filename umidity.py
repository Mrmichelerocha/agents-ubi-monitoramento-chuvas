from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model
from uagents.resolver import RulesBasedResolver
import urllib.request
import requests


TEMPERATURE_ADDRESS = "agent1qwmrvl8w0aduvgh95fdya4nsnkqnax7pu553mra3y8nx2u95cwrsz2zwtvx"
UMIDITY_ADDRESS = " agent1qf5u9l6mcc92fggaxtr3hpkqcw2gqnc55pljphl728lhgehz8lpazq5eygv"
PLUVIOMETER_ADDRESS = "agent1q02gfx2na4ednrkvclwwsdm6dr0wspddy5w8rp22jh4tflghpptlyynmnr0"
ANEMOMETER_ADDRESS = "agent1qf98zrr8r2syt7v8j3vfduvap355tm4x424ctzqnwu4tr5krte9j6fsvnus"


umid = Agent(
    name="umid",
    port=8021,
    seed="umid secret phrase",
    resolve=RulesBasedResolver(
        {
            TEMPERATURE_ADDRESS: "http://127.0.0.1:8020/submit",
            UMIDITY_ADDRESS: "http://127.0.0.1:8021/submit",
            PLUVIOMETER_ADDRESS: "http://127.0.0.1:8022/submit",
            ANEMOMETER_ADDRESS: "http://127.0.0.1:8023/submit",
        }
    ),
)

fund_agent_if_low(umid.wallet.address())


class Message(Model):
    message: str
    data: int
    
class House_env():        
    def update_perception(ctx: Context):
        # Sobe 'crença' | atualiza dado
        if(House_data_umid.checked_umid):
            data = {"umid_status": House_data_umid.status,}  
            ctx.storage.set('desire_umid', data)
    
class House_data_umid():
    aux = 0    
    status = None
    checked_umid = None
        
    def checked_data(ctx: Context):
        # Entra 'banco' pega status da umid 
        url = "http://192.168.18.8/umi"
        response = requests.get(url)
        
        if response.status_code == 200:
            highest_id = 0
            House_data_umid.status = 0.0
            
            data = response.json()
            for item in data["umi_dict"]:
                if item["id"] >= highest_id:
                    highest_id = item["id"]
                    House_data_umid.status = item["umi_status"]
                    House_data_umid.brain_post()

            print("Highest ID:", highest_id)
            print(House_data_umid.status)
            House_data_umid.checked_umid = True
            House_env.update_perception(ctx)
            print(House_data_umid.checked_umid)
        else:
            print("Falha ao fazer a solicitação.") 
            
    def brain_post():
        print("adiciono status ao meu cerebro")
        url = "http://127.0.0.1:8000/dataumid/"
        
        if House_data_umid.status != House_data_umid.aux:
            data = {
                "status": House_data_umid.status,
            }
            response = requests.post(url, data)
            House_data_umid.aux = House_data_umid.status

            if response.status_code == 201:
                print("Post bem-sucedido!")
            else:
                print("Post falhou.")
        else:
            pass
        

@umid.on_interval(period=30.5)
async def waiting_status(ctx: Context):
    House_data_umid.checked_data(ctx)
    if(House_data_umid.checked_umid):
        pass
        # data = ctx.storage.get('desire_umid')
        # msg = Message(message=f'waiting_umid_status', data=data['umid_status'])
        # await ctx.send(DECISION_ADDRESS, msg)        


if __name__ == "__main__":
    umid.run()
