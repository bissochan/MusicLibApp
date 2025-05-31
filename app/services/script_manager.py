import subprocess
import sys

class ScriptManager:
    def run_spotdl(self, url: str, path_to_folder: str):
        print("Running spotdl")
        process = subprocess.Popen(
            ["spotdl", url],
            cwd=path_to_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line-buffered
            universal_newlines=True
        )
        # Stream output line by line
        for line in iter(process.stdout.readline, ''):
            yield line.strip()
        for line in iter(process.stderr.readline, ''):
            yield line.strip()
        process.stdout.close()
        process.stderr.close()
        return_code = process.wait()
        if return_code != 0:
            yield f"Error: spotdl failed with return code {return_code}"
            raise Exception(f"spotdl failed with return code {return_code}")