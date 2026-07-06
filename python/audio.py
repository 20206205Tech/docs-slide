# import os
# import re
# import sys
# import asyncio
# import hashlib
# import edge_tts
# import env

# # Ensure console output handles UTF-8 for Vietnamese characters
# if sys.stdout.encoding != "utf-8":
#     try:
#         sys.stdout.reconfigure(encoding="utf-8")
#     except AttributeError:
#         import codecs
#         sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)

# def strip_latex_comments(text):
#     """
#     Remove comments from LaTeX text. Discard lines starting with % (comments).
#     """
#     lines = []
#     for line in text.splitlines():
#         stripped_line = line.strip()
#         # If the line starts with a comment %, skip it entirely
#         if stripped_line.startswith('%') and not stripped_line.startswith(r'\%'):
#             continue
#         # Otherwise, split by unescaped % to remove trailing comments
#         cleaned_line = re.split(r'(?<!\\)%', line)[0]
#         cleaned_line = cleaned_line.replace(r'\%', '%')
#         lines.append(cleaned_line)
#     return '\n'.join(lines)

# def clean_note_text(text):
#     """
#     Strip comments, handle basic formatting commands, and normalize whitespace.
#     """
#     text = strip_latex_comments(text)

#     # Strip basic LaTeX command markers but keep their content.
#     # Replace 2-arg commands like \textcolor{color}{content} -> content
#     text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}\{([^}]+)\}', r'\1', text)
#     # Then 1-arg commands like \textbf{content} -> content
#     text = re.sub(r'\\[a-zA-Z]+\{([^}]+)\}', r'\1', text)

#     # Replace LaTeX line break (\\) with newline
#     text = text.replace(r'\\', '\n')

#     # Replace whitespace characters (newlines, tabs, spaces) with a single space
#     words = text.split()
#     return ' '.join(words)

# def extract_notes_from_tex(content):
#     r"""
#     Extract content from inside \note{...} blocks, handling nested braces correctly.
#     """
#     notes = []
#     idx = 0
#     while True:
#         match = re.search(r'\\note\s*\{', content[idx:])
#         if not match:
#             break

#         start_pos = idx + match.start()
#         open_brace_idx = start_pos + match.end() - 1

#         # Track nested braces
#         brace_count = 1
#         current_idx = open_brace_idx + 1
#         while current_idx < len(content) and brace_count > 0:
#             char = content[current_idx]
#             if char == '{':
#                 brace_count += 1
#             elif char == '}':
#                 brace_count -= 1
#             current_idx += 1

#         if brace_count == 0:
#             note_content = content[open_brace_idx + 1 : current_idx - 1]
#             notes.append(note_content)
#             idx = current_idx
#         else:
#             idx = open_brace_idx + 1

#     return notes

# def parse_doc_inputs(doc_path):
#     r"""
#     Parses doc.tex to find uncommented \input{...} paths in order.
#     """
#     if not os.path.exists(doc_path):
#         print(f"Error: {doc_path} not found.")
#         return []

#     inputs = []
#     with open(doc_path, 'r', encoding='utf-8') as f:
#         for line in f:
#             # Strip comment lines or trailing comments
#             stripped_line = line.strip()
#             if stripped_line.startswith('%') and not stripped_line.startswith(r'\%'):
#                 continue
#             line_no_comment = re.split(r'(?<!\\)%', line)[0]
#             # Match \input{path}
#             matches = re.findall(r'\\input\{([^}]+)\}', line_no_comment)
#             for m in matches:
#                 inputs.append(m.strip())
#     return inputs

# async def generate_tts(text, output_file, voice="vi-VN-HoaiMyNeural"):
#     """
#     Generates TTS for text using edge_tts with retries.
#     """
#     retries = 3
#     for attempt in range(retries):
#         try:
#             communicate = edge_tts.Communicate(text, voice)
#             await communicate.save(output_file)
#             print(f"Successfully generated audio for: '{text[:30]}...' -> {os.path.basename(output_file)}")
#             return True
#         except Exception as e:
#             print(f"Attempt {attempt + 1} failed for text '{text[:30]}...': {e}")
#             if attempt < retries - 1:
#                 await asyncio.sleep(2)
#             else:
#                 raise e
#     return False

# async def main():
#     doc_path = os.path.join(env.PATH_FOLDER_LATEX, "doc.tex")
#     audio_dir = os.path.join(env.PATH_FOLDER_PROJECT, "audio")
#     os.makedirs(audio_dir, exist_ok=True)

#     input_files = parse_doc_inputs(doc_path)
#     if not input_files:
#         print("No input files found in doc.tex.")
#         return

#     segment_paths = []
#     for rel_path in input_files:
#         # Resolve path
#         tex_path = os.path.join(env.PATH_FOLDER_LATEX, rel_path)
#         if not tex_path.endswith('.tex'):
#             tex_path += '.tex'

#         if not os.path.exists(tex_path):
#             print(f"Warning: File {tex_path} does not exist. Skipping.")
#             continue

#         with open(tex_path, 'r', encoding='utf-8') as f:
#             content = f.read()

#         notes = extract_notes_from_tex(content)
#         for note in notes:
#             cleaned = clean_note_text(note)
#             if not cleaned:
#                 continue

#             # Compute MD5 hash
#             note_hash = hashlib.md5(cleaned.encode('utf-8')).hexdigest()
#             seg_file = os.path.join(audio_dir, f"{note_hash}.mp3")

#             if not os.path.exists(seg_file):
#                 print(f"Generating audio for new/modified note: {note_hash}")
#                 await generate_tts(cleaned, seg_file)
#             else:
#                 print(f"Using cached audio: {note_hash}")

#             segment_paths.append(seg_file)

#     if not segment_paths:
#         print("No audio segments to combine.")
#         return

#     # Concatenate all segment MP3 files
#     output_audio = os.path.join(audio_dir, "audio.mp3")
#     print(f"Combining {len(segment_paths)} audio segments into {output_audio}...")
#     with open(output_audio, 'wb') as out_f:
#         for seg_path in segment_paths:
#             with open(seg_path, 'rb') as in_f:
#                 out_f.write(in_f.read())

#     print("Audio processing complete!")

# if __name__ == "__main__":
#     asyncio.run(main())
