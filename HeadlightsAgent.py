import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from spade.template import Template
import random
from json import loads, dumps

WAITING_MESSAGE = "WAITING_MESSAGE"
SENDING_MESSAGE = "SENDING_MESSAGE"

LOW_BEAMS_ON = "LOW_BEAMS_ON"
DAYLIGHTS_ON = "DAYLIGHTS_ON"
DISABLED = "DISABLED"

class FSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"[HeadlightsAgent] Pokrenut. Stanje: {self.current_state}")

    async def on_end(self):
        print(f"[HeadlightsAgent] zavrsio. Stanje: {self.current_state}")
        await self.agent.stop()

class WaitingMessage(State):
    async def run(self):
        self.agent.status = DISABLED
        msg = await self.receive(timeout=10)
        if msg:
            if msg.metadata.get("performative") == "inform" and msg.metadata.get("ontology") == "lights":
                msg_content = loads(msg.body)
                if 'agent_id' in msg_content and msg_content['agent_id'].lower() == "roadvisibilityagent"+"@localhost":
                    print(f"[HeadlightsAgent] Primljena poruka od *{msg_content['agent_id']}* sa sadržajem: {msg.body}")
                    luminosity_reading = int(msg_content['luminosity_level'])
                    rain_reading = int(msg_content['rain_level'])

                    if 0 <= luminosity_reading <= 15:
                        self.agent.status = LOW_BEAMS_ON
                    elif 16 <= luminosity_reading <= 25:
                        if rain_reading > 0:
                            self.agent.status = LOW_BEAMS_ON
                        else:
                            self.agent.status = DAYLIGHTS_ON
                    elif 26 <= luminosity_reading <= 40:
                        if rain_reading >= 2:
                            self.agent.status = LOW_BEAMS_ON
                        else:
                            self.agent.status = DISABLED
                    else:
                        self.agent.status(-999)
                    
                    
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
            print("[HeadlightsAgent] No messages. Staying in the Disabled state.")
            self.set_next_state(WAITING_MESSAGE)


class HeadlightsAgent(Agent):
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
    agent = HeadlightsAgent("HeadlightsAgent@localhost", "tajna")
    agent.start()
    agent.wait()  
