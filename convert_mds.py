import os
import logging
import pypandoc
from config import config, configure_logging

configure_logging(config())

WORD_FOLDER = "data/src_words"
MD_FOLDER = "data/src_mds"

# .docxファイルをすべて検索する
for root, dirs, files in os.walk(WORD_FOLDER):
    for file in files:
        if file.endswith(".docx"):
            input_file_path = os.path.join(root, file)

            # 出力用のサブディレクトリ構造を作成する
            rel_path = os.path.relpath(root, WORD_FOLDER)
            output_subdir = os.path.join(MD_FOLDER, rel_path)
            os.makedirs(output_subdir, exist_ok=True)

            output_file_path = os.path.join(
                output_subdir, os.path.splitext(file)[0] + ".md"
            )

            # WordファイルをMarkdownファイルに変換する
            logging.info("Converting %s to %s", input_file_path, output_file_path)
            markdown_content = pypandoc.convert_file(input_file_path, "markdown")

            # 変換したMarkdownファイルを保存する
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write(markdown_content)
            logging.info("Converted %s to %s", input_file_path, output_file_path)
