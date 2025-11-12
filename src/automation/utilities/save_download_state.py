from pathlib import Path
import csv

from automation.utilities.logger import logger
from automation.config.settings import PROJECT_ROOT
from automation.utilities.file_manager import create_directory_if_not_exists

class SaveDownloadState:
    """
      Utility class to save the state of downloads.
    """

    def add(self, order_id: str, doc_type: str, downloaded: bool = True, uploaded: bool = False) -> None:
      """
      Persist a single download/upload state row into application_state/downloads.csv.

      If a row with the same order_id and doc_type exists, update its DOWNLOAD and upload
      values based on the arguments passed. Otherwise append a new row.

      Columns: order_id, doc_type, DOWNLOAD (true/false), upload (true/false)
      """

      folder = Path(PROJECT_ROOT) / "application_state"
      create_directory_if_not_exists(folder)
      csv_path = folder / "downloads.csv"

      logger.info(f"Saving download state for Order ID: {order_id}, Doc Type: {doc_type}, Downloaded: {downloaded}, Uploaded: {uploaded}")

      fieldnames = ["order_id", "doc_type", "download", "upload"]
      new_values = {
        "order_id": order_id,
        "doc_type": doc_type,
        "download": str(bool(downloaded)).lower(),
        "upload": str(bool(uploaded)).lower(),
      }

      rows = []
      updated = False

      if csv_path.exists():
        logger.info(f"Found existing download state file: {csv_path}")
        with csv_path.open("r", newline="", encoding="utf-8") as fh:
          reader = csv.DictReader(fh)
          for row in reader:
            if row.get("order_id") == order_id and row.get("doc_type") == doc_type:
              row["download"] = new_values["download"]
              row["upload"] = new_values["upload"]  
              updated = True
            # ensure all expected keys exist for consistent output
            normalized = {k: row.get(k, "") for k in fieldnames}
            rows.append(normalized)

      if not updated:
        logger.info(f"Adding new download state entry: {new_values}")
        rows.append(new_values)

      with csv_path.open("w", newline="", encoding="utf-8") as fh:
        logger.info(f"Writing download state to CSV file: {csv_path}")
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        logger.info(f"Finished writing download state to CSV file: {csv_path}")
    
    def clear(self) -> None:
      """
      Clear the download state CSV file.
      """
      folder = Path(PROJECT_ROOT) / "application_state"
      csv_path = folder / "downloads.csv"

      if csv_path.exists():
        logger.info(f"Clearing download state file: {csv_path}")
        csv_path.unlink()
      else:
        logger.info(f"No download state file to clear at: {csv_path}")

    def load(self) -> list[dict]:
      """
      Load and return all download state entries from the CSV file.

      Returns:
          list[dict]: A list of dictionaries representing each row in the CSV.
      """
      folder = Path(PROJECT_ROOT) / "application_state"
      csv_path = folder / "downloads.csv"
      entries = []

      if csv_path.exists():
        logger.info(f"Loading download state from file: {csv_path}")
        with csv_path.open("r", newline="", encoding="utf-8") as fh:
          reader = csv.DictReader(fh)
          for row in reader:
            entries.append(row)
        logger.info(f"Loaded {len(entries)} entries from download state file.")
      else:
        logger.info(f"No download state file found at: {csv_path}")

      return entries
    
    def exists(self, order_id: str, doc_type: str) -> bool:
      """
      Check if a download state entry exists for the given order_id and doc_type.

      Returns:
          bool: True if the entry exists, False otherwise.
      """
      entries = self.load()
      for entry in entries:
        if entry.get("order_id") == order_id and entry.get("doc_type") == doc_type:
          return True
      return False
    
    def get_state(self, order_id: str, doc_type: str) -> dict | None:
      """
      Retrieve the download state entry for the given order_id and doc_type.

      Returns:
          dict | None: The entry dictionary if found, otherwise None.
      """
      entries = self.load()
      for entry in entries:
        if entry.get("order_id") == order_id and entry.get("doc_type") == doc_type:
          return entry
      return None
    
    def get_last_entry(self) -> dict | None:
      """
      Retrieve the last download state entry from the CSV file.

      Returns:
          dict | None: The last entry dictionary if found, otherwise None.
      """
      entries = self.load()
      if entries:
        return entries[-1]
      return None

save_state = SaveDownloadState()