from spade.behaviour import PeriodicBehaviour, CyclicBehaviour, OneShotBehaviour, State
from spade.agent import Agent
from spade.message import Message

from aioxmpp import JID
from datetime import datetime
from json import loads, dumps
from asyncio import sleep
import random


class SensorBehaviour(PeriodicBehaviour):
    """Ponašanje senzora koji šalju podatke samo jednom agentu."""

    def __init__(self, receiver, period):
        super().__init__(period=period)
        self.receiver = receiver + "@localhost"
        self.status = 1
        self.counter = 0
        
    
    async def run(self):
        msg = Message(metadata={"performative": "inform", "ontology": "sensor"})
        msg.to = self.receiver
        msg_content = {
            "sensor_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
            "sensor_status": self.status,
            "readings": self.generate_readings()
        }
        msg.body = dumps(msg_content)
        await self.send(msg)
        print(f"Message sent to: {msg.to} with the contents: {msg.body}")


    async def on_end(self) -> None:
        await self.agent.stop()

    def generate_readings(self):
        return self.agent.generate_readings()


class SensorBehaviourTwoReceivers(PeriodicBehaviour):
    """Ponašanje senzora koji šalju podatke prema dva agenta."""

    def __init__(self, first_receiver, second_receiver, period):
        super().__init__(period=period)
        self.first_receiver = first_receiver + "@localhost"
        self.second_receiver = second_receiver + "@localhost"
        self.status = 1
        self.counter = 0
        
    
    async def run(self):
        readings = self.generate_readings()
        msg = Message(metadata={"performative": "inform", "ontology": "sensor"})
        msg.to = self.first_receiver
        msg_content = {
            "sensor_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
            "sensor_status": self.status,
            "readings": readings
        }
        msg.body = dumps(msg_content)
        await self.send(msg)
        print(f"Message sent to: {msg.to} with the contents: {msg.body}")

        msg = Message(metadata={"performative": "inform", "ontology": "sensor"})
        msg.to = self.second_receiver
        msg_content = {
            "sensor_id": f"{self.agent.jid[0]}@{self.agent.jid[1]}",
            "sensor_status": self.status,
            "readings": readings
        }
        msg.body = dumps(msg_content)
        await self.send(msg)
        print(f"Message sent to: {msg.to} with the contents: {msg.body}")


    async def on_end(self) -> None:
        await self.agent.stop()

    def generate_readings(self):
        return self.agent.generate_readings()