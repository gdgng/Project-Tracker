import os
import sys
import tempfile
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt

# Extra veilige instellingen
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-gpu --disable-software-rasterizer --disable-extensions"
os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
os.environ["QTWEBENGINE_DISABLE_GPU_THREAD"] = "1"
os.environ["QTWEBENGINE_PROFILE_STORAGE_PATH"] = tempfile.mkdtemp()

class BchViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blockchain.com")
        self.setGeometry(100, 100, 1200, 800)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.browser = QWebEngineView()
        self.browser.settings().setAttribute(self.browser.settings().JavascriptEnabled, True)
        self.browser.setZoomFactor(1.0)

        # Hier zet je de URL waar je naartoe wilt
        self.browser.setUrl(QUrl("https://www.blockchain.com/explorer/assets/btc"))
        self.setCentralWidget(self.browser)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = BchViewer()
    viewer.show()
    sys.exit(app.exec_())
