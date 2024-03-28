import multiprocessing
import signal
import sys
import api.main
import website.main


def main():
    """Runs the API and React servers in parallel."""
    api_server = multiprocessing.Process(target=api.main.main)
    api_server.start()
    print("Running API Server on http://localhost:8000")
    react_server = multiprocessing.Process(target=website.main.main)
    react_server.start()
    print("Running React Server on http://localhost:3000")
    running = True

    def handle_signal(signum, frame):
        print(signum, frame)
        print("Shutting down API Server...")
        api_server.join()
        print("Shutting down React Server...")
        react_server.join()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    while running:
        pass


if __name__ == "__main__":
    main()
