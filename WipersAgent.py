import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from spade.template import Template
import random
from json import loads, dumps

WAITING_MESSAGE = "WAITING_MESSAGE"
SENDING_MESSAGE = "SENDING_MESSAGE"

WIPERS_OFF = "WIPERS_OFF"
WIPERS_ON = "WIPERS_ON"
DISABLED = "DISABLED"

class FSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"[WipersAgent] Pokrenut. Stanje: {self.current_state}")

    async def on_end(self):
        print(f"[WipersAgent] zavrsio. Stanje: {self.current_state}")
        await self.agent.stop()

class WaitingMessage(State):
    async def run(self):
        self.agent.status = DISABLED
        msg = await self.receive(timeout=10)
        if msg:
            if msg.metadata.get("performative") == "inform" and msg.metadata.get("ontology") == "wipers":
                msg_content = loads(msg.body)
                if 'agent_id' in msg_content and msg_content['agent_id'].lower() == "roadvisibilityagent"+"@localhost":
                    print(f"[WipersAgent] Primljena poruka od *{msg_content['agent_id']}* sa sadržajem: {msg.body}")
                    rain_level_reading = int(msg_content['rain_level'])
                    speed_reading = int(msg_content['speed'])

                    
                    if rain_level_reading > 0 and speed_reading > 5:
                        self.agent.status = WIPERS_ON
                    else:
                        self.agent.status = WIPERS_OFF
                    
                    #Replying to the recieved message
                    reply = msg.make_reply()
                    msg_content = {
                        "agent_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
                        "status": f"{self.agent.status}" if hasattr(self.agent, 'status') else -999
                    }
                    reply.body = dumps(msg_content)
                    await self.send(reply)
                    
                    
                    
                
            self.set_next_state(WAITING_MESSAGE)
        else:
            print("[WipersAgent] No messages. Staying in the Disabled state.")
            self.set_next_state(WAITING_MESSAGE)


class WipersAgent(Agent):
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
    agent = WipersAgent("WipersAgent@localhost", "tajna")
    agent.start()
    agent.wait()  
