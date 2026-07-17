import sys
import logging

# Configure basic logging before transformers is imported
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

# Ensure stderr is properly configured
if sys.stderr is None:
    sys.stderr = open('transformers.log', 'w') 