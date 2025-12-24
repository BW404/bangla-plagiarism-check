import re

def format_text(input_file, output_file, remove_unnecessary_chars=False):
    """
    Formats the text by joining lines that are part of the same sentence.

    Args:
        input_file (str): The path to the input text file.
        output_file (str): The path to the output text file where formatted text will be saved.
        remove_unnecessary_chars (bool): Whether to remove unnecessary characters like quotes.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as infile:
            lines = infile.readlines()

        formatted_text = []
        current_sentence = ""

        for line in lines:
            line = line.strip()
            if remove_unnecessary_chars:
                line = re.sub(r'["“”]', '', line)  # Remove double quotes
                line = re.sub(r"[']+", '', line)  # Remove single quotes

            if line:
                if re.search(r'[।!?]$', line):  # Bangla full stop, exclamation, or question mark
                    current_sentence += line
                    formatted_text.append(current_sentence)
                    current_sentence = ""
                else:
                    current_sentence += line + " "

        if current_sentence:
            formatted_text.append(current_sentence.strip())

        with open(output_file, "w", encoding="utf-8") as outfile:
            for sentence in formatted_text:
                outfile.write(sentence + "\n")

        print(f"Formatted text has been successfully written to '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def convert_sentences_to_lines(input_file, output_file, remove_unnecessary_chars=False):
    """
    Converts each sentence in a Bangla text file into a new line in the output file.

    Args:
        input_file (str): The path to the input Bangla text file.
        output_file (str): The path to the output file where each sentence will be on a new line.
        remove_unnecessary_chars (bool): Whether to remove unnecessary characters like quotes.
    """
    try:
        with open(input_file, "r", encoding="utf-8") as infile:
            content = infile.read()

        if remove_unnecessary_chars:
            content = re.sub(r'["“”]', '', content)  # Remove double quotes
            content = re.sub(r"[']+", '', content)  # Remove single quotes

        sentences = re.split(r'(?<=[।!?])\s*', content)

        with open(output_file, "w", encoding="utf-8") as outfile:
            for sentence in sentences:
                cleaned_sentence = sentence.strip()
                if cleaned_sentence:
                    outfile.write(cleaned_sentence + "\n")

        print(f"Sentences have been successfully written to '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def filter_source_text(input_file, output_file, remove_unnecessary_chars=False):
    """
    Filters the source text file by removing duplicates, empty lines, and irrelevant content,
    while preserving the original line order. Removes sentences containing Bangla digits.
    """
    unique_lines = []
    seen_lines = set()

    bangla_digit_pattern = r'[১২৩৪৫৬৭৮৯০]'

    try:
        with open(input_file, "r", encoding="utf-8") as infile:
            for line in infile:
                cleaned_line = line.strip()
                if remove_unnecessary_chars:
                    cleaned_line = re.sub(r'["“”]', '', cleaned_line)
                    cleaned_line = re.sub(r"[']+", '', cleaned_line)
                    cleaned_line = re.sub(r"[,]+", '', cleaned_line)

                if re.search(bangla_digit_pattern, cleaned_line):
                    continue

                if cleaned_line:
                    if re.search(r'[^\W\d_]', cleaned_line):
                        if cleaned_line not in seen_lines:
                            unique_lines.append(cleaned_line)
                            seen_lines.add(cleaned_line)

        with open(output_file, "a", encoding="utf-8") as outfile:
            for line in unique_lines:
                outfile.write(line + "\n")

        print(f"Filtered source text written to '{output_file}' with {len(unique_lines)} unique lines.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def clean_data(input_file, output_file):
    """
    Cleans the data by formatting, splitting into sentences, and filtering the text.
    """
    format_text(input_file, input_file, remove_unnecessary_chars=True)
    convert_sentences_to_lines(input_file, input_file, remove_unnecessary_chars=True)
    filter_source_text(input_file, output_file, remove_unnecessary_chars=True)
    return output_file


if __name__ == "__main__":
    input_file = "source_text/database_temp.txt"
    output_file = "source_text/database.txt"
    clean_data(input_file, output_file)
