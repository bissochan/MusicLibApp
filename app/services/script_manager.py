import subprocess
import logging
import time

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ScriptManager:
    def __init__(self, max_retries=3, retry_delay=5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay  # Seconds between retries

    def run_spotdl(self, url: str, download_dir: str):
        """Run spotdl with retry logic and stream output."""
        attempt = 1
        while attempt <= self.max_retries:
            try:
                logging.info(f"Running spotdl attempt {attempt}/{self.max_retries} for URL: {url}")
                yield f"Running spotdl attempt {attempt}/{self.max_retries}\n"

                # Run spotdl command
                process = subprocess.Popen(
                    ["spotdl", url, "--output", download_dir],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                # Stream output
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        yield f"{line}\n"
                        logging.info(line)

                # Wait for process to complete and check exit code
                return_code = process.wait()
                if return_code == 0:
                    logging.info("spotdl completed successfully")
                    return
                else:
                    raise subprocess.CalledProcessError(return_code, "spotdl")

            except subprocess.CalledProcessError as e:
                logging.error(f"spotdl attempt {attempt} failed with exit code {e.returncode}: {e}")
                yield f"spotdl attempt {attempt} failed: {e}\n"
                if attempt == self.max_retries:
                    logging.error("Max retries reached for spotdl")
                    yield "Failed to download songs after max retries\n"
                    raise
                attempt += 1
                time.sleep(self.retry_delay)
                yield f"Retrying spotdl in {self.retry_delay} seconds...\n"
            except Exception as e:
                logging.error(f"Unexpected error in spotdl attempt {attempt}: {e}")
                yield f"Unexpected error: {e}\n"
                if attempt == self.max_retries:
                    logging.error("Max retries reached for spotdl")
                    yield "Failed to download songs after max retries\n"
                    raise
                attempt += 1
                time.sleep(self.retry_delay)
                yield f"Retrying spotdl in {self.retry_delay} seconds...\n"