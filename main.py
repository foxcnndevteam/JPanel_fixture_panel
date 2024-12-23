from subprocess import call, run
from PyQt5 import QtCore, QtWidgets 
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5 import Qt


class EmbeddedTerminal(QtWidgets.QFrame):
    finished = pyqtSignal(int)

    def __init__(self, id: str):
        super().__init__()
        self.process = QtCore.QProcess(self)
        self.process.finished.connect(self.on_finished)

        self.sessionId = f"console_{id}"
        self.terminal = QtWidgets.QFrame()
        self.setStyleSheet(
            """
            border-radius: 5px;
            border: 1px solid #cccccc; 
            background-color: #e6ebe7;
            """
        )

    def start(self, args: "list[str]" = []):
        self.create_tmux_session(";".join(args))
        fullArgs = [
            "-into",
            self.get_terminal_winId(),
            "-si",
            "-geometry",
            "120x30",
            "-sl",
            "2000",
            "-bg",
            "black",
            "-fg",
            "white",
            "-e",
            f"tmux attach-session -t {self.sessionId};",
        ]
        self.process.start("xterm", fullArgs)

    def create_tmux_session(self, command: str):
        tmuxSession = run(["tmux", "has-session", "-t", self.sessionId])
        if tmuxSession.returncode != 0:
            call(f"tmux new-session -A -s {self.sessionId} \; detach", shell=True)
            call(
                f'tmux send-keys -t {self.sessionId} "{command};exit" Enter',
                shell=True,
            )
            self.set_tmux_option("status", "off")
            self.set_tmux_option("history-limit", "3000")
            self.set_tmux_option("mouse", "on")
            self.set_tmux_option("mode-keys", "vi")

    def set_tmux_option(self, option: str, value: str):
        call(f"tmux set-option -t {self.sessionId} {option} {value}", shell=True)
        for i in range(0, 50000):
            call("echo", f'"this is {i}"')

    def on_finished(self, exitCode, exitStatus):
        self.finished.emit(exitCode)

    def Stop(self):
        call(f"tmux kill-session -t {self.sessionId}", shell=True)
        self.process.kill()

    def get_terminal_winId(self) -> str:
        return str(int(self.winId()))

def main():
    app = QApplication([])

    window = QWidget()
    layout = QVBoxLayout()
    embTer = EmbeddedTerminal(2)
    embTer.start()
    layout.addWidget(embTer)
    window.setLayout(layout)
    window.show()
    app.exec()
#     ex.show()
#     ex.raise_()
#     sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    

# import subprocess
# import sys

# # with open("test.log", "wb") as f:
# process = subprocess.Popen("node", stdout=subprocess.PIPE)
# for c in iter(lambda: process.stdout.read(1), b""):
#     sys.stdout.buffer.write(c)
#         # f.buffer.write(c)