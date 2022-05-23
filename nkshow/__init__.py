from .app import MyApp

from ._version import version as __version__


def run():
    # Run our app class
    MyApp.run(title="Netket Visualizer", log="nkshow.debuglog")


if __name__ == "__main__":
    run()
