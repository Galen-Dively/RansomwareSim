import tui


class Menu:
    def __init__(self, tui: tui.TUI):
        self.tui = tui

    def run(self):
        self.tui.add_text("This is main menu for navigation\nr: Ransom\nq: Quit", tui.SCREENS.MAIN, (0, 0))
        c = self.tui.screen.getch()
        if c == ord('q'):
            self.tui.end()
            quit()