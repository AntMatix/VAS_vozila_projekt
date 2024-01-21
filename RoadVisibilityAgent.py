import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from spade.template import Template
import random
from json import loads, dumps

WAITING_MESSAGE = "WAITING_MESSAGE"
SENDING_MESSAGE_CENTRAL = "SENDING_MESSAGE_CENTRAL"
SENDING_MESSAGE_VISIBILITY = "SENDING_MESSAGE_VISIBILITY"

class FSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"[RoadVisibilityAgent] Pokrenut. Stanje: {self.current_state}")

    async def on_end(self):
        print(f"[RoadVisibilityAgent] zavrsio. Stanje: {self.current_state}")
        await self.agent.stop()

class CekanjePoruke(State):
    async def run(self):
        print(f"[RoadVisibilityAgent] WAITING MESSAGE")
        msg = await self.receive(timeout=10)
        if msg:
            ##Message received from sensors:
            if msg.metadata.get("performative") == "inform" and msg.metadata.get("ontology") == "sensor":
                msg_content = loads(msg.body)
                ##Message received from luminosity sensor
                if 'sensor_id' in msg_content and msg_content['sensor_id'].lower() == "luminositysensor"+"@localhost":
                    print(f"[RoadVisibilityAgent] Primljena poruka od *{msg_content['sensor_id']}* sa sadržajem: {msg.body}")
                    self.agent.luminosity_level = msg_content['readings']
                    self.set_next_state(SENDING_MESSAGE_VISIBILITY)
                ##Message received from rain sensor
                if 'sensor_id' in msg_content and msg_content['sensor_id'].lower() == "rainsensor"+"@localhost":
                    print(f"[RoadVisibilityAgent] Primljena poruka od *{msg_content['sensor_id']}* sa sadržajem: {msg.body}")
                    self.agent.rain_level = msg_content['readings']
                    self.set_next_state(SENDING_MESSAGE_VISIBILITY)
                ##Message received from inside temperature sensor
                if 'sensor_id' in msg_content and msg_content['sensor_id'].lower() == "insidetempsensor"+"@localhost":
                    print(f"[RoadVisibilityAgent] Primljena poruka od *{msg_content['sensor_id']}* sa sadržajem: {msg.body}")
                    self.agent.inside_temp = msg_content['readings']
                    self.set_next_state(SENDING_MESSAGE_VISIBILITY)
                ##Message received from outside temperature sensor
                if 'sensor_id' in msg_content and msg_content['sensor_id'].lower() == "outsidetempsensor"+"@localhost":
                    print(f"[RoadVisibilityAgent] Primljena poruka od *{msg_content['sensor_id']}* sa sadržajem: {msg.body}")
                    self.agent.outside_temp = msg_content['readings']
                    self.set_next_state(SENDING_MESSAGE_VISIBILITY)
                ##Message received from speed sensor
                if 'sensor_id' in msg_content and msg_content['sensor_id'].lower() == "speedsensor"+"@localhost":
                    print(f"[RoadVisibilityAgent] Primljena poruka od *{msg_content['sensor_id']}* sa sadržajem: {msg.body}")
                    self.agent.speed = msg_content['readings']
                    self.set_next_state(SENDING_MESSAGE_VISIBILITY)
            ##Message received from HeadlightsAgent
            if msg.metadata.get("performative") == "inform" and msg.metadata.get("ontology") == "lights":
                msg_content = loads(msg.body)
                if 'agent_id' in msg_content and msg_content['agent_id'].lower() == "headlightsagent"+"@localhost":
                    print(f"[RoadVisibilityAgent] Primljena poruka od *{msg_content['agent_id']}* sa sadržajem: {msg.body}")
                    self.agent.headlights_status = msg_content['status']
                    self.set_next_state(SENDING_MESSAGE_CENTRAL)
            ##Message received from WipersAgent
            if msg.metadata.get("performative") == "inform" and msg.metadata.get("ontology") == "wipers":
                msg_content = loads(msg.body)
                if 'agent_id' in msg_content and msg_content['agent_id'].lower() == "wipersagent"+"@localhost":
                        print(f"[RoadVisibilityAgent] Primljena poruka od *{msg_content['agent_id']}* sa sadržajem: {msg.body}")
                        self.agent.wipers_status = msg_content['status']
                        self.set_next_state(SENDING_MESSAGE_CENTRAL)
            ##Message received from ACControlAgent
            if msg.metadata.get("performative") == "inform" and msg.metadata.get("ontology") == "heating":
                msg_content = loads(msg.body)
                if 'agent_id' in msg_content and msg_content['agent_id'].lower() == "accontrolagent"+"@localhost":
                        print(f"[RoadVisibilityAgent] Primljena poruka od *{msg_content['agent_id']}* sa sadržajem: {msg.body}")
                        self.agent.ac_status = msg_content['status']
                        self.set_next_state(SENDING_MESSAGE_CENTRAL)

        else:
            print("[RoadVisibilityAgent] Nema poruka")
            print("[RoadVisibilityAgent] Prelazim na slanje poruka...")
            self.set_next_state(WAITING_MESSAGE)

class SendingMessageVisibility(State):
    async def run(self):
        if hasattr(self.agent, 'luminosity_level'):
            msg = Message()
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "lights")
            msg.to = "HeadlightsAgent@localhost"
            msg_content = {
                "agent_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
                "luminosity_level": f"{self.agent.luminosity_level}" if hasattr(self.agent, 'luminosity_level') else -999,
                "rain_level": f"{self.agent.rain_level}" if hasattr(self.agent, 'rain_level') else -999
            }
            msg.body = dumps(msg_content)
            await self.send(msg)
            print(f"[RoadVisibilityAgent] Poslana poruka prema HeadlightsAgent. Prelazim na cekanje...")
        if hasattr(self.agent, 'rain_level'):
            msg = Message()
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "wipers")
            msg.to = "WipersAgent@localhost"
            msg_content = {
                "agent_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
                "rain_level": f"{self.agent.rain_level}" if hasattr(self.agent, 'rain_level') else -999,
                "speed": f"{self.agent.speed}" if hasattr(self.agent, 'speed') else -999
            }
            msg.body = dumps(msg_content)
            await self.send(msg)
            print(f"[RoadVisibilityAgent] Poslana poruka prema WipersAgent. Prelazim na cekanje...")
        if hasattr(self.agent, 'inside_temp') and hasattr(self.agent, 'outside_temp'):
            msg = Message()
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "heating")
            msg.to = "ACControlAgent@localhost"
            msg_content = {
                "agent_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
                "rain_level": f"{self.agent.rain_level}" if hasattr(self.agent, 'rain_level') else -999,
                "inside_temp": f"{self.agent.inside_temp}" if hasattr(self.agent, 'inside_temp') else -999,
                "outside_temp": f"{self.agent.outside_temp}" if hasattr(self.agent, 'outside_temp') else -999,
            }
            msg.body = dumps(msg_content)
            await self.send(msg)
            print(f"[RoadVisibilityAgent] Poslana poruka prema ACControlAgent. Prelazim na cekanje...")

        self.set_next_state(WAITING_MESSAGE)

class SendingMessageCentral(State):
    async def run(self):
        msg = Message()
        msg.set_metadata("performative", "inform")
        msg.set_metadata("ontology", "central_agent_update")
        msg.to = "CentralAgent@localhost"
        msg_content = {
            "agent_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
            "headlights_status": f"{self.agent.headlights_status}" if hasattr(self.agent, 'headlights_status') else -999,
            "wipers_status": f"{self.agent.wipers_status}" if hasattr(self.agent, 'wipers_status') else -999,
            "ac_status": f"{self.agent.ac_status}" if hasattr(self.agent, 'ac_status') else -999,
            "rain_level": f"{self.agent.rain_level}" if hasattr(self.agent, 'rain_level') else -999,
            "luminosity_level": f"{self.agent.luminosity_level}" if hasattr(self.agent, 'luminosity_level') else -999,
            "outside_temp": f"{self.agent.outside_temp}" if hasattr(self.agent, 'outside_temp') else -999,
            "inside_temp": f"{self.agent.inside_temp}" if hasattr(self.agent, 'inside_temp') else -999,
            "speed": f"{self.agent.speed}" if hasattr(self.agent, 'speed') else -999
        }
        msg.body = dumps(msg_content)
        await self.send(msg)
        print(f"[RoadVisibilityAgent] Poslana poruka. Prelazim na cekanje...")
        self.set_next_state(WAITING_MESSAGE)

class RoadVisibilityAgent(Agent):
    async def setup(self):
        template = Template()
        template.set_metadata("performative", "inform")
        fsm = FSMBehaviour()
        fsm.add_state(name=WAITING_MESSAGE, state=CekanjePoruke(), initial=True)
        fsm.add_state(name=SENDING_MESSAGE_CENTRAL, state=SendingMessageCentral())
        fsm.add_state(name=SENDING_MESSAGE_VISIBILITY, state=SendingMessageVisibility())

        #Transition Waiting to Waiting
        fsm.add_transition(source=WAITING_MESSAGE, dest=WAITING_MESSAGE)

        fsm.add_transition(source=WAITING_MESSAGE, dest=SENDING_MESSAGE_VISIBILITY)
        fsm.add_transition(source=SENDING_MESSAGE_VISIBILITY, dest=WAITING_MESSAGE)

        fsm.add_transition(source=WAITING_MESSAGE, dest=SENDING_MESSAGE_CENTRAL)
        fsm.add_transition(source=SENDING_MESSAGE_CENTRAL, dest=WAITING_MESSAGE)

        self.add_behaviour(fsm)
    
if __name__ == "__main__":
    agent = RoadVisibilityAgent("RoadVisibilityAgent@localhost", "tajna")
    agent.start()
    agent.wait()  
