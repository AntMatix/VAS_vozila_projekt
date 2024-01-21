from spade.agent import Agent
from spade.template import Template
from spade import run, wait_until_finished

import argparse
from json import loads
from datetime import datetime, timedelta
import random

from Behaviours import SensorBehaviourTwoReceivers

class OutsideTempSensor(Agent):
    """
    OutsideTempSensor that has one Behaviour (Periodic Behaviour called SensorBehaviour) and sends data to RoadVisibilityAgent 
    """
    async def setup(self):
        self.say("OutsideTempSensor starting...")
        self.id = id
        sensor_behaviour = SensorBehaviourTwoReceivers("RoadVisibilityAgent", "DrivingAssistanceAgent", 5)
        self.add_behaviour(sensor_behaviour)
        self.say("OutsideTempSensor finished setup.")

    def say(self, line):
        print(f"{self.name}: {line}")
    
    def generate_readings(self):
        return int(random.uniform(-30,40))

    
