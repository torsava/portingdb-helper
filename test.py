#!/usr/bin/python3

import logging

# Setup logging
# handler = logging.FileHandler('helper.log')
# handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
# handler.setFormatter(formatter)

logging.basicConfig(filename='helper.log', level=logging.INFO,
        format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Hugo")
