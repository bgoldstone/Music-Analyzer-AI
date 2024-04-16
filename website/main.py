import os


def main():
    app_path = os.path.join(os.path.dirname(__file__), "soundsmith")
    os.chdir(app_path)
    os.system("npm start")


if __name__ == "__main__":
    main()
