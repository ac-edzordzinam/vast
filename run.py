import logging
from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()


if __name__ == "__main__":
    # Log the start of the application
    logger.info("Starting Flask application.")
    
    # Set the port dynamically, defaulting to 5000 if PORT is not set in environment
    port = int(os.environ.get("PORT", 5000))
    
    # Run the app with host set to 0.0.0.0 to allow access from external source
    app.run(host="0.0.0.0", port=port, debug=True)
