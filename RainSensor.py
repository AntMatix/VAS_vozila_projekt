from spade.agent import Agent
from spade.template import Template
from spade import run, wait_until_finished

import argparse
from json import loads
from datetime import datetime, timedelta
import random

from Behaviours import SensorBehaviourTwoReceivers

class RainSensor(Agent):
    """
    RainSensor that has one Behaviour (Periodic Behaviour called SensorBehaviour) and sends data to RoadVisibilityAgent 
    """
    async def setup(self):
        self.say("RainSensor starting...")
        self.id = id
        #komunikacijaTemplate = Template(metadata={"ontology": "aukcija"})
        #komunikacijaPonasanje = KomunikacijaOrganizator()
        #self.add_behaviour(komunikacijaPonasanje, komunikacijaTemplate)
        #aukcijaPonasanje = Aukcija(period=5)
        #self.add_behaviour(aukcijaPonasanje)

        sensor_behaviour = SensorBehaviourTwoReceivers("RoadVisibilityAgent", "DrivingAssistanceAgent", 5)
        self.add_behaviour(sensor_behaviour)
        self.say("RainSensor finished setup.")

    def say(self, line):
        print(f"{self.name}: {line}")
    
    def generate_readings(self):
        return int(random.uniform(0,3))

    
