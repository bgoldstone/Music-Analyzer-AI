import multiprocessing
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
    while True:
        try:
            pass
        except KeyboardInterrupt:
            break
    print("Shutting down API Server...")
    api_server.terminate()
    print("Shutting down React Server...")
    react_server.terminate()


if __name__ == "__main__":
    main()
