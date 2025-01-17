import os
import glob
import subprocess
import re


def sanitize_filename(name: str) -> str:
    '''Replace characters invalid in Windows and other filesystems'''
    return re.sub(r'[\\/*?:"<>|]', '_', name)


class FileAndFolderRenamer:
    def __init__(self, base_dir):
        """Initialize the handler with directory paths"""
        self.base_dir = base_dir
        research_paths = [f"{base_dir}/{dirs}" for dirs in os.listdir(base_dir)]

        paths = []
        for path in research_paths:
            try:
                new_path = {}
                new_path['folder_path'] = path
                pdf_files = glob.glob(f"{path}/*.pdf")
                original_pdf = [f for f in pdf_files if not f.startswith(f"{path}/summary_")][0]
                new_path['research_path'] = original_pdf
                new_path['pdf_summary_path'] = f"{glob.glob(f"{path}/summary_**.pdf".strip(), recursive=True)[0]}"
                new_path['md_summary_path'] = f"{glob.glob(f"{path}/summary_**.md".strip(), recursive=True)[0]}"

                paths.append(new_path)
            except Exception as e:
                print(f"Error processing path {path}: {e}")
                continue

        # print(paths)

        for path in paths:
            try:
                # Get title from original PDF
                command = ['pdftitle', '-p', path['research_path']]
                output = subprocess.check_output(command, text=True).strip()
                safe_output = sanitize_filename(output)
                
                # Create new filenames
                new_pdf = f"{path['folder_path']}/{safe_output}.pdf"
                new_summary_pdf = f"{path['folder_path']}/summary_{safe_output}.pdf"
                new_summary_md = f"{path['folder_path']}/summary_{safe_output}.md"
                new_folder = f"{self.base_dir}/{safe_output}"

                # Rename files first
                os.rename(path['research_path'], new_pdf)
                os.rename(path['pdf_summary_path'], new_summary_pdf)
                os.rename(path['md_summary_path'], new_summary_md)
                # Rename folder last
                os.rename(path['folder_path'], new_folder)
                
                print(f"Successfully processed {safe_output}")
                
            except Exception as e:
                print(f"Error processing files: {e}")

        

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Change all the files and containing folder name to a more suitable name"
    )
    parser.add_argument("directory", help='Base directory containing PDF files')
    args = parser.parse_args()

    handler = FileAndFolderRenamer(args.directory)
    # handler.process_files_and_folder()


if __name__ == '__main__':
    main()
    
