import calendar
import os

import dotenv
from PIL import Image
from sentinelhub import SHConfig, SentinelHubRequest, DataCollection, MimeType, CRS, BBox, bbox_to_dimensions, \
    MosaickingOrder, to_utm_bbox

from geo_util import create_georeferenced_tiff, generate_tiles_with_gdal2tiles, generate_tiles_with_gdal

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
def load_dam_tiles(year, month, dam_id, coord_bbox):
    """
    Fetches a Sentinel-2 image for a given bounding box and time range, and saves it as a PNG file.
    :param start_date: YYYY-MM-DD
    :param end_date:  YYYY-MM-DD
    :param output_file: Name of the output PNG file
    :param coord_bbox: Bounding box in (min_lon, min_lat, max_lon, max_lat) order
    :return:
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

    geo_tiff = f"{path}/geo_img.tif"

    create_georeferenced_tiff(f"{path}/img.png", geo_tiff, coord_bbox)

    generate_tiles_with_gdal2tiles(geo_tiff, path, zoom_range="0-16")
    #generate_tiles_with_gdal(geo_tiff, path, zoom_range=(0, 16))

    print(f"Tiles saved to {path}")

    os.remove(f"{path}/img.png")


if __name__ == "__main__":
    year = 2023
    month = 1
    bbox = (26.665371, 43.013685, 26.820627, 43.105996)

    # Example usage
    load_dam_tiles(year, month, "dam1", bbox)
