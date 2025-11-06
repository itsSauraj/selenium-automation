# Selenium Automation Project

This project is an automated workflow built using Selenium that handles two main operations inside the application:

- Download PDF Reports
- Re-upload those PDFs into another section of the application

The steps and navigation flow are not hardcoded — instead, they are read dynamically from an Excel file. This allows the workflow to be flexible and reusable without changing the code every time. The script will be executed on a Virtual Machine, where the Excel file and output directories will be provided by the user.

The automation logs in to the application, follows the navigation instructions row-by-row, downloads the required PDF files, stores them in a predefined folder, and then switches to another workflow where it uploads those same files to a different page.

Everything is structured cleanly using Poetry for dependency and environment management, making it easy to install, maintain, and update.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Running the Project](#running-the-project)
- [Running the Tests](#running-the-tests)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [API/Workflow](#apiworkflow)
- [Disclaimer](#disclaimer)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Python 3.12+
- Poetry
- Google Chrome

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd selenium-automation
    ```

2.  **Install Dependencies:**
    Open your terminal, navigate to the `selenium-automation` directory, and run the following command to install the project dependencies:
    ```bash
    poetry install
    ```

## Running the Project

To run the main automation script, use the following command:
```bash
poetry run python3 src/automation/main.py
```

## Running the Tests

To run the unit tests, use the following command:
```bash
poetry run pytest
```

## Configuration

The project can be configured using the `.env` file. Create a `.env` file in the root directory of the project by copying the `.env.example` file:

```bash
cp .env.example .env
```

Then, update the variables in the `.env` file as needed:

```
BASE_URL=https://example.com
USERNAME=testuser
PASSWORD=testpassword
DOWNLOAD_PATH=downloads/
UPLOAD_PATH=uploads/
LOG_FILE_PATH=logs/run.log
EXCEL_FILE_PATH=data/navigation.xlsx
```

## Project Structure

```bash
selenium-automation/
│
├── pyproject.toml                 # managed by poetry
├── poetry.lock                    # generated automatically
├── README.md
├── .env.example
│
├── data/
│   ├── navigation.xlsx
│   └── sample_navigation.xlsx
│
├── downloads/
├── uploads/
├── logs/
│   └── run.log
│
├── src/
│   └── automation/                # package root (matches project name)
│       │
│       ├── __init__.py
│       ├── main.py                # entry script
│       │
│       ├── config/
│       │   ├── settings.py
│       │   └── locators.py
│       │
│       ├── authentication/
│       │   ├── login.py
│       │   └── session_manager.py
│       │
│       ├── workflows/
│       │   ├── download_reports.py
│       │   └── upload_reports.py
│       │
│       ├── utilities/
│       │   ├── excel_reader.py
│       │   ├── file_manager.py
│       │   ├── wait_utils.py
│       │   └── logger.py
│       │
│       └── ui/
│           ├── page_base.py
│           └── navigation.py
│
└── tests/
    ├── test_download_flow.py
    └── test_upload_flow.py
```

## API/Workflow

The project consists of two main workflows that are defined in the `src/automation/workflows` directory:

1.  **Download PDF Reports (`download_reports.py`):** This workflow reads the navigation steps from the `Download` sheet in the `data/navigation.xlsx` file and executes them to download the PDF reports.

2.  **Re-upload PDFs (`upload_reports.py`):** This workflow reads the navigation steps from the `Upload` sheet in the `data/navigation.xlsx` file and executes them to upload the downloaded PDF reports.

The navigation steps in the Excel file are defined with the following columns:

-   **Action:** The action to be performed (e.g., `navigate`, `click`, `send_keys`).
-   **LocatorType:** The type of locator to be used (e.g., `id`, `name`, `xpath`).
-   **LocatorValue:** The value of the locator.
-   **Value:** The value to be used for the action (e.g., the URL to navigate to, the text to be sent).

## Disclaimer

Since the automation depends on the current HTML structure and UI flow, any changes to the DOM (like new IDs, changed CSS classes, or layout modifications) may require updates to element locators in the `navigation.xlsx` file.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.