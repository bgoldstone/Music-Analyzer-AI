import multiprocessing
import signal
import sys
import time
import api.main
import website.main

running = True

def main():
    """Runs the API and React servers in parallel."""
    api_server = multiprocessing.Process(target=api.main.main)
    api_server.start()
    react_server = multiprocessing.Process(target=website.main.main)
    react_server.start()
    time.sleep(5)
    def handle_signal(signum, frame):
        global running
        print(signum, frame)
        print("Shutting down API Server...")
        api_server.join()
        print("Shutting down React Server...")
        react_server.join()
        running = False
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    while running:
        pass


if __name__ == "__main__":
    main()
