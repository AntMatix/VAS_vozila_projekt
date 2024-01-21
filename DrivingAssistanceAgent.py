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

OFF = "OFF"
ON = "ON"
ERROR = "ERROR"

class FSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"[DrivingAssistanceAgent] Pokrenut. Stanje: {self.current_state}")

    async def on_end(self):
        print(f"[DrivingAssistanceAgent] zavrsio. Stanje: {self.current_state}")
        await self.agent.stop()

class CekanjePoruke(State):
    async def run(self):
        print(f"[DrivingAssistanceAgent] WAITING MESSAGE")
        msg = await self.receive(timeout=10)
        if msg:
            ##Message received from sensors:
            if msg.metadata.get("performative") == "inform" and msg.metadata.get("ontology") == "sensor":
                msg_content = loads(msg.body)            
                ##Message received from rain sensor
                if 'sensor_id' in msg_content and msg_content['sensor_id'].lower() == "rainsensor"+"@localhost":
                    print(f"[DrivingAssistanceAgent] Primljena poruka od *{msg_content['sensor_id']}* sa sadržajem: {msg.body}")
                    self.agent.rain_level = msg_content['readings']
                    self.set_next_state(SENDING_MESSAGE_CENTRAL)
                ##Message received from speed sensor
                if 'sensor_id' in msg_content and msg_content['sensor_id'].lower() == "speedsensor"+"@localhost":
                    print(f"[DrivingAssistanceAgent] Primljena poruka od *{msg_content['sensor_id']}* sa sadržajem: {msg.body}")
                    self.agent.speed = msg_content['readings']
                    self.set_next_state(SENDING_MESSAGE_CENTRAL)
                ##Message received from esp sensor
                if 'sensor_id' in msg_content and msg_content['sensor_id'].lower() == "espsensor"+"@localhost":
                    print(f"[DrivingAssistanceAgent] Primljena poruka od *{msg_content['sensor_id']}* sa sadržajem: {msg.body}")
                    self.agent.esp_sensor_status = msg_content['readings']
                    self.set_next_state(SENDING_MESSAGE_CENTRAL)
                ##Message received from abs sensor
                if 'sensor_id' in msg_content and msg_content['sensor_id'].lower() == "abssensor"+"@localhost":
                    print(f"[DrivingAssistanceAgent] Primljena poruka od *{msg_content['sensor_id']}* sa sadržajem: {msg.body}")
                    self.agent.abs_sensor_status = msg_content['readings']
                    self.set_next_state(SENDING_MESSAGE_CENTRAL)
                ##Message received from outsidetempsensor
                if 'sensor_id' in msg_content and msg_content['sensor_id'].lower() == "outsidetempsensor"+"@localhost":
                    print(f"[DrivingAssistanceAgent] Primljena poruka od *{msg_content['sensor_id']}* sa sadržajem: {msg.body}")
                    self.agent.outside_temp = msg_content['readings']
                    self.set_next_state(SENDING_MESSAGE_CENTRAL)
        else:
            print("[DrivingAssistanceAgent] Nema poruka")
            print("[DrivingAssistanceAgent] Prelazim na slanje poruka...")
            self.set_next_state(WAITING_MESSAGE)


class SendingMessageCentral(State):
    async def run(self):
        if hasattr(self.agent, 'abs_sensor_status') and hasattr(self.agent, 'esp_sensor_status') and hasattr(self.agent, 'rain_level') and hasattr(self.agent, 'speed') and hasattr(self.agent, 'outside_temp'):
            # Logika za Traction Control (tc)
            #Ispis očitanja i stanja prije promjene
            print(f"\n\n ESP SENZOR: {self.agent.esp_sensor_status}, ABS SENSOR: {self.agent.abs_sensor_status}, OUTSIDE TEMP: {self.agent.outside_temp}, SPEED: {self.agent.speed}, RAIN: {self.agent.rain_level}")

            if self.agent.abs_sensor_status == 0 and self.agent.esp_sensor_status == 0:
                self.agent.traction_control_status = OFF
            elif 0 < self.agent.speed <= 40 and self.agent.rain_level == 0:  # Isključi tc za niske brzine bez kiše
                self.agent.traction_control_status = OFF
            else:
                self.agent.traction_control_status = ON
        
            # Logika za ESP
            if self.agent.esp_sensor_status == 0 and self.agent.esp_sensor_status == 0:
                self.agent.esp_status = OFF
            elif self.agent.speed > 40 or self.agent.rain_level > 0:  # Uključi esp za brzine veće od 40 ili kišu
                    self.agent.esp_status = ON
            else:
                self.agent.esp_status = ON
            
            if self.agent.outside_temp < 3:
                self.agent.traction_control_status = ON
                self.agent.esp_status = ON

        msg = Message()
        msg.set_metadata("performative", "inform")
        msg.set_metadata("ontology", "central_agent_update")
        msg.to = "CentralAgent@localhost"
        msg_content = {
            "agent_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
            "speed": f"{self.agent.speed}" if hasattr(self.agent, 'speed') else -999,
            "traction_control_status": f"{self.agent.traction_control_status}" if hasattr(self.agent, 'traction_control_status') else -999,
            "esp_status": f"{self.agent.esp_status}" if hasattr(self.agent, 'esp_status') else -999
        }
        msg.body = dumps(msg_content)
        await self.send(msg)
        print(f"[DrivingAssistanceAgent] Poslana poruka. Prelazim na cekanje...")
        self.set_next_state(WAITING_MESSAGE)

class DrivingAssistanceAgent(Agent):
    async def setup(self):
        template = Template()
        template.set_metadata("performative", "inform")
        fsm = FSMBehaviour()
        fsm.add_state(name=WAITING_MESSAGE, state=CekanjePoruke(), initial=True)
        fsm.add_state(name=SENDING_MESSAGE_CENTRAL, state=SendingMessageCentral())
        

        #Transition Waiting to Waiting
        fsm.add_transition(source=WAITING_MESSAGE, dest=WAITING_MESSAGE)

        fsm.add_transition(source=WAITING_MESSAGE, dest=SENDING_MESSAGE_CENTRAL)
        fsm.add_transition(source=SENDING_MESSAGE_CENTRAL, dest=WAITING_MESSAGE)

        self.add_behaviour(fsm)
    
if __name__ == "__main__":
    agent = DrivingAssistanceAgent("DrivingAssistanceAgent@localhost", "tajna")
    agent.start()
    agent.wait()
