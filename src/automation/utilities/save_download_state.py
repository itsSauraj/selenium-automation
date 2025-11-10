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
      # folder = PROJECT_ROOT + "/application_state"
      # create_directory_if_not_exists(folder)
      # csv_path = folder + "/downloads.csv"

      folder = Path(PROJECT_ROOT) / "application_state"
      create_directory_if_not_exists(folder)
      csv_path = folder / "downloads.csv"

      logger.info(f"Saving download state for Order ID: {order_id}, Doc Type: {doc_type}, Downloaded: {downloaded}, Uploaded: {uploaded}")

      fieldnames = ["order_id", "doc_type", "DOWNLOAD", "upload"]
      new_values = {
        "order_id": order_id,
        "doc_type": doc_type,
        "DOWNLOAD": str(bool(downloaded)).lower(),
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
              row["DOWNLOAD"] = new_values["DOWNLOAD"]
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
    

save_state = SaveDownloadState()