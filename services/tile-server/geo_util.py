import os
import subprocess
from osgeo import gdal, osr

def create_georeferenced_tiff(image_path, output_tiff, bbox):
    """
    Create a georeferenced GeoTIFF from a PNG image using an EPSG:4326 bounding box.

    Parameters:
        image_path (str): Path to the input PNG image (assumed to be in EPSG:4326).
        output_tiff (str): Path for the output GeoTIFF.
        bbox (tuple): Bounding box in (min_lon, min_lat, max_lon, max_lat) order.
    """
    # Open the source PNG
    ds = gdal.Open(image_path)
    if ds is None:
        raise RuntimeError(f"Unable to open image: {image_path}")

    width = ds.RasterXSize
    height = ds.RasterYSize

    # Unpack bbox: (min_lon, min_lat, max_lon, max_lat)
    min_lon, min_lat, max_lon, max_lat = bbox

    # For a north-up image, the upper-left pixel is at (min_lon, max_lat)
    pixel_width = (max_lon - min_lon) / width
    pixel_height = (max_lat - min_lat) / height

    # Geotransform: (top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution)
    # Note: n-s pixel resolution must be negative.
    geotransform = (min_lon, pixel_width, 0, max_lat, 0, -pixel_height)

    # Create the output GeoTIFF (copy the input image)
    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.CreateCopy(output_tiff, ds, 0)
    if out_ds is None:
        raise RuntimeError("Failed to create output GeoTIFF.")

    out_ds.SetGeoTransform(geotransform)

    # Set spatial reference to EPSG:4326 (WGS84)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    out_ds.SetProjection(srs.ExportToWkt())

    out_ds.FlushCache()
    out_ds = None
    ds = None

    print(f"Created georeferenced TIFF (EPSG:4326): {output_tiff}")

def generate_tiles_with_gdal2tiles(geotiff_path, output_folder, zoom_range="0-15"):
    """
    Generate Leaflet-compatible XYZ tiles from a GeoTIFF (in EPSG:4326) using the gdal2tiles.py tool.

    Parameters:
        geotiff_path (str): Path to the input GeoTIFF (EPSG:4326).
        output_folder (str): Directory where the generated tiles will be stored.
        zoom_range (str): Zoom level range to generate (e.g., "0-15").
    """
    if not os.path.exists(geotiff_path):
        raise RuntimeError("Input GeoTIFF for tiling does not exist.")

    os.makedirs(output_folder, exist_ok=True)

    cmd = [
        "gdal2tiles.py",
        "-z", zoom_range,  # Zoom level range
        "--xyz",
        geotiff_path,
        output_folder
    ]

    print("Running gdal2tiles command:")
    print(" ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"gdal2tiles.py failed: {e}")

    print(f"Tiles generated in: {output_folder}")


if __name__ == "__main__":
    # Input parameters
    image_path = "sentinel_image.png"  # Path to your PNG image (original coordinates are in EPSG:4326)
    # Bounding box in EPSG:4326: (min_lon, min_lat, max_lon, max_lat)
    bbox4326 = (26.665371, 43.013685, 26.820627, 43.105996)
    output_tiff = "temp_merc.tif"
    tiles_folder = "tiles"
    zoom_range = "0-16"

    try:
        create_georeferenced_tiff(image_path, output_tiff, bbox4326)

        # Generate Leaflet-compatible tiles using gdal2tiles
        generate_tiles_with_gdal2tiles(output_tiff, tiles_folder, zoom_range)
    except Exception as e:
        print("Error:", e)
    #finally:
    #    # Clean up temporary file if needed
    #    if os.path.exists(output_tiff):
    #        os.remove(output_tiff)
    #        print(f"Removed temporary file: {output_tiff}")
#