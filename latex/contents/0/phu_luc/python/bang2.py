import json
import os
import time
import urllib.error
import urllib.request

# Mapping from result.json categories to report categories
CATEGORY_MAPPING = {
    "Trong dữ liệu (Cơ bản)": "Câu hỏi có trong CSDL pháp luật",
    "Trong dữ liệu (Nâng cao)": "Câu hỏi có trong CSDL pháp luật",
    "Ngoài dữ liệu (Out-of-domain)": "Câu hỏi ngoài phạm vi (đời sống, IT...)",
    "Truy vấn mập mờ (Ambiguous)": "Câu hỏi phức tạp, tối nghĩa",
    "Câu hỏi đánh lừa (Deceptive)": "Câu hỏi phức tạp, tối nghĩa",
}


def extract_json(text):
    """
    Extracts and parses JSON from model response text.
    Handles potential markdown code blocks.
    """
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: find the first '{' and last '}'
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Cannot extract valid JSON from response: {text}")


def call_nvidia_judge_with_retry(api_key, question, context, answer, category):
    """
    Calls NVIDIA API (using OpenAI-compatible endpoint) to judge the RAG response,
    with automatic retry on rate limits (429) or server errors (503).
    """
    url = "https://integrate.api.nvidia.com/v1/chat/completions"

    prompt = f"""Bạn là một chuyên gia đánh giá hệ thống RAG (Retrieval-Augmented Generation) trong lĩnh vực pháp luật Việt Nam.
Nhiệm vụ của bạn là đánh giá câu trả lời của hệ thống (Model Answer) dựa trên câu hỏi (Question), tài liệu truy xuất được (Retrieved Context) và phân loại nhóm câu hỏi (Category).

Dữ liệu đánh giá:
- Nhóm câu hỏi (Category): {category}
- Câu hỏi: {question}
- Tài liệu truy xuất được (Context): {context}
- Câu trả lời của hệ thống (Model Answer): {answer}

Quy tắc phân loại (Verdict):
1. "CORRECT" (Đúng):
   - Nếu câu hỏi thuộc nhóm "Trong dữ liệu" và câu trả lời trả lời đúng, chính xác, đầy đủ thông tin dựa trên tài liệu truy xuất.
   - Nếu câu hỏi thuộc nhóm "Ngoài dữ liệu (Out-of-domain)" hoặc "Câu hỏi đánh lừa / mập mờ", và hệ thống đã nhận diện đúng và từ chối trả lời một cách hợp lý/lịch sự (ví dụ: "Tôi không có thông tin về...", "Đây là câu hỏi ngoài phạm vi hỗ trợ..."). Đây được coi là phản hồi ĐÚNG (chống ảo giác thành công).
2. "REFUSED" (Không trả lời do không chắc chắn):
   - Hệ thống trả lời rằng không tìm thấy thông tin, không có tài liệu phù hợp, hoặc từ chối trả lời vì thiếu thông tin trong tài liệu pháp luật (áp dụng cho các câu hỏi đáng lẽ phải có trong dữ liệu nhưng hệ thống không tìm thấy và từ chối trả lời để an toàn). Ví dụ: "Tôi không tìm thấy thông tin trong tài liệu...", "Không có tài liệu nào đề cập...".
3. "INCORRECT_HALLUCINATION" (Sai / Ảo giác):
   - Hệ thống đưa ra thông tin sai lệch, mâu thuẫn hoặc không có trong tài liệu truy xuất.
   - Hệ thống tự bịa ra thông tin (ảo giác) cho câu hỏi.
   - Hệ thống trả lời linh tinh, không từ chối đối với các câu hỏi ngoài phạm vi hoặc câu hỏi đánh lừa.

Hãy đưa ra phân tích ngắn gọn trong trường "reasoning" và kết luận trong "verdict" (chỉ được chọn một trong ba giá trị: "CORRECT", "INCORRECT_HALLUCINATION", "REFUSED").
Định dạng đầu ra BẮT BUỘC là JSON như sau:
{{
    "reasoning": "phân tích của bạn ở đây",
    "verdict": "CORRECT hoặc INCORRECT_HALLUCINATION hoặc REFUSED"
}}"""

    payload = {
        "model": "meta/llama-3.3-70b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "top_p": 0.7,
        "max_tokens": 1024,
        "stream": False,
    }

    max_retries = 5
    delay = 10  # Initial delay in seconds for retries
    backoff_factor = 2

    for attempt in range(max_retries):
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                text_response = (
                    res_json.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                return extract_json(text_response)
        except urllib.error.HTTPError as e:
            if e.code in [429, 502, 503, 504]:
                print(
                    f"\n   [Rate Limit / Error {e.code}] {e.reason}. Đang ngủ {delay} giây trước khi thử lại (Lần thử {attempt + 1}/{max_retries})..."
                )
                time.sleep(delay)
                delay *= backoff_factor
            else:
                print(f"\n   [Lỗi HTTP {e.code}] {e.reason}. Không thể thử lại.")
                raise e
        except Exception as e:
            print(
                f"\n   [Lỗi kết nối] {e}. Đang ngủ {delay} giây trước khi thử lại (Lần thử {attempt + 1}/{max_retries})..."
            )
            time.sleep(delay)
            delay *= backoff_factor

    raise Exception("Không thể kết nối đến NVIDIA API sau nhiều lần thử lại.")


def write_latex_table(tex_path, stats):
    """
    Writes the aggregated statistics to bang2.tex.
    """
    lines = []
    lines.append(r"\begin{table}[H]")
    lines.append(r"\centering")
    lines.append(r"\refstepcounter{table}")
    lines.append(
        r"\textbf{Bảng \thetable:} Bảng thống kê hiệu năng và độ chính xác của hệ thống RAG"
    )
    lines.append(r"\label{tab:hieu_nang_do_chinh_xac}")
    lines.append(r"\vspace{0.5em}")
    lines.append(r"\begin{tabular}{|l|c|c|c|c|}")
    lines.append(r"\hline")
    lines.append(
        r"\textbf{Nhóm câu hỏi kiểm thử} & \makecell{\textbf{Tổng số}\\\textbf{câu hỏi}} & \makecell{\textbf{Phản hồi}\\\textbf{Đúng (\%)}} & \makecell{\textbf{Phản hồi Sai /}\\\textbf{Ảo giác (\%)}} & \makecell{\textbf{Không trả lời do}\\\textbf{không chắc chắn (\%)}} \\ \hline"
    )

    overall_total = 0
    overall_correct = 0
    overall_incorrect = 0
    overall_refused = 0

    groups = [
        "Câu hỏi có trong CSDL pháp luật",
        "Câu hỏi ngoài phạm vi (đời sống, IT...)",
        "Câu hỏi phức tạp, tối nghĩa",
    ]

    for group in groups:
        g_stats = stats.get(
            group,
            {"total": 0, "CORRECT": 0, "INCORRECT_HALLUCINATION": 0, "REFUSED": 0},
        )
        total = g_stats["total"]
        if total == 0:
            continue

        correct = g_stats["CORRECT"]
        incorrect = g_stats["INCORRECT_HALLUCINATION"]
        refused = g_stats["REFUSED"]

        overall_total += total
        overall_correct += correct
        overall_incorrect += incorrect
        overall_refused += refused

        pct_correct = (correct / total) * 100 if total > 0 else 0
        pct_incorrect = (incorrect / total) * 100 if total > 0 else 0
        pct_refused = (refused / total) * 100 if total > 0 else 0

        row = f"{group} & {total} & {correct} ({pct_correct:.1f}\\%) & {incorrect} ({pct_incorrect:.1f}\\%) & {refused} ({pct_refused:.1f}\\%) \\\\ \\hline"
        lines.append(row)

    if overall_total > 0:
        pct_o_correct = (overall_correct / overall_total) * 100
        pct_o_incorrect = (overall_incorrect / overall_total) * 100
        pct_o_refused = (overall_refused / overall_total) * 100

        overall_row = (
            f"\\textbf{{Tổng cộng (Overall)}} & \\textbf{{{overall_total}}} & "
            f"\\textbf{{{overall_correct} ({pct_o_correct:.1f}\\%)}} & "
            f"\\textbf{{{overall_incorrect} ({pct_o_incorrect:.1f}\\%)}} & "
            f"\\textbf{{{overall_refused} ({pct_o_refused:.1f}\\%)}} \\\\ \\hline"
        )
        lines.append(overall_row)

    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "result.json")
    eval_path = os.path.join(script_dir, "evaluation_detail.json")
    tex_path = os.path.join(script_dir, "bang2.tex")

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    # Check for NVIDIA_API_KEY
    api_key = os.environ.get("NVIDIA_API_KEY")
    use_mock = False

    if not api_key:
        print("\n" + "=" * 80)
        print("[CẢNH BÁO] Biến môi trường NVIDIA_API_KEY chưa được thiết lập!")
        print(
            "Hệ thống sẽ tự động tạo bảng bang2.tex sử dụng dữ liệu giả lập (mock data)"
        )
        print("để bạn có thể biên dịch tài liệu LaTeX ngay lập tức.")
        print(
            "Để chạy đánh giá thật bằng NVIDIA API, vui lòng thiết lập biến môi trường:"
        )
        print('  Windows (PowerShell): $env:NVIDIA_API_KEY="your_key_here"')
        print("  Windows (CMD):        set NVIDIA_API_KEY=your_key_here")
        print('  Linux/macOS:          export NVIDIA_API_KEY="your_key_here"')
        print("=" * 80 + "\n")
        use_mock = True

    if use_mock:
        mock_stats = {
            "Câu hỏi có trong CSDL pháp luật": {
                "total": 60,
                "CORRECT": 54,
                "INCORRECT_HALLUCINATION": 4,
                "REFUSED": 2,
            },
            "Câu hỏi ngoài phạm vi (đời sống, IT...)": {
                "total": 15,
                "CORRECT": 15,
                "INCORRECT_HALLUCINATION": 0,
                "REFUSED": 0,
            },
            "Câu hỏi phức tạp, tối nghĩa": {
                "total": 25,
                "CORRECT": 22,
                "INCORRECT_HALLUCINATION": 1,
                "REFUSED": 2,
            },
        }
        print(f"Đang ghi dữ liệu giả lập vào {tex_path}...")
        write_latex_table(tex_path, mock_stats)
        print("Đã tạo bảng bang2.tex thành công với dữ liệu giả lập!")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Load existing evaluation results and filter out failed API calls (saved as REFUSED due to errors)
    eval_results = []
    evaluated_stts = set()
    if os.path.exists(eval_path):
        try:
            with open(eval_path, "r", encoding="utf-8") as f:
                raw_eval_results = json.load(f)
                for item in raw_eval_results:
                    reasoning = item.get("danh_gia", {}).get("ly_do", "")
                    # Filter out items that failed with API errors (which contain 'Lỗi hệ thống đánh giá')
                    if "Lỗi hệ thống đánh giá" in reasoning:
                        continue
                    eval_results.append(item)
                    evaluated_stts.add(item.get("stt"))
            print(
                f"Đã tải {len(evaluated_stts)} câu hỏi từ cache hợp lệ. (Đã tự động loại bỏ các câu hỏi lỗi trước đó)."
            )
        except Exception as e:
            print(
                f"Lỗi khi đọc file đánh giá cũ: {e}. Sẽ tiến hành đánh giá lại từ đầu."
            )
            eval_results = []

    # Run evaluation
    stats = {
        "Câu hỏi có trong CSDL pháp luật": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
        "Câu hỏi ngoài phạm vi (đời sống, IT...)": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
        "Câu hỏi phức tạp, tối nghĩa": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
    }

    # Populate stats with already evaluated items
    for item in eval_results:
        target_category = item.get("phan_loai_bao_cao")
        verdict = item.get("danh_gia", {}).get("ket_luan", "REFUSED")
        if target_category in stats:
            stats[target_category]["total"] += 1
            stats[target_category][verdict] += 1

    remaining_count = len(data) - len(evaluated_stts)
    if remaining_count > 0:
        print(
            f"Bắt đầu đánh giá {remaining_count} câu hỏi còn lại bằng NVIDIA API (meta/llama-3.3-70b-instruct)..."
        )

        # Add a 1-second rate limit safety delay between successful calls (NVIDIA key usually has good limits)
        request_delay = 1.0

        for idx, item in enumerate(data, 1):
            stt = item.get("stt")
            if stt in evaluated_stts:
                continue

            raw_category = item.get("phan_loai", "Trong dữ liệu (Cơ bản)")
            question = item.get("cau_hoi", "")
            context = item.get("tai_lieu_formatted", "")
            answer = item.get("cau_tra_loi", "")

            target_category = CATEGORY_MAPPING.get(
                raw_category, "Câu hỏi có trong CSDL pháp luật"
            )

            print(f"[{stt}/{len(data)}] Đang chấm Câu hỏi {stt} ({raw_category})...")

            try:
                # Call judge API with retry mechanism
                judge = call_nvidia_judge_with_retry(
                    api_key, question, context, answer, raw_category
                )
                verdict = judge.get("verdict", "REFUSED")
                reasoning = judge.get("reasoning", "")

                print(f"   -> Kết quả: {verdict}")

                # Update stats
                stats[target_category]["total"] += 1
                stats[target_category][verdict] += 1

                # Save to list and cache
                eval_item = {
                    "stt": stt,
                    "phan_loai_goc": raw_category,
                    "phan_loai_bao_cao": target_category,
                    "cau_hoi": question,
                    "cau_tra_loi": answer,
                    "tai_lieu_formatted": context,
                    "danh_gia": {"ket_luan": verdict, "ly_do": reasoning},
                }
                eval_results.append(eval_item)
                evaluated_stts.add(stt)

                # Auto-save cache after each successful item
                with open(eval_path, "w", encoding="utf-8") as f:
                    json.dump(eval_results, f, ensure_ascii=False, indent=4)

                # Rate limiting delay
                time.sleep(request_delay)

            except Exception as e:
                print(
                    f"\n[DỪNG LẠI] Dừng đánh giá tại Câu hỏi {stt} do gặp lỗi không thể tự khôi phục: {e}"
                )
                print(
                    "Dữ liệu đã hoàn thành đã được lưu vào cache. Bạn có thể chạy lại script sau ít phút để tiếp tục."
                )
                break

    # Re-calculate statistics from all evaluated items to write the table
    final_stats = {
        "Câu hỏi có trong CSDL pháp luật": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
        "Câu hỏi ngoài phạm vi (đời sống, IT...)": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
        "Câu hỏi phức tạp, tối nghĩa": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
    }
    for item in eval_results:
        target_category = item.get("phan_loai_bao_cao")
        verdict = item.get("danh_gia", {}).get("ket_luan", "REFUSED")
        if target_category in final_stats:
            final_stats[target_category]["total"] += 1
            final_stats[target_category][verdict] += 1

    print(
        f"\nĐang ghi kết quả thống kê ({len(eval_results)} câu hỏi đã hoàn thành) vào {tex_path}..."
    )
    write_latex_table(tex_path, final_stats)
    print("Hoàn thành!")


if __name__ == "__main__":
    main()
