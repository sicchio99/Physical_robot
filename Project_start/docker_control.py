import subprocess
import os


def control_docker(action):
    try:
        # Change directory to where the docker-compose file is located
        os.chdir("../Computer_modules")

        # Execute the docker-compose command
        subprocess.run(["docker", "compose", action], check=True)
        return f"Docker Compose {action} command executed successfully."
    except subprocess.CalledProcessError as e:
        return f"Error executing Docker Compose {action}: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2 or sys.argv[1] not in ["up", "down"]:
        print("Usage: python docker_control.py <up|down>")
        sys.exit(1)

    action = sys.argv[1]
    message = control_docker(action)
    print(message)

