import json
import os
import re
import sqlite3
import sys
from urllib.parse import parse_qs, urlparse

import requests
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

# Consolidated Model Type Mapping
MODEL_TYPE_MAPPING = {
    ("Hypernetwork", None): "hypernetworks",
    ("Model", None): "diffusion_models",
    ("Controlnet", None): "controlnet",
    ("LORA", None): "loras",
    ("TextualInversion", None): "embeddings",
    ("Checkpoint", "Model"): "checkpoints",
    ("Checkpoint", "VAE"): "vae",
    ("VAE", "Model"): "vae",
}


def determine_types(model_type, file_type):
    key = (model_type, file_type)
    if key in MODEL_TYPE_MAPPING:
        return MODEL_TYPE_MAPPING[key]
    key = (model_type, None)
    if key in MODEL_TYPE_MAPPING:
        return MODEL_TYPE_MAPPING[key]
    key = (None, file_type)
    if key in MODEL_TYPE_MAPPING:
        return MODEL_TYPE_MAPPING[key]
    return None


def check_gated(url, status_update_func=None):
    try:
        if status_update_func:
            status_update_func("Checking if model is gated...", False)
        response = requests.get(url, stream=True, allow_redirects=True)
        # Close the connection immediately
        response.close()
        if response.status_code == 200:
            return False
        elif response.status_code == 401:
            return True
        else:
            if status_update_func:
                status_update_func(
                    f"Unexpected status code: {response.status_code}", True
                )
            return True
    except Exception as e:
        if status_update_func:
            status_update_func(f"Error checking gated: {e}", True)
        return True


def get_auth_tokens():
    db_paths = ["visionatrix.db", "../Visionatrix/visionatrix.db"]
    tokens = {}
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name, value FROM global_settings WHERE name IN (?, ?)",
                    ("huggingface_auth_token", "civitai_auth_token"),
                )
                rows = cursor.fetchall()
                for name, value in rows:
                    tokens[name] = value
                conn.close()
            except Exception as e:
                print(f"Error reading tokens from {db_path}: {e}")
            break  # If we've found the database and read the tokens, no need to check other paths
    return tokens


class URLWorker(QObject):
    # Define signals
    finished = Signal()
    url_corrected = Signal(str)
    homepage_extracted = Signal(str)
    default_filename_found = Signal(str)
    second_filename_found = Signal(str)
    hash_fetched = Signal(str)
    gated_checked = Signal(bool)
    status_update = Signal(str, bool)
    files_found = Signal(list, str)  # list of files, model_type
    model_type_found = Signal(str)

    def __init__(self, url, huggingface_token=None, civitai_token=None):
        super().__init__()
        self.url = url
        self.huggingface_token = huggingface_token
        self.civitai_token = civitai_token

    def run(self):
        if "civitai.com" in self.url:
            self.process_civitai_url()
        else:
            self.process_huggingface_url()
        self.finished.emit()

    def process_civitai_url(self):
        self.status_update.emit("Processing CivitAI URL...", False)

        # Extract modelVersionId or modelId
        model_version_id = self.extract_civitai_model_version_id(self.url)
        if not model_version_id:
            # Attempt to extract a modelId instead
            model_version_id = self.extract_civitai_model_version_id_maybe(self.url)
            if not model_version_id:
                self.status_update.emit(
                    "Failed to extract modelVersionId or modelId from URL.", True
                )
                return

            metadata = self.fetch_civitai_metadata(
                f"https://civitai.com/api/v1/model-versions/{model_version_id}",
                log_warning=False,
            )
            if not metadata:
                model_id = model_version_id

                # Fetch the latest model version
                self.status_update.emit(
                    f"Fetching the latest version for modelId: {model_id}", False
                )
                latest_version_id = self.fetch_civitai_latest_model_version(model_id)
                if not latest_version_id:
                    self.status_update.emit(
                        "Failed to fetch the latest model version from CivitAI.", True
                    )
                    return

                model_version_id = latest_version_id

        # Fetch metadata
        metadata = self.fetch_civitai_metadata(
            f"https://civitai.com/api/v1/model-versions/{model_version_id}"
        )
        if not metadata:
            self.status_update.emit("Failed to fetch metadata from CivitAI.", True)
            return

        # Get model_type
        model_type = metadata.get("model", {}).get("type", None)

        # Get files
        files = metadata.get("files", [])
        if not files:
            self.status_update.emit("No files found in metadata.", True)
            return

        # Emit files_found signal with model_type
        self.files_found.emit(files, model_type)

        # Extract homepage
        model_id = metadata.get("modelId", "")
        if model_id:
            homepage = f"https://civitai.com/models/{model_id}"
            self.homepage_extracted.emit(homepage)
            self.status_update.emit(f"Extracted homepage: {homepage}", False)

    def extract_civitai_model_version_id_maybe(self, url):
        """We can not be sure what will we extract with this, a modelVersionId or a modelId."""
        try:
            match = re.search(r"/models/(\d+)", url)
            if match:
                return match.group(1)
        except Exception as e:
            self.status_update.emit(f"Error extracting modelId: {e}", True)
        return None

    def extract_civitai_model_version_id(self, url):
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            model_version_id = query_params.get("modelVersionId", [None])[0]
            if model_version_id:
                return model_version_id
        except Exception as e:
            self.status_update.emit(f"Error extracting modelVersionId: {e}", True)
        return None

    def fetch_civitai_latest_model_version(self, model_id):
        try:
            api_url = f"https://civitai.com/api/v1/models/{model_id}"
            self.status_update.emit(
                f"Fetching latest model version from: {api_url}", False
            )

            headers = {}
            if self.civitai_token:
                headers["Authorization"] = f"Bearer {self.civitai_token}"

            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                versions = data.get("modelVersions", [])
                if versions:
                    # Assume the first version is the latest
                    return versions[0].get("id")
                else:
                    self.status_update.emit(
                        "No versions found in the model data.", True
                    )
            else:
                self.status_update.emit(
                    f"Failed to fetch model data. Status code: {response.status_code}",
                    True,
                )
        except Exception as e:
            self.status_update.emit(f"Error fetching latest model version: {e}", True)
        return None

    def process_huggingface_url(self):
        corrected_url = self.url

        if "huggingface.co" in self.url and "/blob/" in self.url:
            corrected_url = self.url.replace("/blob/", "/resolve/")
            self.status_update.emit("Corrected URL from 'blob' to 'resolve'", False)
        self.url_corrected.emit(corrected_url)

        # Extract homepage
        homepage = self.extract_huggingface_homepage(corrected_url)
        if homepage:
            self.status_update.emit(f"Extracted homepage: {homepage}", False)
            self.homepage_extracted.emit(homepage)

        # Get default filename
        default_filename = self.get_default_filename(corrected_url)
        if default_filename:
            self.status_update.emit(f"Default filename: {default_filename}", False)
            self.default_filename_found.emit(default_filename)

        # Fetch hash for HuggingFace models
        model_hash = ""
        if "huggingface.co" in corrected_url:
            model_hash = self.prefill_hash_from_huggingface(corrected_url)
            if model_hash:
                self.status_update.emit(f"Fetched hash: {model_hash}", False)
                self.hash_fetched.emit(model_hash)
                # Search CivitAI by hash
                self.search_civitai_by_hash(model_hash)
            else:
                self.status_update.emit("Hash not found", True)
                self.hash_fetched.emit("")
        else:
            self.hash_fetched.emit("")

        # Check if gated
        gated = check_gated(corrected_url, status_update_func=self.status_update.emit)
        self.gated_checked.emit(gated)
        if gated:
            self.status_update.emit("Model is gated (requires token)", True)
        else:
            self.status_update.emit("Model is not gated", False)

    def extract_huggingface_homepage(self, url):
        try:
            if "huggingface.co" in url:
                base_url = re.match(r"(https://huggingface\.co/[^/]+/[^/]+)", url)
                if base_url:
                    return base_url.group(1)
            return ""
        except Exception as e:
            self.status_update.emit(f"Error extracting HuggingFace homepage: {e}", True)
            return ""

    def get_default_filename(self, url):
        try:
            self.status_update.emit("Fetching default filename...", False)
            headers = {}
            if "huggingface.co" in url and self.huggingface_token:
                headers["Authorization"] = f"Bearer {self.huggingface_token}"
            response = requests.head(url, headers=headers, allow_redirects=True)
            if "Content-Disposition" in response.headers:
                cd = response.headers["Content-Disposition"]

                if "filename*=" in cd:
                    match = re.search(
                        r"filename\*\s*=\s*[^']*'[^']*'([^;]+)", cd, re.IGNORECASE
                    )
                    if match:
                        return match.group(1)

                match = re.search(r'filename\s*=\s*"([^"]+)"', cd, re.IGNORECASE)
                if match:
                    return match.group(1)

                match = re.search(r"filename\s*=\s*([^;]+)", cd, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

            return os.path.basename(response.url)
        except Exception as e:
            self.status_update.emit(f"Error getting default filename: {e}", True)
            return ""

    def prefill_hash_from_huggingface(self, url):
        try:
            self.status_update.emit("Fetching hash from HuggingFace...", False)
            headers = {}
            if self.huggingface_token:
                headers["Authorization"] = f"Bearer {self.huggingface_token}"
            response = requests.head(url, headers=headers, allow_redirects=False)
            if response.status_code in (200, 302):
                etag = response.headers.get("x-linked-etag")
                if etag:
                    clean_etag = etag.strip('"')
                    return clean_etag
            else:
                self.status_update.emit(
                    f"Unexpected status code for hash request: {response.status_code}",
                    True,
                )
                return ""
        except Exception as e:
            self.status_update.emit(f"Error fetching hash from HuggingFace: {e}", True)
            return ""

    def fetch_civitai_metadata(self, api_url, log_warning=True):
        try:
            self.status_update.emit(f"Fetching metadata from: {api_url}", False)
            headers = {}
            if self.civitai_token:
                headers["Authorization"] = f"Bearer {self.civitai_token}"
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                metadata = response.json()
                return metadata
            else:
                self.status_update.emit(
                    f"Failed to fetch metadata. Status code: {response.status_code}",
                    log_warning,
                )
        except Exception as e:
            self.status_update.emit(f"Error fetching metadata: {e}", log_warning)
        return None

    def search_civitai_by_hash(self, model_hash):
        try:
            self.status_update.emit("Searching CivitAI by hash...", False)
            api_url = f"https://civitai.com/api/v1/model-versions/by-hash/{model_hash}"
            headers = {}
            if self.civitai_token:
                headers["Authorization"] = f"Bearer {self.civitai_token}"
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                model_type = data.get("model", {}).get("type")
                file_type = None
                if "files" in data and data["files"]:
                    file_type = data["files"][0].get("type")
                    civitai_filename = data["files"][0].get("name")
                    if civitai_filename:
                        self.second_filename_found.emit(civitai_filename)
                        self.status_update.emit(
                            f"Found filename on CivitAI: {civitai_filename}", False
                        )
                else:
                    self.status_update.emit("No files found in CivitAI data", True)

                types_value = determine_types(model_type, file_type)
                if types_value:
                    self.status_update.emit(
                        f"Determined type '{types_value}' from model_type '{model_type}' and file_type '{file_type}'",
                        False,
                    )
                    self.model_type_found.emit(types_value)
                else:
                    self.status_update.emit(
                        f"Unknown combination of model_type '{model_type}' and file_type '{file_type}', please report this",
                        True,
                    )
            else:
                self.status_update.emit(
                    f"CivitAI returned status code {response.status_code} for hash {model_hash}",
                    True,
                )
        except Exception as e:
            self.status_update.emit(f"Error searching CivitAI by hash: {e}", True)


class ModelCatalogEditor(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize tokens
        tokens = get_auth_tokens()
        self.huggingface_token = tokens.get("huggingface_auth_token", None)
        self.civitai_token = tokens.get("civitai_auth_token", None)

        log_init_message = []
        if self.huggingface_token:
            log_init_message.append("HuggingFace token found.")
        else:
            log_init_message.append("HuggingFace token not found.")

        if self.civitai_token:
            log_init_message.append("CivitAI token found.")
        else:
            log_init_message.append("CivitAI token not found.")

        print("\n".join(log_init_message))

        self.setWindowTitle("Model Catalog Editor")

        # Main layout
        main_layout = QVBoxLayout()

        # Form layout using QGridLayout
        form_layout = QGridLayout()

        # Helper function to create a stretching QLineEdit
        def create_stretching_line_edit(placeholder_text):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(placeholder_text)
            line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            return line_edit

        # URL
        self.url_edit = create_stretching_line_edit("Enter model URL")
        form_layout.addWidget(QLabel("URL:"), 0, 0)
        form_layout.addWidget(self.url_edit, 0, 1)

        # Process Button
        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process_url)
        form_layout.addWidget(self.process_button, 1, 1)

        # Download URL
        self.download_url_edit = create_stretching_line_edit("Download URL")
        form_layout.addWidget(QLabel("Download URL:"), 2, 0)
        form_layout.addWidget(self.download_url_edit, 2, 1)

        # Homepage
        self.homepage_edit = create_stretching_line_edit("Enter homepage URL")
        form_layout.addWidget(QLabel("Homepage:"), 3, 0)
        form_layout.addWidget(self.homepage_edit, 3, 1)

        # HuggingFace Filename
        self.filename_edit = create_stretching_line_edit("HuggingFace Filename")
        self.filename_edit.setReadOnly(True)
        form_layout.addWidget(QLabel("HugFace name:"), 4, 0)
        form_layout.addWidget(self.filename_edit, 4, 1)

        # CivitAI Filename
        self.second_filename_label = create_stretching_line_edit("CivitAI Filename")
        self.second_filename_label.setReadOnly(True)
        form_layout.addWidget(QLabel("CivitAI name:"), 5, 0)
        form_layout.addWidget(self.second_filename_label, 5, 1)

        # Overridden Filename
        self.overridden_filename_edit = create_stretching_line_edit(
            "Enter overridden filename"
        )
        form_layout.addWidget(QLabel("Force Filename:"), 6, 0)
        form_layout.addWidget(self.overridden_filename_edit, 6, 1)

        # Hash
        self.hash_edit = create_stretching_line_edit("Enter SHA256 hash")
        form_layout.addWidget(QLabel("Hash:"), 7, 0)
        form_layout.addWidget(self.hash_edit, 7, 1)

        # Types (multiselect in two columns)
        self.types_group = QGroupBox()
        self.types_layout = QGridLayout()

        types = [
            "checkpoints",
            "text_encoders",
            "clip_vision",
            "controlnet",
            "diffusion_models",
            "diffusers",
            "ipadapter",
            "instantid",
            "loras",
            "photomaker",
            "sams",
            "ultralytics",
            "upscale_models",
            "vae",
            "vae_approx",
            "pulid",
            "embeddings",
            "hypernetworks",
        ]

        self.type_checkboxes = {}
        num_columns = 2
        for index, type_name in enumerate(types):
            checkbox = QCheckBox(type_name)
            self.type_checkboxes[type_name] = checkbox
            row = index // num_columns
            col = index % num_columns
            self.types_layout.addWidget(checkbox, row, col)

        self.types_group.setLayout(self.types_layout)
        form_layout.addWidget(QLabel("Types:"), 8, 0)
        form_layout.addWidget(self.types_group, 8, 1)

        # Gated checkbox
        self.gated_checkbox = QCheckBox()
        form_layout.addWidget(QLabel("Gated model:"), 9, 0)
        form_layout.addWidget(self.gated_checkbox, 9, 1)

        # Regexes
        regexes_layout = QGridLayout()
        self.class_type_edit = create_stretching_line_edit("Enter class_type regex")
        regexes_layout.addWidget(QLabel("class_type:"), 0, 0)
        regexes_layout.addWidget(self.class_type_edit, 0, 1)

        self.input_name_edit = create_stretching_line_edit("Enter input_name regex")
        regexes_layout.addWidget(QLabel("input_name:"), 1, 0)
        regexes_layout.addWidget(self.input_name_edit, 1, 1)

        self.input_value_edit = create_stretching_line_edit(
            "Enter input_value regex (required)"
        )
        regexes_layout.addWidget(QLabel("input_value:"), 2, 0)
        regexes_layout.addWidget(self.input_value_edit, 2, 1)

        form_layout.addWidget(QLabel("Regexes:"), 10, 0)
        form_layout.addLayout(regexes_layout, 10, 1)

        # Add the Save button directly to the grid layout
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_model)
        form_layout.addWidget(self.save_button, 11, 1)

        main_layout.addLayout(form_layout)

        # Log Widget
        log_group = QGroupBox("Logs")
        log_layout = QVBoxLayout()
        self.log_widget = QPlainTextEdit()
        self.log_widget.setReadOnly(True)
        self.log_widget.setPlaceholderText("Logs will appear here...")
        log_layout.addWidget(self.log_widget)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        self.setLayout(main_layout)

        # Load existing models_catalog.json
        self.models_catalog = {}
        self.models_catalog_file = "models_catalog.json"
        if os.path.exists(self.models_catalog_file):
            with open(self.models_catalog_file, "r", encoding="utf-8") as f:
                try:
                    self.models_catalog = json.load(f)
                except json.JSONDecodeError:
                    QMessageBox.critical(
                        self, "Error", "Failed to parse models_catalog.json"
                    )
                    self.models_catalog = {}

        # Thread and Worker
        self.thread = None
        self.worker = None

    def save_model(self):
        """
        Gather data from the form, validate, and save the new model entry to models_catalog.json.
        """
        # Gather data from fields
        homepage = self.homepage_edit.text().strip()
        url = self.download_url_edit.text().strip()
        filename = self.filename_edit.text().strip()
        second_filename = self.second_filename_label.text().strip()
        overridden_filename = self.overridden_filename_edit.text().strip()
        model_hash = self.hash_edit.text().strip()
        gated = self.gated_checkbox.isChecked()

        # Get selected types
        types = [
            type_name
            for type_name, checkbox in self.type_checkboxes.items()
            if checkbox.isChecked()
        ]

        # Regexes
        class_type = self.class_type_edit.text().strip()
        input_name = self.input_name_edit.text().strip()
        input_value = self.input_value_edit.text().strip()

        # Validation
        if not url:
            QMessageBox.warning(self, "Validation Error", "Download URL is required.")
            return

        if not model_hash:
            QMessageBox.warning(self, "Validation Error", "Hash is required.")
            return

        if not input_value:
            QMessageBox.warning(
                self, "Validation Error", "input_value in regexes is required."
            )
            return

        # Validate input_value regex
        try:
            input_value_pattern = re.compile(input_value)
        except re.error as e:
            QMessageBox.warning(
                self, "Validation Error", f"Invalid regex in input_value: {e}"
            )
            return

        # Validate regex captures filenames
        filenames = {filename, second_filename, overridden_filename} - {
            ""
        }  # Remove empty strings
        invalid_filenames = [
            fname for fname in filenames if not input_value_pattern.search(fname)
        ]

        if invalid_filenames:
            QMessageBox.warning(
                self,
                "Validation Error",
                (
                    f"The input_value regex does not match the following filenames:\n\n"
                    + "\n".join(invalid_filenames)
                    + "\n\nPlease adjust the regex or filenames to proceed."
                ),
            )
            return

        # Prepare regexes
        regexes = [{}]
        if class_type:
            regexes[0]["class_type"] = class_type
        if input_name:
            regexes[0]["input_name"] = input_name
        if input_value:
            regexes[0]["input_value"] = input_value

        # Prepare the model entry
        model_entry = {
            "regexes": regexes,
            "url": url,
            "homepage": homepage,
            "hash": model_hash,
        }

        if overridden_filename:
            model_entry["filename"] = overridden_filename
        else:
            default_filename = self.get_default_filename(url)
            if filename and filename != default_filename:
                model_entry["filename"] = filename

        if types:
            model_entry["types"] = types

        if gated:
            model_entry["gated"] = True

        # Find existing key(s) with the same hash
        existing_keys_with_hash = [
            key
            for key, entry in self.models_catalog.items()
            if entry.get("hash") == model_hash
        ]

        # Ensure no filename matches more than one existing regex in the catalog
        filename_matches = {}
        for fname in filenames:
            for entry in self.models_catalog.values():
                regexes_list = entry.get("regexes", [])
                for regex_entry in regexes_list:
                    existing_input_value = regex_entry.get("input_value", "")
                    if (
                        existing_input_value
                        and regex_entry.get("class_name", "") == class_type
                        and regex_entry.get("input_name", "") == input_name
                    ):
                        try:
                            existing_pattern = re.compile(existing_input_value)
                        except re.error:
                            continue
                        if existing_pattern.search(fname):
                            filename_matches[fname] = regex_entry
                            break

        if filename_matches and not existing_keys_with_hash:
            QMessageBox.warning(
                self,
                "Validation Error",
                f"The following filenames match more than one regex in the catalog:\n\n"
                f"{json.dumps(filename_matches, indent=2)}\n\n"
                "Please adjust the input regexes or filenames to ensure unique matches.",
            )
            return

        # Get a unique model key
        model_key = self.get_model_key()
        if not model_key:
            return

        # Update models_catalog
        self.models_catalog[model_key] = model_entry

        # Save to models_catalog.json
        with open(self.models_catalog_file, "w", encoding="utf-8") as f:
            json.dump(self.models_catalog, f, indent=2, ensure_ascii=False)

        QMessageBox.information(self, "Success", "Model entry saved successfully.")

        # Clear the form
        self.clear_full_form()

    def get_model_key(self):
        model_hash = self.hash_edit.text().strip()
        existing_keys = set(self.models_catalog.keys())

        # Find existing key(s) with the same hash
        existing_keys_with_hash = [
            key
            for key, entry in self.models_catalog.items()
            if entry.get("hash") == model_hash
        ]

        if existing_keys_with_hash:
            existing_key = existing_keys_with_hash[0]
            # Pre-fill the UniqueKeyDialog with existing_key
            dialog = UniqueKeyDialog(
                existing_keys, self, prefill_key=existing_key, existing_key=existing_key
            )
        else:
            dialog = UniqueKeyDialog(existing_keys, self)

        if dialog.exec() == QDialog.Accepted:
            result_key = dialog.get_result()
            # If the hash exists and the user changes the key, we need to delete the old record
            if existing_keys_with_hash and result_key != existing_key:
                # Delete old record
                del self.models_catalog[existing_key]
                # Log this action
                self.append_log(
                    f"Deleted existing model with key '{existing_key}' due to hash conflict.",
                    True,
                )
            return result_key
        return None

    def get_default_filename(self, url):
        try:
            headers = {}
            if "huggingface.co" in url and self.huggingface_token:
                headers["Authorization"] = f"Bearer {self.huggingface_token}"
            response = requests.head(url, headers=headers, allow_redirects=True)
            if "Content-Disposition" in response.headers:
                cd = response.headers["Content-Disposition"]
                if "filename*=" in cd:
                    match = re.search(
                        r"filename\*\s*=\s*[^']*'[^']*'([^;]+)", cd, re.IGNORECASE
                    )
                    if match:
                        return match.group(1)
                match = re.search(r'filename\s*=\s*"([^"]+)"', cd, re.IGNORECASE)
                if match:
                    return match.group(1)
                match = re.search(r"filename\s*=\s*([^;]+)", cd, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            return os.path.basename(response.url)
        except Exception as e:
            print(f"Error getting default filename: {e}")
            return ""

    def process_url(self):
        self.clear_form()

        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Validation Error", "URL is required.")
            return

        self.process_button.setEnabled(False)
        self.url_edit.setEnabled(False)

        self.log_widget.clear()

        self.thread = QThread()
        self.worker = URLWorker(
            url,
            huggingface_token=self.huggingface_token,
            civitai_token=self.civitai_token,
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.url_corrected.connect(self.handle_url_corrected)
        self.worker.homepage_extracted.connect(self.handle_homepage_extracted)
        self.worker.default_filename_found.connect(self.handle_default_filename_found)
        self.worker.second_filename_found.connect(self.handle_second_filename_found)
        self.worker.hash_fetched.connect(self.handle_hash_fetched)
        self.worker.gated_checked.connect(self.handle_gated_checked)
        self.worker.status_update.connect(self.append_log)
        self.worker.files_found.connect(self.handle_files_found)
        self.worker.model_type_found.connect(
            self.handle_model_type_found
        )  # Connect the signal

        self.thread.finished.connect(lambda: self.process_button.setEnabled(True))
        self.thread.finished.connect(lambda: self.url_edit.setEnabled(True))

        self.thread.start()

    def handle_url_corrected(self, corrected_url):
        self.download_url_edit.setText(corrected_url)

    def handle_homepage_extracted(self, homepage):
        self.homepage_edit.setText(homepage)

    def handle_default_filename_found(self, filename):
        self.filename = filename
        self.filename_edit.setText(filename)
        self.update_input_value_regex()

    def handle_second_filename_found(self, second_filename):
        self.second_filename = second_filename
        self.second_filename_label.setText(second_filename)
        self.update_input_value_regex()

    def update_input_value_regex(self):
        # Combine filenames into a set to remove duplicates
        filenames = set()
        if self.filename:
            filenames.add(self.filename)
        if self.second_filename:
            filenames.add(self.second_filename)
        overridden_filename = self.overridden_filename_edit.text().strip()
        if overridden_filename:
            filenames.add(overridden_filename)

        if not filenames:
            return  # No filenames to generate regex

        # Escape filenames for regex
        escaped_filenames = [re.escape(fn) for fn in filenames]

        # Create a regex that matches any path ending with the filenames or just the filename itself
        if len(escaped_filenames) == 1:
            # If only one unique filename, create a simpler regex
            regex_pattern = rf"(?i)(?:[^\/\\]*[\/\\]?)?{escaped_filenames[0]}$"
        else:
            # Multiple filenames, include all in the regex
            regex_pattern = (
                rf"(?i)(?:[^\/\\]*[\/\\]?)?(?:{'|'.join(escaped_filenames)})$"
            )

        # Set the regex in the input_value field
        self.input_value_edit.setText(regex_pattern)

    def handle_hash_fetched(self, model_hash):
        self.hash_edit.setText(model_hash)

    def handle_gated_checked(self, gated):
        self.gated_checkbox.setChecked(gated)

    def handle_files_found(self, files, model_type):
        self.current_model_type = model_type  # Store for later use

        valid_files = []
        ignored_files = []

        self.append_log(f"Found {len(files)} files.", False)

        for file in files:
            # Check if the file has non-empty hashes
            hashes = file.get("hashes", {})
            if not hashes:
                ignored_files.append(file)
                continue

            valid_files.append(file)

        # Log ignored files
        if ignored_files:
            for ignored_file in ignored_files:
                self.append_log(
                    f"Ignored file '{ignored_file.get('name', 'Unnamed file')}' due to missing hashes.",
                    True,
                )

        if not valid_files:
            self.append_log("No valid files found with non-empty hashes.", True)
            return

        # Handle valid files
        file_descriptions = []
        for file in valid_files:
            name = file.get("name", "Unnamed file")
            file_type = file.get("type", "Unknown type")
            metadata = file.get("metadata", {})
            size = metadata.get("size", "Unknown size")
            fp = metadata.get("fp", "Unknown FP")

            # Add additional metadata to differentiate files with the same name
            description = f"{name} (Type: {file_type}, Size: {size}, FP: {fp})"
            file_descriptions.append(description)

        # Let the user select a file if multiple are valid
        if len(valid_files) > 1:
            item, ok = QInputDialog.getItem(
                self,
                "Select File",
                "Multiple files found. Select a file to use:",
                file_descriptions,
                editable=False,
            )
            if not ok or not item:
                self.append_log("No file selected.", True)
                return

            # Find the selected file
            selected_index = file_descriptions.index(item)
            selected_file = valid_files[selected_index]
        else:
            # If only one valid file, use it
            selected_file = valid_files[0]

        filename = selected_file.get("name", "")
        hash_sha256 = selected_file.get("hashes", {}).get("SHA256", "")
        download_url = selected_file.get("downloadUrl", "")
        file_type = selected_file.get("type", "Unknown")

        if download_url:
            self.download_url_edit.setText(download_url)
            self.append_log(f"Set download URL: {download_url}", False)
        else:
            self.append_log("No download URL found.", True)
            return

        if filename:
            self.second_filename = filename
            self.second_filename_label.setText(filename)
            self.update_input_value_regex()
            self.append_log(f"Set CivitAI filename: {filename}", False)
        else:
            self.append_log("No filename found.", True)

        if hash_sha256:
            self.hash_edit.setText(hash_sha256)
            self.append_log(f"Set hash: {hash_sha256}", False)
        else:
            self.append_log("No hash found.", True)

        # Set type based on model_type and file_type
        types_value = determine_types(self.current_model_type, file_type)
        if types_value and types_value in self.type_checkboxes:
            self.type_checkboxes[types_value].setChecked(True)
            self.append_log(
                f"Set type '{types_value}' from model_type '{self.current_model_type}' "
                f"and file_type '{file_type}'",
                False,
            )
        else:
            self.append_log(
                f"Unknown combination of model_type '{self.current_model_type}' "
                f"and file_type '{file_type}', please report this",
                True,
            )

        gated = check_gated(download_url, status_update_func=self.append_log)
        self.gated_checkbox.setChecked(gated)
        if gated:
            self.append_log("Model is gated (requires token)", True)
        else:
            self.append_log("Model is not gated", False)

    def handle_model_type_found(self, types_value):
        if types_value in self.type_checkboxes:
            checkbox = self.type_checkboxes[types_value]
            checkbox.setChecked(True)
            self.append_log(f"Set type '{types_value}' from CivitAI model type", False)
        else:
            self.append_log(
                f"Unknown model type '{types_value}', please report this", True
            )

    def append_log(self, message, is_warning):
        if is_warning:
            self.log_widget.appendHtml(
                f'<span style="color: red; font-weight: bold;">{message}</span>'
            )
        else:
            self.log_widget.appendPlainText(message)

    def clear_full_form(self):
        self.url_edit.clear()
        self.clear_form()

    def clear_form(self):
        self.homepage_edit.clear()
        self.download_url_edit.clear()
        self.filename_edit.clear()
        self.second_filename_label.setText("")
        self.filename = ""
        self.second_filename = ""
        self.overridden_filename_edit.clear()
        self.hash_edit.clear()
        self.gated_checkbox.setChecked(False)
        self.class_type_edit.clear()
        self.input_name_edit.clear()
        self.input_value_edit.clear()
        for checkbox in self.type_checkboxes.values():
            checkbox.setChecked(False)
        self.log_widget.clear()

    def closeEvent(self, event):
        # Clean up the worker thread if it's still running
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        event.accept()


class UniqueKeyDialog(QDialog):
    def __init__(self, existing_keys, parent=None, prefill_key=None, existing_key=None):
        super().__init__(parent)
        self.setWindowTitle("Model Name Input")
        self.setMinimumWidth(550)

        self.existing_keys = existing_keys
        self.result_key = None
        self.existing_key = existing_key

        layout = QVBoxLayout(self)

        # Input label and field
        self.label = QLabel("Enter a unique model name:")
        layout.addWidget(self.label)

        self.input_field = QLineEdit(self)
        if prefill_key:
            self.input_field.setText(prefill_key)
        layout.addWidget(self.input_field)

        # Warning label
        self.warning_label = QLabel("", self)
        self.warning_label.setStyleSheet("color: red;")
        layout.addWidget(self.warning_label)

        # Info label
        self.info_label = QLabel("", self)
        self.info_label.setStyleSheet("color: blue;")
        layout.addWidget(self.info_label)

        # Button layout
        button_layout = QHBoxLayout()
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self.accept)

        button_layout.addWidget(self.confirm_button)

        layout.addLayout(button_layout)

        # Connect signals
        self.input_field.textChanged.connect(self.validate_input)

        # Initial validation
        self.validate_input()

    def validate_input(self):
        key = self.input_field.text().strip()
        if not key:
            self.warning_label.setText("Model name cannot be empty.")
            self.confirm_button.setEnabled(False)
            self.info_label.clear()
        elif key in self.existing_keys:
            if key == self.existing_key:
                # The key is the same as existing key, allow overwriting
                self.warning_label.setText(
                    f"A model with this name '{key}' already exists with the same hash."
                )
                self.info_label.setText("Proceeding will overwrite the existing entry.")
                self.confirm_button.setEnabled(True)
            else:
                # Key exists with different hash
                self.warning_label.setText(
                    f"A model with the name '{key}' already exists with a different hash."
                )
                self.info_label.setText(
                    "Proceeding will delete the old entry and save under the new name."
                )
                self.confirm_button.setEnabled(True)
        else:
            self.warning_label.clear()
            if self.existing_key:
                self.info_label.setText(
                    f"A model with the same hash exists under the name '{self.existing_key}'.\n"
                    f"Proceeding will delete the old entry and save under the new name."
                )
            else:
                self.info_label.clear()
            self.confirm_button.setEnabled(True)

    def accept(self):
        key = self.input_field.text().strip()
        if not key:
            QMessageBox.warning(self, "Validation Error", "Model name cannot be empty.")
            return
        self.result_key = key
        super().accept()

    def get_result(self):
        return self.result_key


if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = ModelCatalogEditor()
    editor.show()
    sys.exit(app.exec())
