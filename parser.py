from docx import Document

def parse_tests(file_path):
    doc = Document(file_path)
    tests = []

    question = None
    options = []
    correct_index = None

    for p in doc.paragraphs:
        text = p.text.strip()

        if text and text[0].isdigit() and "." in text:
            if question:
                tests.append((question, options, correct_index))
            question = text
            options = []
            correct_index = None

        elif text.startswith("-"):
            options.append(text[1:].strip())

        elif text.startswith("+"):
            correct_index = len(options)
            options.append(text[1:].strip())

    if question:
        tests.append((question, options, correct_index))

    return tests
