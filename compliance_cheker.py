import os
import re
import subprocess
import tempfile
from py_markdown_table.markdown_table import markdown_table


directory_path = "./"
compliance_file_name = "./Docs/compliance.md"

surveys = list()
all_authors = set()

# Traverse through the directory and its subdirectories
for dirpath, dirnames, filenames in os.walk(directory_path):
    for file_name in filenames:
        if file_name.endswith(".svx"):  # Check if the file has .svx extension
            file_path = os.path.join(dirpath, file_name)

            # Open the file and read its content
            try:
                with open(file_path, "r") as file:
                    file_content = (
                        file.readlines()
                    )  # Read entire file into a list of lines

                    start_line_number = None
                    end_line_number = None
                    inside_block = False

                    # Iterate over the lines to find the contiguous block
                    for line_number, line in enumerate(
                        file_content, 0
                    ):  # Enumerate lines and start counting from 1
                        if ";  OBLIGATORY FIELDS" in line:
                            start_line_number = line_number
                            inside_block = True
                        elif inside_block and line.startswith(";"):
                            end_line_number = line_number
                        else:
                            if inside_block:
                                break  # Exit the loop if the block ends
                            inside_block = False

                    # Print the line numbers of the beginning and end of the block
                    if start_line_number is not None and end_line_number is not None:
                        compliance_block = file_content[
                            start_line_number : end_line_number + 1
                        ]

                        def try_get_field(lines_block, field_name):
                            for line in lines_block:
                                if line.startswith(f";    {field_name}"):
                                    return " ".join(line.split()[2:]).strip()

                        def try_get_all_fields(lines_block, field_name):
                            fields = list()
                            for line in lines_block:
                                if line.startswith(f";    {field_name}"):
                                    fields.append(" ".join(line.split()[2:]).strip())
                            if len(fields) > 0:
                                return fields

                        def check_date_format(date_str):
                            pattern = r"^\d{4}-\d{2}-\d{2}$"
                            return bool(re.match(pattern, date_str))

                        def check_license_format(license_str):
                            return "CC BY SA 4.0" == license_str

                        cave_name = try_get_field(compliance_block, "Cave_name")
                        section_name = try_get_field(compliance_block, "Section_name")
                        entry_last_update = try_get_field(
                            compliance_block, "Entry_last_update"
                        )
                        license = try_get_field(compliance_block, "Licence")
                        survey_device = try_get_field(compliance_block, "Survey_device")

                        authors = try_get_all_fields(compliance_block, "Author")
                        if authors and len(authors) > 0:
                            for author in authors:
                                if "Puchatek" in author:
                                    continue
                                if "Prosiaczek" in author:
                                    continue
                                all_authors.add(author)

                        if not cave_name:
                            print(f"Cave_name missing in: {file_path}")
                        if not section_name:
                            print(f"Section_name missing in: {file_path}")
                        if not entry_last_update:
                            print(f"Entry_last_update missing in: {file_path}")
                        if not license:
                            print(
                                f"License missing or malformed ({license}) in: {file_path}"
                            )
                        if not license:
                            print(f"License missing in: {file_path}")
                        if not check_license_format(license):
                            print(f"Unknown license {license} in : {file_path}")
                        if not check_date_format(entry_last_update):
                            print(
                                f"Entry_last_update malformed ({entry_last_update}) in: {file_path}"
                            )
                        if not survey_device:
                            print(f"Survey_device missing in : {file_path}")
                        if not authors:
                            print(f"Authors missing in: {file_path}")

                    else:
                        print(f"No OBLIGATORY FIELDS block in: {file_path}")

                    authors_string = None
                    if authors:
                        authors_string = "; ".join(authors)

                    if not authors_string:
                        print(
                            f"Problem with authors in ({authors, authors_string}): {file_path}"
                        )

                    overall = None
                    if start_line_number is None:
                        overall = ":boom:"
                    elif (
                        cave_name
                        and section_name
                        and entry_last_update
                        and license
                        and survey_device
                        and authors_string
                    ):
                        if check_date_format(
                            entry_last_update
                        ) and check_license_format(license):
                            overall = ":cake:"
                        else:
                            overall = ":green_apple:"
                    else:
                        overall = ":pick:"

                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".3d"
                    ) as temp_file:
                        output_file_name = temp_file.name
                        result = subprocess.run(
                            ["cavern", "-s", file_path, "-o", output_file_name],
                            capture_output=True,
                            text=True,
                        )
                        if os.path.exists(output_file_name):
                            os.remove(output_file_name)

                    if result.returncode == 0:
                        compile_status = ":green_apple:"
                    else:
                        print(f"Unable to cavern {file_path}")
                        compile_status = ":boom:"

                    survey_info = {
                        "overall": str(overall),
                        "cave_name": str(cave_name),
                        "section_name": str(section_name),
                        "entry_last_update": str(entry_last_update),
                        "license": str(license),
                        "survey_device": str(survey_device),
                        "authors": str(authors_string),
                        "compiles": str(compile_status),
                        "filename": f"[{file_name}]({file_path})",
                    }

                    surveys.append(survey_info)

            except Exception as e:
                print(f"Error reading {file_path}: {e}")


def parse_name_and_club(input_str):
    parts = input_str.split(" - ")

    # Check if both parts are present
    if len(parts) == 2:
        name, club = parts
        return {"name": name, "club": club}
    else:
        return {"name": input_str, "club": ""}


print()
print("All authors:")
print(
    markdown_table([parse_name_and_club(author) for author in sorted(all_authors)])
    .set_params(
        row_sep="markdown",
        padding_width=0,
        padding_weight="centerleft",
        quote=False,
    )
    .get_markdown()
)


md_table = (
    markdown_table(sorted(surveys, key=lambda s: (s["cave_name"], s["section_name"])))
    .set_params(
        row_sep="markdown",
        padding_width=0,
        padding_weight="centerleft",
        quote=False,
    )
    .get_markdown()
)

with open(compliance_file_name, "w") as of:
    of.write(
        "\n".join(
            [
                "# Overview of metadata in `.svx` files inside this repository.",
                "",
                "This file was procedurally generated using `compliance_checker.py`.",
                "You can run it by executing `python3 compliance_checker.py` to get up to date version.",
                "",
                "",
            ]
        )
    )
    of.write(md_table)
