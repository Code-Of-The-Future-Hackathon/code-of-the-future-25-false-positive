import calendar
import os
import dotenv

from PIL import Image
from datetime import datetime, timedelta
from sentinelhub import SHConfig, SentinelHubRequest, DataCollection, MimeType, CRS, BBox, bbox_to_dimensions, \
    MosaickingOrder, to_utm_bbox

from geo_util import create_georeferenced_tiff, generate_tiles_with_gdal2tiles

# Sentinel Hub Credentials (Replace with your actual credentials)
CLIENT_ID = dotenv.get_key(".env", "CLIENT_ID")
CLIENT_SECRET = dotenv.get_key(".env", "CLIENT_SECRET")

config = SHConfig()
config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET


def month_interval(year: int, month: int) -> tuple[str, str]:
    """
    Returns the start and end date of the given month as a string interval (YYYY-MM-DD to YYYY-MM-DD).

    :param year: The year (e.g., 2024)
    :param month: The month (1-12)
    :return: A tuple containing the first and last day of the month in "YYYY-MM-DD" format.
    """
    if not (1 <= month <= 12):
        raise ValueError("Month must be between 1 and 12")

    # Get the first day and last day of the month
    first_day = f"{year:04d}-{month:02d}-01"
    last_day = f"{year:04d}-{month:02d}-{calendar.monthrange(year, month)[1]}"

    return first_day, last_day


def max_resolution_for_bbox(bbox: BBox) -> float:
    """
    Given a bounding box, calculate the maximum resolution (meters per pixel)
    so that the output dimensions do not exceed 2500 pixels.

    :param bbox: The bounding box.
    :return: Maximum resolution in meters per pixel (rounded to 1 decimal).
    """
    utm_bbox = to_utm_bbox(bbox)
    east1, north1 = utm_bbox.lower_left
    east2, north2 = utm_bbox.upper_right

    # Calculate width and height in meters
    width_m = abs(east2 - east1)
    height_m = abs(north2 - north1)

    # To ensure neither width nor height exceed 2500 pixels,
    # the resolution must be at least (dimension in meters) / 2500.
    max_res = max(width_m, height_m) / 2500.0

    # Return resolution rounded to one decimal place.
    return round(max_res, 1)


# Function to request Sentinel-2 imagery
def collect_dam_satellite_imagery(year, month, dam_id, coord_bbox):
    """
    Collects satellite imagery for a specified dam and time period.

    :param year: The year of the imagery (e.g., 2023).
    :param month: The month of the imagery (1-12).
    :param dam_id: The identifier for the dam.
    :param coord_bbox: The bounding box coordinates (min_lon, min_lat, max_lon, max_lat).
    :return: None
    """

    bbox = BBox(bbox=coord_bbox, crs=CRS.WGS84)
    bbox_size = bbox_to_dimensions(bbox, resolution=max_resolution_for_bbox(bbox))

    start_date, end_date = month_interval(year, month)

    evalscript = """
    // Basic True Color rendering
    function setup() {
        return {
            input: [{ bands: ["B04", "B03", "B02"] }],
            output: { bands: 3 }
        };
    }
    function evaluatePixel(sample) {
        return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
    }
    """

    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=(start_date, end_date),
                mosaicking_order=MosaickingOrder.LEAST_CC
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=bbox,
        size=bbox_size,
        config=config  # Set up your Sentinel Hub configuration
    )

    path = f"tiles/{dam_id}/{year}/{month}"

    os.makedirs(path, exist_ok=True)

    image = request.get_data()[0]

    im = Image.fromarray(image)

    im.save(f"{path}/img.png")

    create_georeferenced_tiff(f"{path}/img.png", f"{path}/geo_img.tif", coord_bbox)

    print(f"Satellite image saved to {path}")

def create_dam_satellite_tiles(year, month, dam_id, coord_bbox):
    """
    Generates XYZ tiles from a georeferenced image file and saves them in a specified directory.
    :param year: The year of the image.
    :param month: The month of the image.
    :param dam_id: The ID of the dam.
    :param coord_bbox: The bounding box of the image in (min_lon, min_lat, max_lon, max_lat) format.
    """
    path = f"tiles/{dam_id}/{year}/{month}"

    os.makedirs(path, exist_ok=True)

    generate_tiles_with_gdal2tiles(f"{path}/geo_img.tif", path, zoom_range="0-16")

    print(f"Tiles saved to {path}")

    os.remove(f"{path}/img.png")

def automate_imagery_creation(start_year, start_month, end_year, end_month, dam_id, coord_bbox):
    """
    Automates imagery creation from start date to end date by looping through each month.
    """
    current_date = datetime(start_year, start_month, 1)
    end_date = datetime(end_year, end_month, 1)

    while current_date <= end_date:
        year, month = current_date.year, current_date.month
        print(f"\nProcessing: {year}-{month:02d}")

        try:
            collect_dam_satellite_imagery(year, month, dam_id, coord_bbox)
            create_dam_satellite_tiles(year, month, dam_id, coord_bbox)
        except Exception as e:
            print(f"Error processing {year}-{month:02d}: {e}")

        # Move to the next month
        next_month = current_date.month + 1
        next_year = current_date.year + (1 if next_month > 12 else 0)
        current_date = datetime(next_year, 1 if next_month > 12 else next_month, 1)


if __name__ == "__main__":
    start_year = 2020
    start_month = 1
    end_year = 2025
    end_month = 2
    bbox = (26.665371, 43.013685, 26.820627, 43.105996)
    dam_id = "feb0577f-335b-4516-a148-21d27f40ad5e"

    # Run the automation for the specified date range
    automate_imagery_creation(start_year, start_month, end_year, end_month, dam_id, bbox)