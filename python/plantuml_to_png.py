import os
import sys

from plantuml import PlantUML


def render_plantuml(input_file: str, output_file: str):
    # Official PlantUML server

    # server = PlantUML(url="http://www.plantuml.com/plantuml/img/")

    # docker run -d -p 8080:8080 plantuml/plantuml-server:tomcat
    # server = PlantUML(url="http://localhost:8080/img/")
    # 134.185.92.211:8880
    server = PlantUML(url="http://134.185.92.211:8880/img/")

    try:
        # Read the input file
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Ensure it has @startuml and @enduml if not present
        if not content.startswith("@startuml"):
            content = "@startuml\n" + content
        if not content.endswith("@enduml"):
            content = content + "\n@enduml"

        # Use the server to process the code
        # server.processes returns image bytes
        image_bytes = server.processes(content)

        # Save the image
        with open(output_file, "wb") as f:
            f.write(image_bytes)

        print(f"Successfully rendered: {input_file} -> {output_file}")
    except Exception as e:
        print(f"An error occurred while rendering {input_file}: {e}")


def main():
    # Set stdout to use UTF-8 to handle Vietnamese characters in paths
    if sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    if len(sys.argv) < 2:
        print("Usage: python plantuml_to_png.py <file1.txt/puml> <file2.txt/puml> ...")
        sys.exit(1)

    for input_file in sys.argv[1:]:
        if not os.path.exists(input_file):
            print(f"File not found: {input_file}")
            continue

        base_name = os.path.splitext(input_file)[0]
        output_file = base_name + ".png"

        print(f"Processing {input_file}...")
        render_plantuml(input_file, output_file)
        # time.sleep(20)


if __name__ == "__main__":
    main()
