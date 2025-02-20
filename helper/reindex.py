import yaml
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def reindex_annotations(annotation_folder, data_yaml_file, standard_label_map):
    """
    Reindex annotations in text files based on a standard label map and update the YAML file.
    Also handles invalid or unknown labels with logging warnings.

    Args:
        annotation_folder (str): Path to the folder containing annotation text files.
        data_yaml_file (str): Path to the YAML file containing current label names.
        standard_label_map (dict): A dictionary mapping label names to new indices.

    Returns:
        None
    """
    # Load the existing YAML file
    with open(data_yaml_file, "r") as f:
        data = yaml.safe_load(f)

    # Extract current label mapping from YAML file
    current_label_map = {name: idx for idx, name in enumerate(data.get("names", []))}
    reverse_label_map = {idx: name for name, idx in current_label_map.items()}  # Reverse mapping
    logging.info("Current Label Mapping: %s", current_label_map)

    # Iterate through annotation files
    for filename in os.listdir(annotation_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(annotation_folder, filename)

            # Read annotation lines
            with open(file_path, "r") as file:
                lines = file.readlines()

            new_lines = []
            for line in lines:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue  # Skip invalid lines

                old_index = int(parts[0])
                old_label_name = reverse_label_map.get(old_index, None)

                # Check if the label exists in the reverse mapping
                if old_label_name is None:
                    logging.warning("File: %s - Unknown label index %d", filename, old_index)
                    continue  # Skip unknown label

                new_index = standard_label_map.get(old_label_name, old_index)

                if old_index != new_index:
                    logging.info(
                        "File: %s - Class '%s' changed from index %d to %d",
                        filename, old_label_name, old_index, new_index
                    )

                new_line = f"{new_index} {' '.join(parts[1:])}"
                new_lines.append(new_line)

            # Write the updated annotations back to the file
            with open(file_path, "w") as file:
                file.write("\n".join(new_lines))
            logging.info("Updated annotations in file: %s", filename)

    # Update the YAML file with the new class names from the standard_label_map
    updated_yaml_data = data.copy()  # Preserve existing YAML data

    # Update only the 'names' and 'nc' fields
    updated_yaml_data["names"] = {v: k for k, v in standard_label_map.items()}  # Reverse the standard_label_map for names
    updated_yaml_data["nc"] = len(standard_label_map)

    # Log the changes to the YAML data before saving
    logging.info("Updating YAML file with new 'names' and 'nc' values.")
    logging.info("New 'names' values: %s", updated_yaml_data["names"])
    logging.info("New 'nc' value: %d", updated_yaml_data["nc"])

    # Save the updated YAML data
    with open(data_yaml_file, "w") as f:
        yaml.dump(updated_yaml_data, f, default_flow_style=False)

    logging.info("YAML file updated with new label mappings.")
    logging.info("Annotation reindexing completed.")

# Define standard label map
standard_label_map = {
    "angryface": 0, "auto": 1, "bicycle": 2, "bus": 3, "car": 4, "happyface": 5, "motorcycle": 6,
    "neutralface": 7, "numberplate": 8, "person": 9, "pole": 10, "road": 11, "road_cross": 12,
    "sadface": 13, "sidewalk": 14, "truck": 15, "van": 16
}

# Define file paths
annotation_folders = [
    "D:/Updated_video/NEW_UPDATE_FINAL_ONE/labels"
]
data_yaml_files = [
    "D:/Updated_video/NEW_UPDATE_FINAL_ONE/dataset.yaml"
]

# Process each dataset folder
for i in range(len(annotation_folders)):
    reindex_annotations(annotation_folders[i], data_yaml_files[i], standard_label_map)
