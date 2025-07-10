import os

from app.core.config import settings as s
from app.services.storage import StorageService
from lib import gen_collection_point, gen_plot_centroids

VILLAGE_MAP_NAME = "raw-map.zip"  # Digitized Raw Map
DATA_SHEET_EXCEL_NAME = "data-sheet.xlsx"
FILLED_DATA_SHEET_EXCEL_NAME = "filled-data-sheet.xlsx"
COLLECTION_POINTS_ZIP_NAME = "collection-points.zip"
GRID_ZIP_NAME = "grid.zip"
PLOT_CENTROID_EXCEL_NAME = "plot-centroids.xlsx"
PLOT_CENTROID_ZIP_NAME = "plot-centroids.zip"

S3_BASE_URL = f"{s.MINIO_ENDPOINT_URL}/{s.S3_BUCKET_NAME}"


def remote_model_directory(village_id: int) -> str:
    return f"village-{village_id}"


def tmp_model_directory(village_id: int) -> str:
    model_dir = f"/tmp/iSPAT/village-{village_id}"
    os.makedirs(model_dir, exist_ok=True)
    return model_dir


class ProximityModelService:

    @staticmethod
    def create_village_project(
        storage: StorageService, village_id: int, raw_map_file: bytes
    ) -> bool:
        output_dir = tmp_model_directory(village_id)

        village_map_path = f"{output_dir}/{VILLAGE_MAP_NAME}"
        with open(village_map_path, "wb") as f:
            f.write(raw_map_file)

        # 2. generate required files
        gen_collection_point.collection_point_data_sheet(
            village_map_path=village_map_path,
            output_directory=output_dir,
            data_sheet_name=DATA_SHEET_EXCEL_NAME,
            grid_zip_name=GRID_ZIP_NAME,
            collection_points_zip_name=COLLECTION_POINTS_ZIP_NAME,
        )
        gen_plot_centroids.generate_plot_centroids_shapefile(
            village_map_path=village_map_path,
            output_directory=output_dir,
            excel_name=PLOT_CENTROID_EXCEL_NAME,
            zip_name=PLOT_CENTROID_ZIP_NAME,
        )

        # 3. upload generated files to storage
        files_to_upload = [
            (
                f"{output_dir}/{VILLAGE_MAP_NAME}",
                f"{remote_model_directory(village_id)}/{VILLAGE_MAP_NAME}",
            ),
            (
                f"{output_dir}/{DATA_SHEET_EXCEL_NAME}",
                f"{remote_model_directory(village_id)}/{DATA_SHEET_EXCEL_NAME}",
            ),
            (
                f"{output_dir}/{GRID_ZIP_NAME}",
                f"{remote_model_directory(village_id)}/{GRID_ZIP_NAME}",
            ),
            (
                f"{output_dir}/{COLLECTION_POINTS_ZIP_NAME}",
                f"{remote_model_directory(village_id)}/{COLLECTION_POINTS_ZIP_NAME}",
            ),
            (
                f"{output_dir}/{PLOT_CENTROID_ZIP_NAME}",
                f"{remote_model_directory(village_id)}/{PLOT_CENTROID_ZIP_NAME}",
            ),
            (
                f"{output_dir}/{PLOT_CENTROID_EXCEL_NAME}",
                f"{remote_model_directory(village_id)}/{PLOT_CENTROID_EXCEL_NAME}",
            ),
        ]

        for local_path, remote_path in files_to_upload:
            try:
                storage.upload_file_from_path(
                    local_path=local_path, destination_path=remote_path
                )
            except Exception as e:
                print(f"Failed to upload {local_path} to {remote_path}: {e}")

                # delete all files
                return False

        return True
