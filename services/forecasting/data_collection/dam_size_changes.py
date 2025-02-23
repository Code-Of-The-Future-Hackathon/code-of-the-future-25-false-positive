import os

import pandas as pd
import torch
import rasterio
import numpy as np
import cv2
import geojson
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, mapping
from pyproj import CRS, Transformer
from segment_anything import sam_model_registry, SamPredictor


# 1. Convert Geo-Coordinates to Pixel Coordinates
def geo_to_pixel(geo_tiff, lon, lat):
    with rasterio.open(geo_tiff) as src:
        transform = src.transform
        col, row = ~transform * (lon, lat)  # Apply inverse affine transformation
        return int(round(col)), int(round(row))  # Ensure integer indices


# 2. Convert Pixel Coordinates to Geo-Coordinates
def pixel_to_geo(geo_tiff, pixel_contours):
    with rasterio.open(geo_tiff) as src:
        transform = src.transform
        geo_contours = [[transform * (pt[0][0], pt[0][1]) for pt in contour] for contour in pixel_contours]
        return geo_contours


# 3. Get Pixel Resolution in Meters (Fixed)
def get_pixel_resolution(geo_tiff):
    with rasterio.open(geo_tiff) as src:
        transform = src.transform
        crs = src.crs  # Get the coordinate reference system
        pixel_width, pixel_height = abs(transform.a), abs(transform.e)  # Pixel size in map units

        # If CRS is in degrees, convert to meters
        if crs.is_geographic:
            center_lat = (src.bounds.top + src.bounds.bottom) / 2  # Approximate center latitude
            transformer = Transformer.from_crs(crs, "EPSG:3857", always_xy=True)  # Convert to Web Mercator
            x1, _ = transformer.transform(src.bounds.left, center_lat)
            x2, _ = transformer.transform(src.bounds.left + pixel_width, center_lat)
            pixel_width = abs(x2 - x1)  # Convert pixel width to meters

            _, y1 = transformer.transform(center_lat, src.bounds.bottom)
            _, y2 = transformer.transform(center_lat, src.bounds.bottom + pixel_height)
            pixel_height = abs(y2 - y1)  # Convert pixel height to meters

        return pixel_width, pixel_height  # Return in meters


# 4. Load the Facebook SAM Model
def load_sam_model(checkpoint_path="sam_vit_h.pth"):
    model_type = "vit_l"
    device = "cuda" if torch.cuda.is_available() else "cpu"

    sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
    sam.to(device)
    predictor = SamPredictor(sam)
    return predictor, device


# 5. Generate Mask Using SAM
def generate_mask(image_path, predictor, point):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    predictor.set_image(image)

    input_point = np.array([point])
    input_label = np.array([1])

    masks, scores, logits = predictor.predict(point_coords=input_point, point_labels=input_label,
                                              multimask_output=False)

    return masks[0]  # The first mask is the most confident one


# 6. Extract High-Quality Contours from Mask
def extract_high_quality_contours(mask):
    contours, _ = cv2.findContours(mask.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(contours) > 0:
        contours = max(contours, key=cv2.contourArea)  # Select the biggest contour
    else:
        contours = []

    return [contours]  # Return as list for processing


# 7. Save Contours as GeoJSON for Mapping
def save_contours_as_geojson(geo_contours, output_path="mask_contour.geojson"):
    polygons = [Polygon(contour) for contour in geo_contours if len(contour) > 2]  # Create polygon from contour

    feature_collection = geojson.FeatureCollection(
        [geojson.Feature(geometry=mapping(polygon)) for polygon in polygons]
    )

    with open(output_path, "w") as f:
        geojson.dump(feature_collection, f, indent=2)

    print(f"GeoJSON saved to {output_path}")


# 8. Calculate Masked Area Using Pixel Count
def calculate_mask_area(mask, geo_tiff):
    pixel_width, pixel_height = get_pixel_resolution(geo_tiff)  # Get meters per pixel
    area_per_pixel_m2 = pixel_width * pixel_height  # Area of a single pixel in m²
    masked_pixels = np.sum(mask > 0)  # Count number of pixels inside the mask
    masked_area_km2 = (masked_pixels * area_per_pixel_m2) / 1e6  # Convert m² to km²
    return masked_area_km2


# 9. Visualize Mask with Contours on the Image
def visualize_mask_with_contours(image_path, mask, pixel_contours):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Overlay mask
    overlay = image.copy()
    overlay[mask > 0] = (255, 0, 0)  # Color mask in red

    # Draw high-quality contours
    cv2.drawContours(overlay, pixel_contours, -1, (0, 255, 0), thickness=2)  # Green contour lines

    # Show result
    plt.figure(figsize=(10, 6))
    plt.imshow(overlay)
    plt.title("SAM Mask with High-Quality Contours")
    plt.axis("off")
    plt.show()


def process_tifs(base_directory, output_directory, checkpoint_path, geo_point):
    os.makedirs(output_directory, exist_ok=True)
    predictor, device = load_sam_model(checkpoint_path)
    results = []

    for year in range(2020, 2026):
        for month in range(1, 13):
            tif_path = os.path.join(base_directory, str(year), f"{month}", "geo_img.tif")
            if os.path.exists(tif_path):
                geojson_path = os.path.join(output_directory, f"{year}_{month}.geojson")
                pixel_coords = geo_to_pixel(tif_path, *geo_point)
                mask = generate_mask(tif_path, predictor, pixel_coords)
                pixel_contours = extract_high_quality_contours(mask)
                geo_contours = pixel_to_geo(tif_path, pixel_contours)
                save_contours_as_geojson(geo_contours, geojson_path)
                masked_area_km2 = calculate_mask_area(mask, tif_path)
                results.append({"Year": year, "Month": month, "Masked Area (km²)": masked_area_km2})
                print(f"Processed {year}-{month}: Area = {masked_area_km2:.4f} km²")

    results_df = pd.DataFrame(results)
    results_csv_path = os.path.join(output_directory, "masked_areas.csv")
    results_df.to_csv(results_csv_path, index=False)
    print(f"Saved area calculations to {results_csv_path}")


# 10. Main Workflow
if __name__ == "__main__":
    process_tifs("/home/kala/Documents/Hackathon-Burgas-2025/code-of-the-future-25-false-positive/services/tile-server/tiles/feb0577f-335b-4516-a148-21d27f40ad5e", "output", "sam_vit_l_0b3195.pth", (26.763296, 43.053022))

    #geo_tiff_path = "geo_img.tif"  # Path to the georeferenced image
    #sam_checkpoint = "sam_vit_l_0b3195.pth"  # Path to the pre-trained SAM checkpoint
    #geo_point = (26.763296, 43.053022)  # Example: San Francisco coordinates (longitude, latitude)
#
    ## Convert geo-coordinates to pixel coordinates
    #pixel_coords = geo_to_pixel(geo_tiff_path, *geo_point)
    #print(f"Pixel coordinates: {pixel_coords}")
#
    ## Load SAM model
    #predictor, device = load_sam_model(sam_checkpoint)
#
    ## Generate mask
    #mask = generate_mask(geo_tiff_path, predictor, pixel_coords)
#
    ## Extract high-quality mask contours
    #pixel_contours = extract_high_quality_contours(mask)
#
    ## Convert mask edges from pixels to geo-coordinates
    #geo_contours = pixel_to_geo(geo_tiff_path, pixel_contours)
    #print(f"Geo-referenced high-quality contours extracted.")
#
    ## Save contours as GeoJSON for GIS or interactive mapping
    #save_contours_as_geojson(geo_contours, "mask_contour.geojson")
#
    ## Calculate Masked Area in Square Kilometers
    #masked_area_km2 = calculate_mask_area(mask, geo_tiff_path)
    #print(f"Masked Area: {masked_area_km2:.4f} km²")
#
    ## Visualize results
    #visualize_mask_with_contours(geo_tiff_path, mask, pixel_contours)
