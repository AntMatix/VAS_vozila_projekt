import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from spade.template import Template
import random
from json import loads, dumps

WAITING_MESSAGE = "WAITING_MESSAGE"
SENDING_MESSAGE = "SENDING_MESSAGE"

class FSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"[CentralAgent] Pokrenut. Stanje: {self.current_state}")

    async def on_end(self):
        print(f"[CentralAgent] zavrsio. Stanje: {self.current_state}")
        await self.agent.stop()

class WaitingMessage(State):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            if msg.metadata.get("performative") == "inform" and msg.metadata.get("ontology") == "central_agent_update":
                msg_content = loads(msg.body)
                ##Message recieved from RoadVisibilityAgent
                if 'agent_id' in msg_content and msg_content['agent_id'].lower() == "roadvisibilityagent"+"@localhost":
                    print(f"[CentralAgent] Primljena poruka od *{msg_content['agent_id']}* sa sadržajem: {msg.body}")
                    self.agent.headlights_status = msg_content['headlights_status']
                    self.agent.wipers_status = msg_content['wipers_status']
                    self.agent.ac_status = msg_content['ac_status']
                    self.agent.rain_level = msg_content['rain_level']
                    self.agent.luminosity_level = msg_content['luminosity_level']
                    self.agent.outside_temp = msg_content['outside_temp']
                    self.agent.inside_temp = msg_content['inside_temp']
                    self.agent.speed = msg_content['speed']
                    self.set_next_state(SENDING_MESSAGE) 
                    return
                ##Message recieved from DrivingAssistanceAgent
                if 'agent_id' in msg_content and msg_content['agent_id'].lower() == "drivingassistanceagent"+"@localhost":
                    print(f"[CentralAgent] Primljena poruka od *{msg_content['agent_id']}* sa sadržajem: {msg.body}")
                    self.agent.esp_status = msg_content['esp_status']
                    self.agent.traction_control_status = msg_content['traction_control_status']
                    self.agent.speed = msg_content['speed']
                    self.set_next_state(SENDING_MESSAGE) 
                    return


                self.set_next_state(WAITING_MESSAGE)
            self.set_next_state(WAITING_MESSAGE)
        else:
            print("[CentralAgent] Nema poruka. Prelazim na cekanje poruka ponovno...")
            self.set_next_state(WAITING_MESSAGE)

class SendingMessage(State):
    async def run(self):
        msg = Message()
        msg.set_metadata("performative", "inform")
        msg.set_metadata("ontology", "dashboard_agent_update")
        msg.to = "DashboardAgent@localhost"
        msg_content = {
            "agent_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
            "headlights_status": f"{self.agent.headlights_status}" if hasattr(self.agent, 'headlights_status') else -999,
            "wipers_status": f"{self.agent.wipers_status}" if hasattr(self.agent, 'wipers_status') else -999,
            "ac_status": f"{self.agent.ac_status}" if hasattr(self.agent, 'ac_status') else -999,
            "traction_control_status": f"{self.agent.traction_control_status}" if hasattr(self.agent, 'traction_control_status') else -999,
            "esp_status": f"{self.agent.esp_status}" if hasattr(self.agent, 'esp_status') else -999,
            "rain_level": f"{self.agent.rain_level}" if hasattr(self.agent, 'rain_level') else -999,
            "luminosity_level": f"{self.agent.luminosity_level}" if hasattr(self.agent, 'luminosity_level') else -999,
            "outside_temp": f"{self.agent.outside_temp}" if hasattr(self.agent, 'outside_temp') else -999,
            "inside_temp": f"{self.agent.inside_temp}" if hasattr(self.agent, 'inside_temp') else -999,
            "speed": f"{self.agent.speed}" if hasattr(self.agent, 'speed') else -999
        }
        msg.body = dumps(msg_content)
        await self.send(msg)
        print(f"[CentralAgent] Poslana poruka. Prelazim na cekanje...")
        
        self.set_next_state(WAITING_MESSAGE)

class CentralAgent(Agent):
    async def setup(self):
        template = Template()
        template.set_metadata("performative", "inform")
        fsm = FSMBehaviour()
        fsm.add_state(name=WAITING_MESSAGE, state=WaitingMessage(), initial=True)
        fsm.add_state(name=SENDING_MESSAGE, state=SendingMessage())
        
        #"Recursive" transitions in case there is no message updates
        fsm.add_transition(source=WAITING_MESSAGE, dest=WAITING_MESSAGE)

        #Transitions between different states
        fsm.add_transition(source=WAITING_MESSAGE, dest=SENDING_MESSAGE)
        fsm.add_transition(source=SENDING_MESSAGE, dest=WAITING_MESSAGE)
        

        self.add_behaviour(fsm)
    
if __name__ == "__main__":
    agent = CentralAgent("CentralAgent@localhost", "tajna")
    agent.start()
    agent.wait()  
