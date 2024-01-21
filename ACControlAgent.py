import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from spade.template import Template
import random
from json import loads, dumps

WAITING_MESSAGE = "WAITING_MESSAGE"
SENDING_MESSAGE = "SENDING_MESSAGE"

HEATING_HIGH = "HEATING_HIGH"
HEATING_LOW = "HEATING_LOW"
COOLING_HIGH = "COOLING_HIGH"
COOLING_LOW = "COOLING_LOW"
DEHAZING = "DEHAZING"
DISABLED = "DISABLED"

class FSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"[ACControlAgent] Pokrenut. Stanje: {self.current_state}")

    async def on_end(self):
        print(f"[ACControlAgent] zavrsio. Stanje: {self.current_state}")
        await self.agent.stop()

class WaitingMessage(State):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            if msg.metadata.get("performative") == "inform" and msg.metadata.get("ontology") == "heating":
                msg_content = loads(msg.body)
                if 'agent_id' in msg_content and msg_content['agent_id'].lower() == "roadvisibilityagent"+"@localhost":
                    print(f"[ACControlAgent] Primljena poruka od *{msg_content['agent_id']}* sa sadržajem: {msg.body}")
                    rain_level = int(msg_content['rain_level'])
                    inside_temp_reading = int(msg_content['inside_temp'])
                    outside_temp_reading = int(msg_content['outside_temp'])
                    temp_difference = abs(outside_temp_reading - inside_temp_reading)
                    
                    if inside_temp_reading > 25 and rain_level == 0:
                        self.agent.status = "COOLING_HIGH"  
                    elif inside_temp_reading > 25 and rain_level > 0:
                        self.agent.status = "COOLING_LOW"  
                    elif inside_temp_reading < 15:
                        self.agent.status = "HEATING_HIGH"  
                    elif 15 < inside_temp_reading <= 22:
                        self.agent.status = "HEATING_LOW"
                    elif temp_difference > 5 and rain_level > 0:
                        self.agent.status = "DEHAZING"
                    else:
                        self.agent.status = "DISABLED"
                    
                    
                    #Replying to the received message
                    reply = msg.make_reply()
                    msg_content = {
                        "agent_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
                        "status": f"{self.agent.status}" if hasattr(self.agent, 'status') else -999
                    }
                    reply.body = dumps(msg_content)
                    await self.send(reply)
                    
                    
                    
                
            self.set_next_state(WAITING_MESSAGE)
        else:
            print("[ACControlAgent] No messages. Staying in the Disabled state.")
            self.set_next_state(WAITING_MESSAGE)


class ACControlAgent(Agent):
    async def setup(self):
        template = Template()
        template.set_metadata("performative", "inform")
        fsm = FSMBehaviour()
        fsm.add_state(name=WAITING_MESSAGE, state=WaitingMessage(), initial=True)
        self.status = DISABLED
        
        #"Recursive" transitions
        fsm.add_transition(source=WAITING_MESSAGE, dest=WAITING_MESSAGE)

        self.add_behaviour(fsm)
    
if __name__ == "__main__":
    agent = ACControlAgent("ACControlAgent@localhost", "tajna")
    agent.start()
    agent.wait()  
