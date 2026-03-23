import curses
import enum
import time

class SCREENS(enum.Enum):
    MAIN = 1
    LOGS = 2

class STATE(enum.Enum):
    MAIN = 1
    CONNECTIONS = 2
    RANSOM = 3
    TARGET = 4


class TUI:
    def __init__(self, bus):
        self.bus = bus
        self.line = 1
        self.screen = curses.initscr()
        self.state = STATE.MAIN
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        self.screen.keypad(True)
        self.screen.nodelay(True)

        # Server Log Window
        self.log_screen = curses.newwin(curses.LINES//2, curses.COLS//2, 0, curses.COLS//2)
        self.log_screen.addstr(0, 0, "===Logs===")
        self.log_screen.refresh()

        self._draw()

    def _set_state(self, state: STATE):
        self.state = state
        self._draw()

    def _draw(self):
        self.screen.clear()
        match self.state:
            case STATE.MAIN: self._draw_main()
            case STATE.CONNECTIONS: self._draw_connections()
            case STATE.RANSOM: self._draw_ransom()
            case STATE.TARGET: self._draw_targets()
        self.screen.refresh()

    def _handle_input(self, c):
        match self.state:
            case STATE.MAIN: self._handle_main_input(c)
            case STATE.CONNECTIONS: self._handle_connections_input(c)
            case STATE.TARGET: self._handle_targets_input(c)
            case STATE.RANSOM: self._handle_ransom_input(c)

    def run(self):
        while True:
            self._drain_logs()
            c = self.screen.getch()
            if c != -1:
                self._handle_input(c)
            time.sleep(0.05)
    
    def _drain_logs(self):
        updated = False
        while not self.bus.log_queue.empty():
            log = self.bus.log_queue.get_nowait()
            self.log_screen.addstr(self.next_line(), 0, log)
            updated = True
        if updated:
            self.log_screen.refresh()

    def next_line(self):
        line = self.line
        self.line += 1
        return line
    

    def end(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()


### MENUS AND INPUTS ####
    
    ### MAIN MENU ###
    def _draw_main(self):
        self.screen.addstr(0, 0, "Please Select Your Action")
        self.screen.addstr(1, 0, "l: list")
        self.screen.addstr(2, 0, "r: Ransom")
        self.screen.addstr(3, 0, "t: Targets")
        self.screen.addstr(4, 0, "q: Quit")

    def _handle_main_input(self, c):
        if c == ord('l'):
            self._set_state(STATE.CONNECTIONS)
            self.bus.cmd_queue.put("list")
        elif c == ord('t'):
            self._set_state(STATE.TARGET)
        elif c ==  ord('r'):
            self._set_state(STATE.RANSOM)
        elif c == ord('q'):
            self.end()
            quit()

    ### CONNECTIONS MENU ###
    def _draw_connections(self):
        self.screen.addstr(0, 0, "Connections: (Select number to add target)")
        if not self.bus.connections:
            self.screen.addstr(1, 0, "No connections yet")
        else:
            for i, c in enumerate(self.bus.connections):
                self.screen.addstr(i+1, 0, f"{i}. {list(c.keys())[0][0]}:{list(c.keys())[0][1]}")
        self.screen.refresh()

    def _handle_connections_input(self, c):
        if c == ord('b'):
            self._set_state(STATE.MAIN)
        else:
            try:
                idx = int(chr(c))
                if idx < len(self.bus.connections):
                    self.bus.targets.append(self.bus.connections[idx])
                    self.screen.addstr(curses.LINES-1, 0, f"Added {list(self.bus.connections[idx].keys())[0][0]}:{list(self.bus.connections[idx].keys())[0][1]} to targets")
                    self.screen.refresh()
            except (ValueError, IndexError):
                pass

    ### TARGET MENU ###
    def _draw_targets(self):
        self.screen.addstr(0, 0, "Targets: (Select number to remove target)")
        if not self.bus.targets:
            self.screen.addstr(1, 0, "No targets yet")
        else:
            for i, c in enumerate(self.bus.targets):
                self.screen.addstr(i+1, 0, f"{i}. {list(c.keys())[0][0]}:{list(c.keys())[0][1]}")
        self.screen.refresh()

    def _handle_targets_input(self, c):
        if c == ord('b'):
            self._set_state(STATE.MAIN)
        else:
            try:
                idx = int(chr(c))
                if idx < len(self.bus.targets):
                    removed = self.bus.targets.pop(idx)
                    self.screen.addstr(curses.LINES-1, 0, f"Removed {list(removed.keys())[0][0]}:{list(removed.keys())[0][1]} from targets")
                    self.screen.refresh()
            except (ValueError, IndexError):
                pass
    ### RANSOM MENU ###
