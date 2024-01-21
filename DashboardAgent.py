import tkinter as tk
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.template import Template
from spade import run, wait_until_finished
from json import loads

WAITING_MESSAGE = "WAITING_MESSAGE"
STATUS_COLORS = {
    "ON": "green",
    "OFF": "red",
    "DAYLIGHTS_ON": "lightblue",

    "HEATING_HIGH": "red",
    "HEATING_LOW": "orange",
    "DEHAZING": "pink",
    "COOLING_HIGH": "blue",
    "COOLING_LOW": "lightblue",

    "DISABLED": "black"
}

STATUS_MAPPINGS = {
    "LOW_BEAMS_ON": "ON",
    "DAYLIGHTS_ON": "DAYLIGHTS_ON",

    "WIPERS_ON": "ON",
    "WIPERS_OFF": "OFF",

    "HEATING_HIGH": "HEATING_HIGH",
    "HEATING_LOW": "HEATING_LOW",
    "COOLING_HIGH": "COOLING_HIGH",
    "COOLING_LOW": "COOLING_LOW",
    "DEHAZING": "DEHAZING",

    "ON": "ON",
    "OFF": "OFF",

    "DISABLED": "DISABLED"
}

class DashboardWidget(tk.Canvas):
    def __init__(self, master, description, status, color, size=100, text_height=30, **kwargs):
        super().__init__(master, width=size, height=size + text_height * 2, **kwargs)
        self.color = color
        self.create_text(size // 2, text_height // 2, text=description, anchor=tk.N, fill="black", width=size-10)
        self.lamp = self.create_oval(5, text_height, size-5, size + text_height-10, fill=color, outline=color)
        self.status_text = self.create_text(size // 2, 3*text_height + size // 2, text=status, anchor=tk.N, fill="black", width=size-10)

    def update_color(self, new_color, new_status_text):
        self.itemconfig(self.lamp, fill=new_color)
        self.color = new_color
        self.itemconfig(self.status_text, text=new_status_text)

class DashboardApp:
    def __init__(self, dashboard_gui):
        self.dashboard_gui = dashboard_gui
        self.dashboard_gui.title("Dashboard App")

        screen_width = self.dashboard_gui.winfo_screenwidth()
        screen_height = self.dashboard_gui.winfo_screenheight()

        # Veličina sučelja
        self.dashboard_gui.geometry(f"{screen_width//2}x{screen_height//2}")

        counter = 0
        self.lamp_widgets = {}
        for lamp_id, description in {"headlights_status": "Headlights", "wipers_status": "Wipers", "ac_status": "AC Status", "esp_status": "ESP Status", "traction_control_status": "Traction Ctl"}.items():
            lamp_status = "N/A"
            lamp_widget = DashboardWidget(self.dashboard_gui, description, lamp_status, "grey")
            lamp_widget.grid(row=1, column=counter, pady=25, padx=25)
            self.lamp_widgets[lamp_id] = lamp_widget
            counter += 1
        
        # Widgeti za prikaz komponenti
        self.rain_level_label = tk.Label(self.dashboard_gui, text="Rain Level:")
        self.rain_level_label.grid(row=2, column=0, pady=10, padx=10)
        
        self.luminosity_level_label = tk.Label(self.dashboard_gui, text="Luminosity Level:")
        self.luminosity_level_label.grid(row=3, column=0, pady=10, padx=10)
        
        self.outside_temp_label = tk.Label(self.dashboard_gui, text="Outside Temperature:")
        self.outside_temp_label.grid(row=4, column=0, pady=10, padx=10)
        
        self.inside_temp_label = tk.Label(self.dashboard_gui, text="Inside Temperature:")
        self.inside_temp_label.grid(row=5, column=0, pady=10, padx=10)

        self.speed_label = tk.Label(self.dashboard_gui, text="Speed:")
        self.speed_label.grid(row=6, column=0, pady=10, padx=10)

    def update_widgets(self, readings):
        print("\n[DashboardAgent] Received readings:")
        for k, v in readings.items():
            print(k, v)
            status_text = str(v) if v != -999 else "N/A"
            # Ažuriranje widgeta
            if k == "rain_level":
                self.rain_level_label.config(text=f"Rain Level: {status_text}")
            elif k == "luminosity_level":
                self.luminosity_level_label.config(text=f"Luminosity Level: {status_text}")
            elif k == "outside_temp":
                self.outside_temp_label.config(text=f"Outside Temperature: {status_text}")
            elif k == "inside_temp":
                self.inside_temp_label.config(text=f"Inside Temperature: {status_text}")
            elif k == "speed":
                self.speed_label.config(text=f"Speed: {status_text}")
            else:
                status = STATUS_MAPPINGS.get(v, "-999")
                color = STATUS_COLORS.get(status, "grey")
                status_text = str(v) if v != -999 else "N/A"
                self.lamp_widgets[k].update_color(color, status_text)
        print()

class FSMBehaviour(FSMBehaviour):
    async def on_start(self):
        print(f"[DashboardAgent] Started. State: {self.current_state}")

    async def on_end(self):
        print(f"[DashboardAgent] Ended. State: {self.current_state}")
        await self.agent.stop()

class WaitingMessage(State):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            if msg.metadata.get("performative") == "inform" and msg.metadata.get("ontology") == "dashboard_agent_update":
                msg_content = loads(msg.body)
                # Message received from CentralAgent
                if 'agent_id' in msg_content and msg_content['agent_id'].lower() == "centralagent@localhost":
                    print(f"[DashboardAgent] Received message from *{msg_content['agent_id']}* with content: {msg.body}")
                    self.agent.headlights_status = msg_content.get('headlights_status', -999)
                    self.agent.wipers_status = msg_content.get('wipers_status', -999)
                    self.agent.ac_status = msg_content.get('ac_status', -999)
                    self.agent.esp_status = msg_content.get('esp_status', -999)
                    self.agent.traction_control_status = msg_content.get('traction_control_status', -999)
                    self.agent.rain_level = msg_content.get('rain_level', -999)
                    self.agent.luminosity_level = msg_content.get('luminosity_level', -999)
                    self.agent.outside_temp = msg_content.get('outside_temp', -999)
                    self.agent.inside_temp = msg_content.get('inside_temp', -999)
                    self.agent.speed = msg_content.get('speed', -999)
                    await self.agent.update_dashboard()
                    
                self.set_next_state(WAITING_MESSAGE)
            self.set_next_state(WAITING_MESSAGE)
        else:
            print("[DashboardAgent] No messages. Returning to waiting state...")
            self.set_next_state(WAITING_MESSAGE)
        self.agent.dashboard_gui.update()

class DashboardAgent(Agent):
    async def setup(self):
        self.dashboard_gui = tk.Tk()
        self.app = DashboardApp(self.dashboard_gui)
        self.dashboard_gui.update()
        template = Template()
        template.set_metadata("performative", "inform")
        fsm = FSMBehaviour()
        fsm.add_state(name=WAITING_MESSAGE, state=WaitingMessage(), initial=True)
        
        # "Recursive" transitions in case there are no message updates
        fsm.add_transition(source=WAITING_MESSAGE, dest=WAITING_MESSAGE)

        self.add_behaviour(fsm)

    async def update_dashboard(self):
        readings = {
            "headlights_status": self.headlights_status,
            "wipers_status": self.wipers_status,
            "ac_status": self.ac_status,
            "traction_control_status": self.traction_control_status,
            "esp_status": self.esp_status,
            "rain_level": self.rain_level,
            "luminosity_level": self.luminosity_level,
            "outside_temp": self.outside_temp,
            "inside_temp": self.inside_temp,
            "speed": self.speed
        }
        self.app.update_widgets(readings)
        self.dashboard_gui.update()

async def main():
    agent = DashboardAgent("DashboardAgent@localhost", "secret")
    await agent.start()
    await wait_until_finished(agent)

if __name__ == "__main__":
    run(main())
