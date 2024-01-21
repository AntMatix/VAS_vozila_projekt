from spade.agent import Agent
from spade.template import Template
from spade import run, wait_until_finished

import argparse
from json import loads
from datetime import datetime, timedelta
import random

from Behaviours import SensorBehaviour

class ABSSensor(Agent):
    """
    ABSSensor that has one Behaviour (Periodic Behaviour called SensorBehaviour) and sends data to RoadVisibilityAgent 
    """
    async def setup(self):
        self.say("ABSSensor starting...")
        self.id = id
        sensor_behaviour = SensorBehaviour("DrivingAssistanceAgent", 5)
        self.add_behaviour(sensor_behaviour)
        self.say("ABSSensor finished setup.")

    def say(self, line):
        print(f"{self.name}: {line}")
    
    def generate_readings(self):
        return int(random.uniform(0,1))

    
