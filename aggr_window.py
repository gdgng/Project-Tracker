import os
import sys
import tempfile
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

# Fix caching errors & sandbox conflicts
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer --disable-cache"
os.environ["QTWEBENGINE_PROFILE_STORAGE_PATH"] = tempfile.mkdtemp()

class AggrViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aggr Trade Live Viewer - Traxker")
        self.setGeometry(100, 100, 1200, 800)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://aggr.trade/p/BTC"))
        self.setCentralWidget(self.browser)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = AggrViewer()
    viewer.show()
    sys.exit(app.exec_())
