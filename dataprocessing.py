import csv


def parse_training_data(file_path):
    X = []
    y = []
    with open(file_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    # Tách các khối dữ liệu bởi dấu ---
    blocks = raw.strip().split('---')

    for block in blocks:
        lines = block.strip().split('\n')
        content_lines = []
        label = None

        for line in lines:
            if line.startswith("Content:"):
                first_line = line[len("Content:"):].strip()
                if first_line:
                    content_lines.append(first_line)
            elif line.startswith("Label:"):
                label = line[len("Label:"):].strip()
            else:
                if line.strip():  # bỏ dòng trống
                    content_lines.append(line.strip())

        if content_lines and label:
            full_text = '. '.join(content_lines)
            X.append(full_text)
            y.append(label)

    return X, y


def save_to_csv(X, y, output_file='processed_data.csv'):
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['text', 'label'])  # header
        for text, label in zip(X, y):
            writer.writerow([text, label])
    print(f"✅ Đã lưu {len(X)} mẫu vào '{output_file}'")


if __name__ == "__main__":
    file_path = "info.txt"  # đảm bảo file này cùng thư mục với script
    X, y = parse_training_data(file_path)

    print("📋 Dữ liệu đã xử lý:")
    for i in range(len(X)):
        print(f"X[{i}]: {X[i]}")
        print(f"y[{i}]: {y[i]}")
        print("-----")

    save_to_csv(X, y)
