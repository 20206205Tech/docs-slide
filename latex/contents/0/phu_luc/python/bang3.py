import json
import os


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "result.json")
    mmd_path = os.path.join(script_dir, "bang3.mmd")

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    print(f"Reading data from {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Count categories
    counts = {}
    for item in data:
        cat = item.get("phan_loai", "Không xác định")
        counts[cat] = counts.get(cat, 0) + 1

    total = len(data)
    print(f"Category counts: {counts}")

    # Generate Mermaid pie chart
    lines = []
    lines.append(
        f"pie title Phân lượng kịch bản thử nghiệm hệ thống (Tổng số: {total})"
    )

    # Sort categories to keep order consistent
    sorted_cats = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    for cat, count in sorted_cats:
        lines.append(f'    "{cat}" : {count}')

    print(f"Writing Mermaid diagram to {mmd_path}...")
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("Successfully generated bang3.mmd!")


if __name__ == "__main__":
    main()
