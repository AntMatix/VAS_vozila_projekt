from spade.agent import Agent
from spade.template import Template
from spade import run, wait_until_finished

import argparse
from json import loads
from datetime import datetime, timedelta

from LuminositySensor import LuminositySensor
from RainSensor import RainSensor
from InsideTempSensor import InsideTempSensor
from OutsideTempSensor import OutsideTempSensor
from SpeedSensor import SpeedSensor
from ABSSensor import ABSSensor
from ESPSensor import ESPSensor
from RoadVisibilityAgent import RoadVisibilityAgent
from HeadlightsAgent import HeadlightsAgent
from WipersAgent import WipersAgent
from DrivingAssistanceAgent import DrivingAssistanceAgent
from ACControlAgent import ACControlAgent
from CentralAgent import CentralAgent
from DashboardAgent import DashboardAgent



async def main():
    dashboard_agent = DashboardAgent("DashboardAgent@localhost", "tajna")
    await dashboard_agent.start()
   
    luminosity_sensor = LuminositySensor("luminositySensor@localhost", "tajna")
    await luminosity_sensor.start()

    rain_sensor = RainSensor("RainSensor@localhost", "tajna")
    await rain_sensor.start()

    inside_temp_sensor = InsideTempSensor("InsideTempSensor@localhost", "tajna")
    await inside_temp_sensor.start()

    outside_temp_sensor = OutsideTempSensor("OutsideTempSensor@localhost", "tajna")
    await outside_temp_sensor.start()

    speed_sensor = SpeedSensor("SpeedSensor@localhost", "tajna")
    await speed_sensor.start()

    abs_sensor = ABSSensor("ABSSensor@localhost", "tajna")
    await abs_sensor.start()

    esp_sensor = ESPSensor("ESPSensor@localhost", "tajna")
    await esp_sensor.start()
   
    road_visibility_agent = RoadVisibilityAgent("RoadVisibilityAgent@localhost", "tajna")
    await road_visibility_agent.start()
    
    headlights_agent = HeadlightsAgent("HeadlightsAgent@localhost", "tajna")
    await headlights_agent.start()

    wipers_agent = WipersAgent("WipersAgent@localhost", "tajna")
    await wipers_agent.start()

    driving_assistance_agent = DrivingAssistanceAgent("DrivingAssistanceAgent@localhost", "tajna")
    await driving_assistance_agent.start()

    accontrol_agent = ACControlAgent("ACControlAgent@localhost", "tajna")
    await accontrol_agent.start()

    central_agent = CentralAgent("CentralAgent@localhost", "tajna")
    await central_agent.start()

    
    await wait_until_finished(road_visibility_agent)
    await wait_until_finished(luminosity_sensor)
    await wait_until_finished(rain_sensor)
    await wait_until_finished(inside_temp_sensor)
    await wait_until_finished(outside_temp_sensor)
    await wait_until_finished(speed_sensor)
    await wait_until_finished(abs_sensor)
    await wait_until_finished(esp_sensor)
    await wait_until_finished(headlights_agent)
    await wait_until_finished(wipers_agent)
    await wait_until_finished(driving_assistance_agent)
    await wait_until_finished(accontrol_agent)
    await wait_until_finished(central_agent)
    await wait_until_finished(dashboard_agent)

if __name__ =='__main__':
    run(main())
