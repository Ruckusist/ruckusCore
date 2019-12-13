try:
    import ruckusCore
except ImportError:
    print("#==? [ERR] You must install ruckusCore first.")
    print("#==> [COPY] pip install -U ruckusCore")
    print("#--> Then Try again. See Ruckusist.com for more info.")
    exit(1)
app = ruckusCore.App()
app.run()