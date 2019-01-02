# Server Architecture

RESTful API Setup
-------------------------------------------------------------------------------------

###### index.py contains the Flask Server and routes

###### Pipfile handles environment and requirements with PIP Virtual Env Lockfile

###### Bootstrap.sh runs the Flask Server


Routes
-------------------------------------------------------------------------------------

###### imagesearch [POST]
  * Requires JPG image as input to request
  * Runs a reverse image search with the input image
  * Parses the URLs of the top page of results from the image search
  * Returns a JSON object with a list of URLs

###### ela
  * Requires JPG image as input to request
  * Runs ELA algorithm on the input image
  * Generates an ELA image displaying the brightness of pixels based on compression levels
  * Returns the resulting ELA image with pixel brightness

###### elascore
  * Requires JPG image as input to request
  * Runs ELA algorithm on the input image
  * Calculates a predicted percentage of manipulated pixels based on a predefined pixel brightness threshold
  * Returns a grade corresponding the the predicted pixel manipulation level

###### metadata
  * Requires JPG image as input to request
  * Generates a JSON object containing all metadata for the input image
  * Returns a JSON object of the input image's metadata
