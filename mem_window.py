import webview
def get_title():
    return window.evaluate_js("document.title")

window = webview.create_window("Live View Mempool - Tracker", "https://www.mempool.space")
webview.start()

# print(get_title())  # Fetches the webpage title
