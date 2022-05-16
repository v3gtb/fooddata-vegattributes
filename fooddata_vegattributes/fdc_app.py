fdc_app_details_base_url = (
  "https://fdc.nal.usda.gov/fdc-app.html#/food-details/"
)

def get_fdc_app_details_url(fdc_id: int):
  return f"{fdc_app_details_base_url}{fdc_id}"
